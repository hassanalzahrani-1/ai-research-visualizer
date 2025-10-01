#!/usr/bin/env python3
"""
Scenario.com Image-to-Image Generator
Generate images from a reference image and text prompt
"""

import os
import time
import requests
import base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

class ScenarioImg2ImgGenerator:
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
    
    def upload_image(self, image_path):
        """
        Upload an image to Scenario.com using base64 encoding and return the asset ID
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Asset ID of the uploaded image, or None if failed
        """
        print(f"📤 Uploading reference image: {image_path}")
        
        try:
            # Check file size (Scenario.com may have limits)
            file_size = Path(image_path).stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                print(f"❌ File too large: {file_size / (1024*1024):.1f}MB (max 10MB)")
                return None
            
            # Read and encode image as base64
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            
            # JSON payload for asset upload
            payload = {
                "image": encoded_string,
                "name": f"{Path(image_path).stem}_upload",
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": self.headers['Authorization']
            }
            
            # Make request to assets endpoint
            response = requests.post(
                f'{self.base_url}/assets',
                headers=headers,
                json=payload
            )
            
            print(f"🔍 Upload response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"🔍 Upload response data: {data}")
                
                # Try different possible field names for asset ID
                asset_id = (data.get('asset', {}).get('assetId') or 
                           data.get('asset', {}).get('id') or 
                           data.get('assetId') or 
                           data.get('id'))
                
                if asset_id:
                    print(f"✅ Image uploaded successfully! Asset ID: {asset_id}")
                    return asset_id
                else:
                    print(f"❌ No asset ID in upload response: {data}")
                    return None
            else:
                print(f"❌ Failed to upload image: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading image: {e}")
            return None
    
    def encode_image_base64(self, image_path):
        """
        Encode image as base64 data URL for direct use in API
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64 data URL, or None if failed
        """
        try:
            # Detect MIME type based on file extension
            file_ext = Path(image_path).suffix.lower()
            mime_type = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.webp': 'image/webp',
                '.bmp': 'image/bmp'
            }.get(file_ext, 'image/png')
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            # Create data URL
            data_url = f"data:{mime_type};base64,{encoded_image}"
            print(f"✅ Image encoded as base64 ({len(encoded_image)} chars)")
            return data_url
            
        except Exception as e:
            print(f"❌ Base64 encoding failed: {e}")
            return None
    
    def generate_image_img2img(self, prompt, image_path, **kwargs):
        """
        Generate an image from a text prompt and input image using Scenario.com API
        
        Args:
            prompt (str): Text description of the desired output
            image_path (str): Path to the input image file
            **kwargs: Additional parameters for image generation
        
        Returns:
            list: List of downloaded image file paths
        """
        # Check if image file exists
        if not Path(image_path).exists():
            print(f"❌ Image file not found: {image_path}")
            return None
        
        # Try to upload the image first to get asset ID
        asset_id = self.upload_image(image_path)
        
        if not asset_id:
            # If upload fails, use base64 encoding as fallback
            print("🔄 Upload failed, using base64 encoding...")
            asset_id = self.encode_image_base64(image_path)
            if not asset_id:
                return None
        
        # Default parameters for img2img
        payload = {
            'modelId': kwargs.get('model_id', 'flux.1-dev'),
            'prompt': prompt,
            'image': asset_id,  # Use 'image' parameter with asset ID or base64
            'numInferenceSteps': kwargs.get('steps', 28),
            'numSamples': kwargs.get('samples', 1),
            'guidance': kwargs.get('guidance', 3.5),
            'width': kwargs.get('width', 1024),
            'height': kwargs.get('height', 1024),
            'scheduler': kwargs.get('scheduler', 'EulerAncestralDiscreteScheduler'),
            'strength': kwargs.get('strength', 0.8)  # How much to change the input image (0.1 = subtle, 1.0 = major changes)
        }
        
        # Add negative prompt if provided
        if 'negative_prompt' in kwargs:
            payload['negativePrompt'] = kwargs['negative_prompt']
        
        print(f"🎨 Generating image-to-image with prompt: '{prompt}'")
        print(f"🖼️  Reference image: {Path(image_path).name}")
        print(f"📊 Parameters: {payload}")
        
        try:
            # Make the API request
            response = requests.post(
                f'{self.base_url}/generate/img2img',
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
                        filename = f"img2img_result_{timestamp}_{i+1}.png"
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
    """Main function to run the image-to-image generator"""
    try:
        # Initialize the generator
        generator = ScenarioImg2ImgGenerator()
        
        print("🖼️  Scenario.com Image-to-Image Generator")
        print("=" * 45)
        
        while True:
            # Get reference image path
            image_path = input("\n📁 Enter path to reference image (or 'quit' to exit): ").strip()
            
            if image_path.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not image_path:
                print("❌ Please enter a valid image path")
                continue
            
            # Check if file exists
            if not Path(image_path).exists():
                print(f"❌ File not found: {image_path}")
                continue
            
            # Get user prompt
            prompt = input("📝 Enter your transformation prompt: ").strip()
            
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
                
                strength = input("Transformation strength 0.1-1.0 (default: 0.8): ").strip()
                strength = float(strength) if strength else 0.8
                
                negative_prompt = input("Negative prompt (optional): ").strip()
                
            except ValueError:
                print("⚠️  Invalid input, using defaults")
                width, height, samples, strength = 1024, 1024, 1, 0.8
                negative_prompt = ""
            
            # Generate the image
            kwargs = {
                'width': width,
                'height': height,
                'samples': samples,
                'strength': strength
            }
            
            if negative_prompt:
                kwargs['negative_prompt'] = negative_prompt
            
            result = generator.generate_image_img2img(prompt, image_path, **kwargs)
            
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
