"""
Maker Crew implementation using CrewAI framework.
Handles VEO3 video generation and professional video assembly.
Following CrewAI 0.30.11+ best practices.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from crewai import Agent, Task, Crew, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.spark.tools.veo3_crewai_tool import (
    generate_video_with_veo3,
    load_project_video_prompts,
    check_veo3_job_status,
    assemble_video_clips,
    download_video_from_url
)

logger = logging.getLogger(__name__)


@CrewBase
class MakerCrew:
    """Maker crew for VEO3 video generation and video assembly using CrewAI best practices."""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        """Initialize the maker crew with proper environment setup."""
        # Load environment variables
        load_dotenv()
        
        # Configure VEO3 API credentials
        veo3_api_key = os.getenv("VIDEO_GENERATE_API_KEY") or os.getenv("VEO3_API_KEY")
        veo3_endpoint = os.getenv("VIDEO_GENERATE_API_ENDPOINT") or os.getenv("VEO3_API_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta")
        
        if veo3_api_key:
            os.environ["VEO3_API_KEY"] = veo3_api_key
            os.environ["VIDEO_GENERATE_API_KEY"] = veo3_api_key
        else:
            logger.warning("VEO3 API key not found in environment variables")
        
        os.environ["VEO3_API_ENDPOINT"] = veo3_endpoint
        os.environ["VIDEO_GENERATE_API_ENDPOINT"] = veo3_endpoint
        
        # Configure LLM for crew coordination
        llm_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        llm_base_url = os.getenv("OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        llm_model = os.getenv("OPENAI_MODEL_NAME", "qwen-turbo-latest")
        
        if llm_api_key:
            os.environ["OPENAI_API_KEY"] = llm_api_key
        
        self.llm = LLM(
            model=llm_model,
            temperature=0.1,  # Low temperature for consistent video processing
            max_tokens=2000
        )
        
        logger.info(f"Maker crew initialized")
        logger.info(f"  VEO3 API Key: {'configured' if veo3_api_key else 'missing'}")
        logger.info(f"  VEO3 Endpoint: {veo3_endpoint}")
        logger.info(f"  LLM Model: {llm_model}")
    
    @agent
    def veo3_video_generator(self) -> Agent:
        """Specialized VEO3 video generation agent with custom tools."""
        return Agent(
            config=self.agents_config['veo3_video_generator'],
            llm=self.llm,
            tools=[
                load_project_video_prompts,
                generate_video_with_veo3,
                check_veo3_job_status,
                download_video_from_url
            ],
            verbose=True,
            max_iter=5,
            memory=True,
            allow_delegation=False
        )
    
    @agent
    def video_assembly_specialist(self) -> Agent:
        """Professional video assembly agent with post-production tools."""
        return Agent(
            config=self.agents_config['video_assembly_specialist'],
            llm=self.llm,
            tools=[
                assemble_video_clips
            ],
            verbose=True,
            max_iter=3,
            memory=True,
            allow_delegation=False
        )
    
    @task
    def load_project_prompts_task(self) -> Task:
        """Task for loading and validating project video prompts."""
        return Task(
            config=self.tasks_config['load_project_prompts_task'],
            agent=self.veo3_video_generator()
        )
    
    @task
    def generate_individual_videos_task(self) -> Task:
        """Task for generating individual video clips using VEO3."""
        return Task(
            config=self.tasks_config['generate_individual_videos_task'],
            agent=self.veo3_video_generator(),
            context=[self.load_project_prompts_task()]
        )
    
    @task
    def assemble_final_video_task(self) -> Task:
        """Task for assembling final video from individual clips."""
        return Task(
            config=self.tasks_config['assemble_final_video_task'],
            agent=self.video_assembly_specialist(),
            context=[self.generate_individual_videos_task()]
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the maker crew with sequential process."""
        return Crew(
            agents=[
                self.veo3_video_generator(),
                self.video_assembly_specialist()
            ],
            tasks=[
                self.load_project_prompts_task(),
                self.generate_individual_videos_task(),
                self.assemble_final_video_task()
            ],
            process='sequential',  # Tasks execute in order
            verbose=True,
            memory=True,
            planning=False,  # Disable planning for deterministic execution
            max_rpm=10  # Rate limiting for API calls
        )
    
    def process_project(self, project_id: str) -> Dict[str, Any]:
        """Process a complete project through the video generation pipeline."""
        try:
            logger.info(f"Starting video generation pipeline for project {project_id}")
            
            # Validate project exists
            project_dir = Path("projects/projects") / project_id
            if not project_dir.exists():
                raise ValueError(f"Project directory not found: {project_dir}")
            
            # Check for video prompts file
            prompts_file = project_dir / "scripts" / "video_prompts.json"
            if not prompts_file.exists():
                raise ValueError(f"Video prompts file not found: {prompts_file}")
            
            # Prepare inputs for the crew
            inputs = {
                'project_id': project_id
            }
            
            # Execute the crew workflow
            logger.info("Executing CrewAI workflow")
            result = self.crew().kickoff(inputs=inputs)
            
            # Process and structure the results
            video_results = self._process_crew_results(result, project_id)
            
            # Save comprehensive results
            final_results = {
                "project_id": project_id,
                "workflow_status": "completed",
                "video_generation_pipeline": video_results,
                                 "execution_timestamp": str(time.time()),
                "crew_execution_result": str(result)
            }
            
            self._save_comprehensive_results(project_id, final_results)
            
            logger.info(f"Successfully completed video generation pipeline for project {project_id}")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in video generation pipeline for project {project_id}: {e}")
            # Save error results
            error_results = {
                "project_id": project_id,
                "workflow_status": "failed",
                "error_message": str(e),
                                 "execution_timestamp": str(time.time())
            }
            self._save_comprehensive_results(project_id, error_results)
            raise
    
    def _process_crew_results(self, crew_result, project_id: str) -> Dict[str, Any]:
        """Process and structure crew execution results."""
        try:
            # Extract meaningful information from crew result
            result_data = {
                "crew_output": str(crew_result),
                "project_path": f"projects/projects/{project_id}",
                "videos_directory": f"projects/projects/{project_id}/videos",
                "final_video_path": f"projects/projects/{project_id}/videos/final_video.mp4"
            }
            
            # Check if final video was actually created
            final_video_path = Path(result_data["final_video_path"])
            if final_video_path.exists():
                result_data["final_video_size_mb"] = final_video_path.stat().st_size / (1024 * 1024)
                result_data["video_creation_status"] = "success"
            else:
                result_data["video_creation_status"] = "pending_or_failed"
            
            return result_data
            
        except Exception as e:
            logger.error(f"Error processing crew results: {e}")
            return {
                "crew_output": str(crew_result),
                "processing_error": str(e),
                "video_creation_status": "error"
            }
    
    def _save_comprehensive_results(self, project_id: str, results: Dict[str, Any]):
        """Save comprehensive results to the project directory."""
        try:
            project_dir = Path("projects/projects") / project_id
            videos_dir = project_dir / "videos"
            videos_dir.mkdir(exist_ok=True)
            
            # Save detailed results
            results_path = videos_dir / "maker_crew_results.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            # Save execution summary
            summary_path = videos_dir / "execution_summary.json"
            summary = {
                "project_id": project_id,
                "status": results.get("workflow_status", "unknown"),
                "timestamp": results.get("execution_timestamp"),
                "final_video_available": "final_video_path" in results.get("video_generation_pipeline", {}),
                "results_file": str(results_path)
            }
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved comprehensive results for project {project_id}")
            
        except Exception as e:
            logger.error(f"Error saving results for project {project_id}: {e}")


# Standalone execution function for testing
def run_maker_crew(project_id: str):
    """Run the maker crew for a specific project."""
    try:
        maker_crew = MakerCrew()
        results = maker_crew.process_project(project_id)
        
        print("Maker Crew Execution Results:")
        print("=" * 50)
        print(f"Project ID: {results['project_id']}")
        print(f"Status: {results['workflow_status']}")
        print(f"Timestamp: {results['execution_timestamp']}")
        
        if results['workflow_status'] == 'completed':
            pipeline_results = results.get('video_generation_pipeline', {})
            print(f"Final Video Status: {pipeline_results.get('video_creation_status', 'unknown')}")
            print(f"Videos Directory: {pipeline_results.get('videos_directory', 'N/A')}")
            if 'final_video_size_mb' in pipeline_results:
                print(f"Final Video Size: {pipeline_results['final_video_size_mb']:.2f} MB")
        
        return results
        
    except Exception as e:
        print(f"Error running maker crew: {e}")
        raise


if __name__ == "__main__":
    # Test with a sample project
    import sys
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
    else:
        # Use a default test project
        project_id = "c1c61a55-91c4-4084-957c-89ab4c9e529f"
    
    print(f"Testing Maker Crew with project: {project_id}")
    run_maker_crew(project_id)