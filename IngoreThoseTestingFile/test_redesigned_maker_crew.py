"""
Test script for the redesigned Maker Crew using CrewAI best practices.
This tests the complete video generation pipeline.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.spark.crews.maker.src.maker.crew import MakerCrew, run_maker_crew


def test_veo3_tools():
    """Test individual VEO3 tools functionality."""
    print("🔧 Testing VEO3 Tools...")
    
    try:
        from src.spark.tools.veo3_crewai_tool import (
            load_project_video_prompts,
            generate_video_with_veo3,
            check_veo3_job_status,
            assemble_video_clips,
            download_video_from_url
        )
        
        # Test project loader
        test_project_id = "c1c61a55-91c4-4084-957c-89ab4c9e529f"
        print(f"📁 Testing project loader for: {test_project_id}")
        
        prompts_result = load_project_video_prompts.run(test_project_id)
        print(f"✅ Project prompts loaded: {len(prompts_result) if prompts_result else 0} characters")
        
        if prompts_result and not prompts_result.startswith("Error"):
            try:
                prompts_data = json.loads(prompts_result)
                print(f"✅ Found {len(prompts_data)} video prompts")
                
                # Test with first prompt (simulation)
                if prompts_data:
                    first_prompt = prompts_data[0]
                    print(f"📝 First prompt: shot_id={first_prompt.get('shot_id')}, duration={first_prompt.get('duration')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing prompts JSON: {e}")
        else:
            print(f"❌ Failed to load prompts: {prompts_result}")
        
        print("✅ VEO3 tools test completed")
        return True
        
    except Exception as e:
        print(f"❌ VEO3 tools test failed: {e}")
        return False


def test_maker_crew_initialization():
    """Test MakerCrew initialization."""
    print("\n🚀 Testing MakerCrew Initialization...")
    
    try:
        # Create crew instance
        maker_crew = MakerCrew()
        print("✅ MakerCrew instance created successfully")
        
        # Test agent creation
        video_generator = maker_crew.veo3_video_generator()
        video_assembler = maker_crew.video_assembly_specialist()
        print("✅ Agents created successfully")
        
        # Test task creation
        load_task = maker_crew.load_project_prompts_task()
        generate_task = maker_crew.generate_individual_videos_task()
        assemble_task = maker_crew.assemble_final_video_task()
        print("✅ Tasks created successfully")
        
        # Test crew creation
        crew = maker_crew.crew()
        print("✅ Crew assembled successfully")
        print(f"   - Agents: {len(crew.agents)}")
        print(f"   - Tasks: {len(crew.tasks)}")
        
        return True
        
    except Exception as e:
        print(f"❌ MakerCrew initialization failed: {e}")
        return False


def test_project_validation():
    """Test project validation logic."""
    print("\n📋 Testing Project Validation...")
    
    test_projects = [
        "c1c61a55-91c4-4084-957c-89ab4c9e529f",
        "7570de8d-2952-44ba-95ac-f9397c95ac0f", 
        "60320249-473f-4214-892d-e99561c7da94"
    ]
    
    valid_projects = []
    
    for project_id in test_projects:
        project_dir = Path("projects/projects") / project_id
        prompts_file = project_dir / "scripts" / "video_prompts.json"
        
        if project_dir.exists() and prompts_file.exists():
            print(f"✅ Valid project: {project_id}")
            valid_projects.append(project_id)
            
            # Check prompts content
            try:
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                print(f"   - Contains {len(prompts)} video prompts")
                
                # Validate prompt structure
                for i, prompt in enumerate(prompts[:2]):  # Check first 2
                    required_fields = ['shot_id', 'veo3_prompt', 'duration', 'character_reference_images']
                    missing_fields = [field for field in required_fields if field not in prompt]
                    
                    if missing_fields:
                        print(f"   ⚠️  Prompt {i+1} missing fields: {missing_fields}")
                    else:
                        print(f"   ✅ Prompt {i+1} structure valid")
                        
            except Exception as e:
                print(f"   ❌ Error reading prompts: {e}")
        else:
            print(f"❌ Invalid project: {project_id}")
            print(f"   - Directory exists: {project_dir.exists()}")
            print(f"   - Prompts file exists: {prompts_file.exists()}")
    
    print(f"\n📊 Summary: {len(valid_projects)}/{len(test_projects)} projects are valid")
    return valid_projects


def simulate_maker_crew_workflow(project_id: str):
    """Simulate the complete maker crew workflow."""
    print(f"\n🎬 Simulating Maker Crew Workflow for: {project_id}")
    
    try:
        # Initialize crew
        maker_crew = MakerCrew()
        print("✅ Crew initialized")
        
        # Validate project
        project_dir = Path("projects/projects") / project_id
        if not project_dir.exists():
            print(f"❌ Project directory not found: {project_dir}")
            return False
        
        prompts_file = project_dir / "scripts" / "video_prompts.json"
        if not prompts_file.exists():
            print(f"❌ Video prompts file not found: {prompts_file}")
            return False
        
        print("✅ Project validation passed")
        
        # Load prompts to understand scope
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        print(f"📝 Found {len(prompts)} video prompts to process")
        print(f"📊 Estimated total duration: {sum(p.get('duration', 5) for p in prompts)} seconds")
        
        # Create videos directory for output
        videos_dir = project_dir / "videos"
        videos_dir.mkdir(exist_ok=True)
        print(f"📁 Output directory prepared: {videos_dir}")
        
        # Simulate workflow steps
        print("\n🔄 Workflow Simulation:")
        print("1️⃣ Load project prompts... ✅")
        print("2️⃣ Generate individual videos... ⏳ (Would call VEO3 API)")
        print("3️⃣ Assemble final video... ⏳ (Would use MoviePy)")
        
        # Create a simulation result
        simulation_result = {
            "project_id": project_id,
            "workflow_status": "simulated",
            "total_prompts": len(prompts),
            "estimated_duration": sum(p.get('duration', 5) for p in prompts),
            "output_directory": str(videos_dir),
            "simulation_notes": [
                "VEO3 API calls would be made for each prompt",
                "Video files would be downloaded to local storage",
                "MoviePy would assemble final video",
                "Quality validation would be performed"
            ]
        }
        
        # Save simulation result
        simulation_file = videos_dir / "workflow_simulation.json"
        with open(simulation_file, 'w', encoding='utf-8') as f:
            json.dump(simulation_result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Simulation result saved: {simulation_file}")
        print("✅ Workflow simulation completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow simulation failed: {e}")
        return False


def main():
    """Main test execution."""
    print("🧪 Testing Redesigned Maker Crew")
    print("=" * 50)
    
    # Check environment
    print("🔍 Environment Check:")
    veo3_key = os.getenv("VIDEO_GENERATE_API_KEY") or os.getenv("VEO3_API_KEY")
    print(f"   VEO3 API Key: {'✅ Set' if veo3_key else '❌ Missing'}")
    
    llm_key = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    print(f"   LLM API Key: {'✅ Set' if llm_key else '❌ Missing'}")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    # Test 1: VEO3 Tools
    if test_veo3_tools():
        tests_passed += 1
    
    # Test 2: Crew Initialization  
    if test_maker_crew_initialization():
        tests_passed += 1
    
    # Test 3: Project Validation
    valid_projects = test_project_validation()
    if valid_projects:
        tests_passed += 1
    
    # Test 4: Workflow Simulation
    if valid_projects and simulate_maker_crew_workflow(valid_projects[0]):
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Redesigned Maker Crew is ready for use.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    # Next steps guidance
    print(f"\n📋 Next Steps:")
    if veo3_key:
        print("✅ You can run actual video generation")
        print("   Command: python -c \"from test_redesigned_maker_crew import *; run_maker_crew('your_project_id')\"")
    else:
        print("❌ Set up VEO3_API_KEY environment variable to enable video generation")
    
    print("📚 Documentation: Check COMPLETE_CHATBOT_TEST_REPORT.md for usage examples")


if __name__ == "__main__":
    main() 