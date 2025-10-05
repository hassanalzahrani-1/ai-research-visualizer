"""
Scenario.com API Client for Image Generation
Enhanced with retry logic and comprehensive error handling
"""

import os
import time
import base64
import logging
from typing import Dict, List, Optional
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get logger (don't configure - let app.py handle it)
logger = logging.getLogger(__name__)


class ScenarioAPIError(Exception):
    """Custom exception for Scenario API errors"""
    pass

class ScenarioClient:
    """Client for interacting with Scenario.com API for image generation"""
    
    BASE_URL = 'https://api.cloud.scenario.com/v1'
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize Scenario API client
        
        Args:
            api_key: Scenario API key (defaults to SCENARIO_API_KEY env var)
            api_secret: Scenario API secret (defaults to SCENARIO_API_SECRET env var)
        """
        self.api_key = api_key or os.getenv('SCENARIO_API_KEY')
        self.api_secret = api_secret or os.getenv('SCENARIO_API_SECRET', '')
        
        if not self.api_key:
            raise ValueError("SCENARIO_API_KEY not found in environment variables")
        
        # Create authorization header
        auth_string = f"{self.api_key}:{self.api_secret}"
        auth_encoded = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_encoded}'
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, ScenarioAPIError)),
        reraise=True
    )
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make API request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            ScenarioAPIError: If API request fails after retries
        """
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            logger.info(f"Making {method} request to {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=30,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise ScenarioAPIError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise ScenarioAPIError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ScenarioAPIError(f"Unexpected error: {e}")
    
    def generate_image(
        self,
        prompt: str,
        model_id: str = 'flux.1-dev',
        width: int = 1024,
        height: int = 1024,
        samples: int = 1,
        steps: int = 28,
        guidance: float = 3.5,
        negative_prompt: Optional[str] = None,
        scheduler: str = 'EulerAncestralDiscreteScheduler'
    ) -> List[str]:
        """
        Generate images from text prompt
        
        Args:
            prompt: Text description of the image to generate
            model_id: Model to use (default: flux.1-dev)
            width: Image width in pixels
            height: Image height in pixels
            samples: Number of images to generate
            steps: Number of inference steps
            guidance: Guidance scale
            negative_prompt: Things to avoid in the image
            scheduler: Scheduler algorithm
            
        Returns:
            List of file paths to generated images
            
        Raises:
            ScenarioAPIError: If generation fails
        """
        payload = {
            'modelId': model_id,
            'prompt': prompt,
            'numInferenceSteps': steps,
            'numSamples': samples,
            'guidance': guidance,
            'width': width,
            'height': height,
            'scheduler': scheduler
        }
        
        if negative_prompt:
            payload['negativePrompt'] = negative_prompt
        
        logger.info(f"Generating image with prompt: '{prompt[:50]}...'")
        
        try:
            # Create generation job
            response = self._make_request('POST', 'generate/txt2img', json=payload)
            
            # Extract job ID
            job_id = response.get('job', {}).get('jobId') or response.get('jobId') or response.get('id')
            
            if not job_id:
                raise ScenarioAPIError(f"Job ID not found in response: {response}")
            
            logger.info(f"Job created successfully! Job ID: {job_id}")
            
            # Poll for completion and get image URLs
            return self._poll_and_get_urls(job_id)
            
        except ScenarioAPIError as e:
            logger.error(f"Image generation failed: {e}")
            raise
    
    def _poll_and_get_urls(self, job_id: str, max_attempts: int = 60) -> List[str]:
        """
        Poll job status until completion with adaptive polling intervals
        
        Args:
            job_id: Job ID to poll
            max_attempts: Maximum polling attempts (default: 60)
            
        Returns:
            List of image URLs
            
        Raises:
            ScenarioAPIError: If job fails or times out
        """
        logger.info(f"Polling job status for {job_id}...")
        
        for attempt in range(max_attempts):
            try:
                job_data = self._make_request('GET', f'jobs/{job_id}')
                job_info = job_data.get('job', {})
                status = job_info.get('status', '')
                
                logger.info(f"Job status: '{status}' (attempt {attempt + 1}/{max_attempts})")
                
                if status == 'success':
                    logger.info("Job completed successfully!")
                    return self._extract_image_urls(job_data)
                    
                elif status == 'failure':
                    error_msg = job_info.get('error', 'Unknown error')
                    raise ScenarioAPIError(f"Job failed: {error_msg}")
                    
                elif status in ['queued', 'in-progress']:
                    progress = job_info.get('progress', 0)
                    logger.info(f"Job {status} - Progress: {progress*100:.1f}%")
                
                # Adaptive polling: fast at first, then slower
                # First 10s: check every 2s (attempts 0-4)
                # Next 30s: check every 3s (attempts 5-14)
                # After 40s: check every 5s (attempts 15+)
                if attempt < 5:
                    time.sleep(2)
                elif attempt < 15:
                    time.sleep(3)
                else:
                    time.sleep(5)
                
            except ScenarioAPIError:
                raise
            except Exception as e:
                logger.error(f"Error polling job status: {e}")
                if attempt == max_attempts - 1:
                    raise ScenarioAPIError(f"Polling failed: {e}")
        
        raise ScenarioAPIError(f"Job timeout after 5 minutes")
    
    def _extract_image_urls(self, job_data: Dict) -> List[str]:
        """
        Extract image URLs from job data, checking multiple possible locations
        
        Args:
            job_data: Job data containing image information
            
        Returns:
            List of image URLs
        """
        urls = []
        job_info = job_data.get('job', {})
        
        # Try to get URLs directly from job response first (faster)
        # Check if URLs are already in the response
        direct_urls = job_info.get('images', []) or job_info.get('urls', [])
        if direct_urls:
            logger.info(f"Found {len(direct_urls)} URLs directly in job response")
            return [url if isinstance(url, str) else url.get('url', '') for url in direct_urls]
        
        # Fallback: Fetch asset URLs (slower but more reliable)
        metadata = job_info.get('metadata', {})
        asset_ids = metadata.get('assetIds', [])
        
        if not asset_ids:
            logger.warning("No asset IDs found in job response")
            return []
        
        logger.info(f"Fetching URLs for {len(asset_ids)} assets")
        
        # Fetch each asset to get its URL
        for asset_id in asset_ids:
            try:
                asset_data = self._make_request('GET', f'assets/{asset_id}')
                asset_info = asset_data.get('asset', {})
                url = asset_info.get('url', '')
                
                if url:
                    urls.append(url)
                    logger.info(f"Found image URL from asset {asset_id}")
                else:
                    logger.warning(f"No URL found for asset {asset_id}")
                    
            except Exception as e:
                logger.error(f"Error fetching asset {asset_id}: {e}")
        
        return urls
    

# Example usage
if __name__ == "__main__":
    try:
        client = ScenarioClient()
        prompt = "A futuristic AI research laboratory with holographic displays showing neural networks"
        
        images = client.generate_image(
            prompt=prompt,
            width=1024,
            height=1024,
            samples=1
        )
        
        print(f"\n✅ Successfully generated {len(images)} image(s)!")
        for filepath in images:
            print(f"📁 {filepath}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
