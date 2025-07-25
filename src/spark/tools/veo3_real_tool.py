"""
Real VEO3/VEO 2.0 API integration for video generation using Google AI Studio.
"""

import os
import time
import json
import requests
from typing import Dict, List, Optional
import base64
from pathlib import Path
from ..models import VideoPrompt

class VEO3RealTool:
    """Real implementation of VEO3 video generation using Google VEO 2.0 API."""
    
    def __init__(self):
        self.api_key = os.getenv('VIDEO_GENERATE_API_KEY')
        if not self.api_key:
            raise ValueError("VIDEO_GENERATE_API_KEY not found in environment variables")
        
        # Google AI Studio API endpoint for VEO 2.0
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.upload_url = f"{self.base_url}/files"
        self.generate_url = f"{self.base_url}/models/veo-2.0-generate:generateContent"
        
    def _upload_image(self, image_path: str) -> Optional[str]:
        """Upload reference image to Google AI Studio and return file URI."""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Prepare upload request
            headers = {
                'X-Goog-Upload-Protocol': 'raw',
                'X-Goog-Upload-Content-Type': 'image/jpeg',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(
                self.upload_url,
                headers=headers,
                data=image_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('file', {}).get('uri')
            else:
                print(f"Failed to upload image {image_path}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error uploading image {image_path}: {str(e)}")
            return None
    
    def generate_video_clip(self, video_prompt: VideoPrompt) -> str:
        """Generate actual video clip using Google VEO 2.0 API."""
        try:
            # Prepare the generation request
            prompt = video_prompt.veo3_prompt
            
            # Upload reference images if provided
            reference_uris = []
            for ref_image in video_prompt.character_reference_images:
                uri = self._upload_image(ref_image)
                if uri:
                    reference_uris.append(uri)
            
            # Build the request payload
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }],
                "generationConfig": {
                    "durationSeconds": video_prompt.duration,
                    "aspectRatio": "16:9",
                    "fps": 24,
                    "resolution": "1080p"
                }
            }
            
            # Add reference images if available
            if reference_uris:
                for uri in reference_uris:
                    payload["contents"][0]["parts"].append({
                        "fileData": {
                            "mimeType": "image/jpeg",
                            "fileUri": uri
                        }
                    })
            
            # Make the API request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(
                self.generate_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract video URL from response
                if "candidates" in result and result["candidates"]:
                    video_part = result["candidates"][0]["content"]["parts"][0]
                    if "video" in video_part:
                        return video_part["video"]["url"]
                
                # Fallback: return job ID for polling
                job_id = result.get("name", "").split("/")[-1]
                return f"job_{job_id}"
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return f"error_{video_prompt.shot_id}"
    
    def generate_with_professional_specs(
        self, 
        video_prompt: VideoPrompt, 
        reference_images: List[str]
    ) -> str:
        """Generate video with professional specifications and reference images."""
        try:
            # Use the same implementation but with enhanced specs
            enhanced_prompt = f"{video_prompt.veo3_prompt}, cinematic quality, professional lighting, high resolution"
            
            # Create a new prompt with enhanced specs
            enhanced_video_prompt = VideoPrompt(
                shot_id=video_prompt.shot_id,
                veo3_prompt=enhanced_prompt,
                duration=video_prompt.duration,
                character_reference_images=reference_images
            )
            
            return self.generate_video_clip(enhanced_video_prompt)
            
        except Exception as e:
            print(f"Error generating professional video: {str(e)}")
            return f"error_prof_{video_prompt.shot_id}"
    
    def check_generation_status(self, job_id: str) -> Dict:
        """Check actual status of video generation job."""
        try:
            # Google AI Studio uses operation polling
            operation_url = f"{self.base_url}/operations/{job_id}"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(operation_url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("done"):
                    # Job completed
                    if "response" in result:
                        video_url = result["response"]["candidates"][0]["content"]["parts"][0]["video"]["url"]
                        return {
                            "status": "completed",
                            "url": video_url,
                            "progress": 100
                        }
                    else:
                        return {
                            "status": "failed",
                            "error": result.get("error", {}).get("message", "Unknown error")
                        }
                else:
                    # Still processing
                    return {
                        "status": "processing",
                        "progress": result.get("metadata", {}).get("progressPercent", 0)
                    }
            else:
                return {
                    "status": "error",
                    "error": f"API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def validate_prompt_compatibility(self, video_prompt: VideoPrompt) -> bool:
        """Validate if prompt is compatible with VEO 2.0."""
        try:
            # Basic validation checks
            if not video_prompt.veo3_prompt or len(video_prompt.veo3_prompt.strip()) < 10:
                return False
            
            if video_prompt.duration < 1 or video_prompt.duration > 60:
                return False
            
            # Check for prohibited content keywords
            prohibited_keywords = ["violence", "gore", "explicit", "nsfw"]
            prompt_lower = video_prompt.veo3_prompt.lower()
            
            for keyword in prohibited_keywords:
                if keyword in prompt_lower:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def optimize_generation_parameters(self, video_prompt: VideoPrompt) -> Dict:
        """Optimize generation parameters for VEO 2.0."""
        duration = video_prompt.duration
        
        # Optimize based on duration
        if duration <= 5:
            fps = 24
            resolution = "1080p"
        elif duration <= 15:
            fps = 24
            resolution = "1080p"
        else:
            fps = 24
            resolution = "720p"  # Lower resolution for longer videos
        
        return {
            "resolution": resolution,
            "fps": fps,
            "duration": duration,
            "aspectRatio": "16:9",
            "quality": "high"
        }
    
    def download_video(self, video_url: str, output_path: str) -> bool:
        """Download generated video to local file."""
        try:
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            return False
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return False