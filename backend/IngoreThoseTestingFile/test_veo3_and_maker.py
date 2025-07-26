#!/usr/bin/env python3
"""
Test script for VEO3 tool and Maker crew functionality.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from spark.models import VideoPrompt, CharacterProfile
from spark.tools.veo3_tool import VEO3Tool
from spark.crews.maker.src.maker.crew import VideoProductionCrew


def test_veo3_tool():
    """Test VEO3 tool functionality."""
    print("=" * 50)
    print("Testing VEO3 Tool")
    print("=" * 50)
    
    # Initialize VEO3 tool
    veo3 = VEO3Tool()
    
    # Create test video prompts
    test_prompts = [
        VideoPrompt(
            shot_id=1,
            veo3_prompt="A young wizard stands in a mystical forest, casting a spell with glowing hands, cinematic lighting, fantasy style",
            duration=5,
            character_reference_images=["wizard_ref1.jpg", "wizard_ref2.jpg"]
        ),
        VideoPrompt(
            shot_id=2,
            veo3_prompt="The wizard walks through ancient stone ruins, magical particles floating in the air, epic fantasy atmosphere",
            duration=8,
            character_reference_images=["wizard_ref1.jpg"]
        ),
        VideoPrompt(
            shot_id=3,
            veo3_prompt="Close-up of the wizard's face as he discovers a magical artifact, wonder and amazement in his eyes",
            duration=3,
            character_reference_images=["wizard_ref1.jpg", "wizard_ref3.jpg"]
        )
    ]
    
    # Test each VEO3 tool method
    print("\n1. Testing generate_video_clip():")
    for prompt in test_prompts:
        result = veo3.generate_video_clip(prompt)
        print(f"   Shot {prompt.shot_id}: {result}")
    
    print("\n2. Testing generate_with_professional_specs():")
    for prompt in test_prompts:
        result = veo3.generate_with_professional_specs(prompt, prompt.character_reference_images)
        print(f"   Shot {prompt.shot_id}: {result}")
    
    print("\n3. Testing check_generation_status():")
    for i, prompt in enumerate(test_prompts):
        job_id = f"job_{prompt.shot_id}"
        status = veo3.check_generation_status(job_id)
        print(f"   Job {job_id}: {status}")
    
    print("\n4. Testing validate_prompt_compatibility():")
    for prompt in test_prompts:
        is_valid = veo3.validate_prompt_compatibility(prompt)
        print(f"   Shot {prompt.shot_id}: {'Valid' if is_valid else 'Invalid'}")
    
    print("\n5. Testing optimize_generation_parameters():")
    for prompt in test_prompts:
        params = veo3.optimize_generation_parameters(prompt)
        print(f"   Shot {prompt.shot_id}: {params}")
    
    return test_prompts


def test_maker_crew():
    """Test Maker crew functionality."""
    print("\n" + "=" * 50)
    print("Testing Maker Crew")
    print("=" * 50)
    
    # Initialize Video Production Crew
    crew = VideoProductionCrew()
    
    # Create test video prompts
    test_prompts = [
        VideoPrompt(
            shot_id=1,
            veo3_prompt="A brave knight stands on a cliff overlooking a medieval castle, dramatic sunset lighting",
            duration=5,
            character_reference_images=["knight_ref1.jpg"]
        ),
        VideoPrompt(
            shot_id=2,
            veo3_prompt="The knight rides his horse across a battlefield, dust and debris flying, epic war scene",
            duration=10,
            character_reference_images=["knight_ref1.jpg", "horse_ref1.jpg"]
        ),
        VideoPrompt(
            shot_id=3,
            veo3_prompt="Close-up of the knight removing his helmet, revealing a determined face, heroic music",
            duration=3,
            character_reference_images=["knight_ref1.jpg"]
        )
    ]
    
    print("\n1. Testing generate_video_clips():")
    clip_urls = crew.generate_video_clips(test_prompts)
    for i, url in enumerate(clip_urls):
        print(f"   Clip {i+1}: {url}")
    
    print("\n2. Testing ensure_visual_consistency():")
    consistent_prompts = crew.ensure_visual_consistency(test_prompts)
    print(f"   Processed {len(consistent_prompts)} prompts for visual consistency")
    for prompt in consistent_prompts:
        print(f"   Shot {prompt.shot_id}: {len(prompt.character_reference_images)} reference images")
    
    print("\n3. Testing assemble_final_video():")
    final_video = crew.assemble_final_video(clip_urls)
    print(f"   Final video: {final_video}")
    
    return test_prompts, clip_urls, final_video


def test_integration():
    """Test integration between VEO3 tool and Maker crew."""
    print("\n" + "=" * 50)
    print("Testing VEO3 + Maker Integration")
    print("=" * 50)
    
    # Initialize both components
    veo3 = VEO3Tool()
    crew = VideoProductionCrew()
    
    # Create a complete workflow test
    print("\n1. Creating test scenario...")
    story_prompts = [
        VideoPrompt(
            shot_id=1,
            veo3_prompt="A futuristic cityscape at night with flying cars and neon lights, cyberpunk style",
            duration=8,
            character_reference_images=["cyber_city_ref.jpg"]
        ),
        VideoPrompt(
            shot_id=2,
            veo3_prompt="A cyberpunk hacker working on multiple holographic screens in a high-tech apartment",
            duration=12,
            character_reference_images=["hacker_ref.jpg", "apartment_ref.jpg"]
        ),
        VideoPrompt(
            shot_id=3,
            veo3_prompt="The hacker discovers a conspiracy on the screens, dramatic lighting with red alerts",
            duration=6,
            character_reference_images=["hacker_ref.jpg"]
        ),
        VideoPrompt(
            shot_id=4,
            veo3_prompt="Wide shot of the hacker running through neon-lit streets, rain falling, urgency",
            duration=10,
            character_reference_images=["hacker_ref.jpg", "street_ref.jpg"]
        )
    ]
    
    print(f"   Created {len(story_prompts)} video prompts")
    
    print("\n2. Optimizing generation parameters...")
    optimized_prompts = []
    for prompt in story_prompts:
        params = veo3.optimize_generation_parameters(prompt)
        print(f"   Shot {prompt.shot_id}: {params}")
        optimized_prompts.append(prompt)
    
    print("\n3. Generating video clips...")
    clip_urls = crew.generate_video_clips(optimized_prompts)
    print(f"   Generated {len(clip_urls)} clips")
    
    print("\n4. Assembling final video...")
    final_video = crew.assemble_final_video(clip_urls)
    print(f"   Final video created: {final_video}")
    
    return story_prompts, clip_urls, final_video


def run_all_tests():
    """Run all tests and provide summary."""
    print("VEO3 Tool and Maker Crew Test Suite")
    print("=" * 60)
    
    try:
        # Test VEO3 tool
        test_prompts = test_veo3_tool()
        
        # Test Maker crew
        crew_prompts, crew_clips, crew_final = test_maker_crew()
        
        # Test integration
        integration_prompts, integration_clips, integration_final = test_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✓ VEO3 Tool: All methods tested successfully")
        print(f"✓ Maker Crew: All methods tested successfully")
        print(f"✓ Integration: Complete workflow tested successfully")
        print(f"\nTotal prompts processed: {len(test_prompts) + len(crew_prompts) + len(integration_prompts)}")
        print(f"Total clips generated: {len(crew_clips) + len(integration_clips)}")
        print(f"Final videos created: 2")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)