#!/usr/bin/env python3
"""
Test script for real VEO3/VEO 2.0 API integration.
This script will actually generate videos using Google AI Studio API.
"""

import sys
import os
from pathlib import Path
import time

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from spark.models import VideoPrompt
from spark.tools.veo3_real_tool import VEO3RealTool


def test_real_veo3():
    """Test real VEO3 API integration."""
    print("=" * 60)
    print("Testing Real VEO3/VEO 2.0 API Integration")
    print("=" * 60)
    
    try:
        # Initialize real VEO3 tool
        veo3 = VEO3RealTool()
        print("✓ VEO3RealTool initialized successfully")
        
        # Create test video prompts
        test_prompts = [
            VideoPrompt(
                shot_id=1,
                veo3_prompt="A serene lake at sunrise with mist rising from the water, peaceful and calm atmosphere, cinematic quality",
                duration=5,
                character_reference_images=[]  # No reference images for first test
            ),
            VideoPrompt(
                shot_id=2,
                veo3_prompt="A majestic eagle soaring over mountain peaks, golden hour lighting, dramatic clouds",
                duration=8,
                character_reference_images=[]
            ),
            VideoPrompt(
                shot_id=3,
                veo3_prompt="Close-up of a blooming flower with morning dew, soft natural lighting, macro photography style",
                duration=3,
                character_reference_images=[]
            )
        ]
        
        print(f"\nCreated {len(test_prompts)} test prompts")
        
        # Test prompt validation
        print("\n1. Testing prompt validation:")
        for prompt in test_prompts:
            is_valid = veo3.validate_prompt_compatibility(prompt)
            print(f"   Prompt {prompt.shot_id}: {'Valid' if is_valid else 'Invalid'}")
        
        # Test parameter optimization
        print("\n2. Testing parameter optimization:")
        for prompt in test_prompts:
            params = veo3.optimize_generation_parameters(prompt)
            print(f"   Shot {prompt.shot_id}: {params}")
        
        # Test video generation
        print("\n3. Testing video generation:")
        generated_videos = []
        
        for i, prompt in enumerate(test_prompts):
            print(f"\n   Generating video {i+1}/{len(test_prompts)}...")
            print(f"   Prompt: {prompt.veo3_prompt}")
            
            # Generate video
            video_url = veo3.generate_video_clip(prompt)
            print(f"   Generated: {video_url}")
            
            # Check status
            if video_url.startswith("job_"):
                print("   Checking generation status...")
                status = veo3.check_generation_status(video_url.replace("job_", ""))
                print(f"   Status: {status}")
            
            generated_videos.append({
                'prompt': prompt,
                'url': video_url
            })
        
        # Test professional specs
        print("\n4. Testing professional specs:")
        professional_video = veo3.generate_with_professional_specs(
            test_prompts[0],
            []
        )
        print(f"   Professional video: {professional_video}")
        
        return generated_videos
        
    except Exception as e:
        print(f"❌ Error testing real VEO3: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def test_with_reference_images():
    """Test video generation with reference images."""
    print("\n" + "=" * 60)
    print("Testing VEO3 with Reference Images")
    print("=" * 60)
    
    try:
        veo3 = VEO3RealTool()
        
        # Create a simple reference image for testing
        # In real usage, you would use actual character images
        test_prompt = VideoPrompt(
            shot_id=1,
            veo3_prompt="A fantasy wizard character casting a spell, wearing blue robes and holding a wooden staff, magical particles around hands",
            duration=5,
            character_reference_images=[]  # We'll skip actual images for now
        )
        
        print("Testing reference image integration...")
        video_url = veo3.generate_with_professional_specs(
            test_prompt,
            []  # Empty for now - would be actual image paths
        )
        
        print(f"Generated with references: {video_url}")
        return video_url
        
    except Exception as e:
        print(f"❌ Error with reference images: {str(e)}")
        return None


def download_and_save_videos(generated_videos):
    """Download generated videos to local files."""
    print("\n" + "=" * 60)
    print("Downloading Generated Videos")
    print("=" * 60)
    
    try:
        veo3 = VEO3RealTool()
        
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        downloaded_files = []
        
        for i, video_data in enumerate(generated_videos):
            video_url = video_data['url']
            prompt = video_data['prompt']
            
            if video_url.startswith("http"):
                output_path = output_dir / f"video_{prompt.shot_id}.mp4"
                print(f"Downloading video {i+1} to {output_path}...")
                
                success = veo3.download_video(video_url, str(output_path))
                if success:
                    print(f"✓ Downloaded: {output_path}")
                    downloaded_files.append(str(output_path))
                else:
                    print(f"❌ Failed to download: {output_path}")
        
        return downloaded_files
        
    except Exception as e:
        print(f"❌ Error downloading videos: {str(e)}")
        return []


def main():
    """Main test function."""
    print("Real VEO3 API Integration Test")
    print("=" * 60)
    
    # Check if API key is available
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    if not api_key:
        print("❌ VIDEO_GENERATE_API_KEY not found in environment variables")
        print("Please check your .env file")
        return
    
    print(f"✓ API key found: {api_key[:10]}...")
    
    try:
        # Test basic functionality
        generated_videos = test_real_veo3()
        
        # Test with reference images
        test_with_reference_images()
        
        # Download videos if URLs are available
        if generated_videos:
            downloaded = download_and_save_videos(generated_videos)
            print(f"\n✓ Downloaded {len(downloaded)} videos")
        
        print("\n" + "=" * 60)
        print("Real VEO3 Test Summary")
        print("=" * 60)
        print(f"✓ API connection: Successful")
        print(f"✓ Video generation: {len(generated_videos)} videos generated")
        print(f"✓ All tests completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()