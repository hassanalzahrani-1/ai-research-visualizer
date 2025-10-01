#!/usr/bin/env python3
"""
Scenario.com Image Generator
A simple app that generates images using the Scenario.com API
"""

import os
import time
import requests
import base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

class ScenarioImageGenerator:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_key = os.getenv('SCENARIO_API_KEY')
        self.api_secret = os.getenv('SCENARIO_API_SECRET')
        self.output_dir = os.getenv('OUTPUT_DIR', 'generated_images')
        
        if not self.api_key:
            raise ValueError("API key not found. Please check your .env file.")
        
        if not self.api_secret:
            print("⚠️  Warning: API secret not provided. Using API key only.")
        
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # Set up API endpoints and headers
        self.base_url = 'https://api.cloud.scenario.com/v1'
        
        # Create authorization header
        auth_string = f"{self.api_key}:{self.api_secret or ''}"
        auth_encoded = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_encoded}'
        }
    
    def generate_image(self, prompt, **kwargs):
        """
        Generate an image from a text prompt using Scenario.com API
        
        Args:
            prompt (str): Text description of the image to generate
            **kwargs: Additional parameters for image generation
        
        Returns:
            dict: Response containing job information
        """
        # Default parameters
        payload = {
            'modelId': kwargs.get('model_id', 'flux.1-dev'),  # Using Flux Dev public model
            'prompt': prompt,
            'numInferenceSteps': kwargs.get('steps', 28),
            'numSamples': kwargs.get('samples', 1),
            'guidance': kwargs.get('guidance', 3.5),
            'width': kwargs.get('width', 1024),
            'height': kwargs.get('height', 1024),
            'scheduler': kwargs.get('scheduler', 'EulerAncestralDiscreteScheduler')
        }
        
        # Add negative prompt if provided
        if 'negative_prompt' in kwargs:
            payload['negativePrompt'] = kwargs['negative_prompt']
        
        print(f"🎨 Generating image with prompt: '{prompt}'")
        print(f"📊 Parameters: {payload}")
        
        try:
            # Make the API request
            response = requests.post(
                f'{self.base_url}/generate/txt2img',
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                               
                job_id = data.get('job', {}).get('jobId')
                
                if not job_id:
                    # Try alternative job ID field names
                    job_id = data.get('jobId') or data.get('id')
                    
                if not job_id:
                    print("❌ Error: Job ID not found in response")
                    print(f"Response data: {data}")
                    return None
                
                print(f"✅ Job created successfully! Job ID: {job_id}")
                return self.poll_job_status(job_id)
            
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Network error: {e}")
            return None
    
    def poll_job_status(self, job_id):
        """
        Poll the job status until completion
        
        Args:
            job_id (str): The job ID to poll
            
        Returns:
            dict: Final job data with image URLs
        """
        print(f"⏳ Polling job status for {job_id}...")
        status = ''
        max_attempts = 60  # Maximum 5 minutes (60 * 5 seconds)
        attempts = 0
        
        while status not in ['success', 'failure'] and attempts < max_attempts:
            attempts += 1
            try:
                # Fetch job status
                job_response = requests.get(
                    f'{self.base_url}/jobs/{job_id}',
                    headers=self.headers
                )
                
                if job_response.status_code != 200:
                    print(f"❌ Error fetching job status: {job_response.status_code}")
                    return None
                
                job_data = job_response.json()
                
                # The status is nested inside the 'job' object
                job_info = job_data.get('job', {})
                status = job_info.get('status', '')
                
                print(f"📊 Job status: '{status}'")
                
                if status == 'success':
                    print("🎉 Job completed successfully!")
                    return self.download_images(job_data)
                elif status == 'failure':
                    print("❌ Job failed!")
                    print(f"Error details: {job_data}")
                    return None
                elif status in ['queued', 'in-progress']:
                    progress = job_info.get('progress', 0)
                    print(f"⏳ Job {status} - Progress: {progress*100:.1f}%")
                
                # Wait before polling again
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Error polling job status: {e}")
                return None
        
        # Check if we timed out
        if attempts >= max_attempts:
            print(f"⏰ Timeout: Job did not complete after {max_attempts} attempts")
            return None
    
    def download_images(self, job_data):
        """
        Download generated images from the job data
        
        Args:
            job_data (dict): Job data containing image information
            
        Returns:
            list: List of downloaded image file paths
        """
        try:
            # Get asset IDs from job metadata (they're nested in job.metadata.assetIds)
            job_info = job_data.get('job', {})
            images = job_info.get('metadata', {}).get('assetIds', [])
            
            if not images:
                print("❌ No images found in job data")
                return []
            
            downloaded_files = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, asset_id in enumerate(images):
                try:
                    # Convert asset ID to download URL
                    asset_url = f"{self.base_url}/assets/{asset_id}"
                    
                    # Get asset information to find the download URL
                    asset_response = requests.get(asset_url, headers=self.headers)
                    
                    if asset_response.status_code != 200:
                        print(f"❌ Failed to get asset info for {asset_id}: {asset_response.status_code}")
                        continue
                    
                    asset_data = asset_response.json()
                    
                    # Try to find the actual image URL in the asset data
                    image_url = asset_data.get('url') or asset_data.get('downloadUrl') or asset_data.get('asset', {}).get('url')
                    
                    if not image_url:
                        print(f"❌ No download URL found in asset data for {asset_id}")
                        continue
                    
                    # Download the image
                    img_response = requests.get(image_url)
                    
                    if img_response.status_code == 200:
                        # Generate filename
                        filename = f"generated_image_{timestamp}_{i+1}.png"
                        filepath = Path(self.output_dir) / filename
                        
                        # Save the image
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        
                        downloaded_files.append(str(filepath))
                        print(f"💾 Downloaded: {filepath}")
                    
                    else:
                        print(f"❌ Failed to download image {i+1}: {img_response.status_code}")
                
                except Exception as e:
                    print(f"❌ Error downloading image {i+1}: {e}")
            
            return downloaded_files
            
        except Exception as e:
            print(f"❌ Error processing images: {e}")
            return []

def main():
    """Main function to run the image generator"""
    try:
        # Initialize the generator
        generator = ScenarioImageGenerator()
        
        print("🚀 Scenario.com Image Generator")
        print("=" * 40)
        
        while True:
            # Get user input
            prompt = input("\n📝 Enter your image prompt (or 'quit' to exit): ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not prompt:
                print("❌ Please enter a valid prompt")
                continue
            
            # Optional: Ask for additional parameters
            print("\n⚙️  Optional parameters (press Enter for defaults):")
            
            try:
                width = input("Width (default: 1024): ").strip()
                width = int(width) if width else 1024
                
                height = input("Height (default: 1024): ").strip()
                height = int(height) if height else 1024
                
                samples = input("Number of samples (default: 1): ").strip()
                samples = int(samples) if samples else 1
                
            except ValueError:
                print("⚠️  Invalid input, using defaults")
                width, height, samples = 1024, 1024, 1
            
            # Generate the image
            result = generator.generate_image(
                prompt,
                width=width,
                height=height,
                samples=samples
            )
            
            if result:
                print(f"✅ Successfully generated {len(result)} image(s)!")
                for filepath in result:
                    print(f"📁 Saved to: {filepath}")
            else:
                print("❌ Failed to generate image")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
