"""
Video Production Crew implementation.
Uses CrewAI framework to generate video clips and assemble final video.
Based on CrewAI official documentation and best practices.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

from crewai import Agent, Task, Crew, LLM
from crewai.project import CrewBase, agent, crew, task

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.spark.models import VideoPrompt, VideoClip
from src.spark.project_manager import project_manager
from .tools import VideoGenerationTool, VideoEditingTool

logger = logging.getLogger(__name__)


@CrewBase
class VideoProductionCrew:
    """Video production crew for generating video clips and assembling final video."""
    
    # Configure the crew
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        """Initialize the video production crew."""
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Set environment variables for LLM
        api_key = os.getenv("VIDEO_GENERATE_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No API key found. Please set VIDEO_GENERATE_API_KEY or OPENAI_API_KEY in .env file")
        
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
        
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = api_base
        os.environ["OPENAI_MODEL_NAME"] = model_name
        
        self.llm = LLM(
            model=model_name,
            api_key=api_key,
            base_url=api_base,
            temperature=0.3,  # Lower temperature for more consistent results
            max_tokens=1000
        )
        
        # Initialize tools
        self.video_generation_tool = VideoGenerationTool()
        self.video_editing_tool = VideoEditingTool()
        
        logger.info(f"Video production crew initialized with {model_name}")
    
    @agent
    def video_clip_generator_agent(self) -> Agent:
        """Video clip generator agent for VEO3 video generation."""
        return Agent(
            config=self.agents_config['video_clip_generator_agent'],
            llm=self.llm,
            tools=[self.video_generation_tool],
            verbose=True,
            max_iter=3,
            memory=True,
            allow_delegation=False
        )
    
    @agent
    def video_editor_agent(self) -> Agent:
        """Video editor agent for video assembly and post-processing."""
        return Agent(
            config=self.agents_config['video_editor_agent'],
            llm=self.llm,
            tools=[self.video_editing_tool],
            verbose=True,
            max_iter=3,
            memory=True,
            allow_delegation=False
        )
    
    @task
    def generate_video_clips_task(self) -> Task:
        """Task for generating video clips from prompts."""
        return Task(
            config=self.tasks_config['generate_video_clips_task'],
            agent=self.video_clip_generator_agent()
        )
    
    @task
    def assemble_final_video_task(self) -> Task:
        """Task for assembling final video from clips."""
        return Task(
            config=self.tasks_config['assemble_final_video_task'],
            agent=self.video_editor_agent(),
            context=[self.generate_video_clips_task()]
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the video production crew."""
        return Crew(
            agents=[self.video_clip_generator_agent(), self.video_editor_agent()],
            tasks=[self.generate_video_clips_task(), self.assemble_final_video_task()],
            verbose=True,
            memory=True
        )
    
    def process_project(self, project_id: str) -> Dict[str, Any]:
        """Process a complete project through the video production pipeline."""
        try:
            logger.info(f"Processing project {project_id} with CrewAI video production crew")
            
            # Load project data
            project_data = project_manager.load_project_for_crew(project_id, "maker")
            
            # Extract video prompts and metadata
            video_prompts, project_metadata = self._extract_video_data(project_data)
            
            if not video_prompts:
                raise Exception("No video prompts found in project data")
            
            # Try CrewAI first, fallback to direct processing if needed
            try:
                # Prepare inputs for the crew
                inputs = {
                    'project_id': project_id,
                    'video_title': project_metadata.get('title', 'Generated Video'),
                    'total_duration': project_metadata.get('duration', 60),
                    'video_prompts': json.dumps([prompt.model_dump() for prompt in video_prompts]),
                    'character_images': json.dumps(project_metadata.get('character_images', [])),
                    'video_clips': '[]'  # Will be populated by first task
                }
                
                # Execute the crew
                result = self.crew().kickoff(inputs=inputs)
                
                # Parse and structure the results
                final_result = self._parse_crew_results(result, project_id, project_metadata)
                
            except Exception as crew_error:
                logger.warning(f"CrewAI execution failed: {crew_error}, using direct processing")
                # Fallback to direct processing
                final_result = self._process_with_direct_calls(project_id, video_prompts, project_metadata)
            
            # Save results
            self._save_results(project_id, final_result)
            
            logger.info(f"Successfully processed project {project_id}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error processing project {project_id}: {e}")
            raise
    
    def _extract_video_data(self, project_data: Dict[str, Any]) -> tuple[List[VideoPrompt], Dict[str, Any]]:
        """Extract video prompts and metadata from project data."""
        try:
            # Load video prompts
            video_prompts = []
            if 'video_prompts' in project_data:
                prompts_data = project_data['video_prompts']
                for prompt_data in prompts_data:
                    video_prompts.append(VideoPrompt(**prompt_data))
            else:
                # Load from scripts directory
                project_dir = Path(project_data.get('project_dir', ''))
                prompts_file = project_dir / "scripts" / "video_prompts.json"
                if prompts_file.exists():
                    with open(prompts_file, 'r', encoding='utf-8') as f:
                        prompts_data = json.load(f)
                        for prompt_data in prompts_data:
                            video_prompts.append(VideoPrompt(**prompt_data))
            
            # Extract metadata
            metadata = {
                'title': project_data.get('title', 'Generated Video'),
                'duration': project_data.get('duration', 60),
                'character_images': []
            }
            
            # Get character images
            if 'character_profiles' in project_data:
                for char in project_data['character_profiles']:
                    if 'image_url' in char and char['image_url']:
                        metadata['character_images'].append(char['image_url'])
            
            return video_prompts, metadata
            
        except Exception as e:
            logger.error(f"Error extracting video data: {e}")
            raise
    
    def _process_with_direct_calls(self, project_id: str, video_prompts: List[VideoPrompt], metadata: Dict) -> Dict[str, Any]:
        """Process using direct tool calls as fallback."""
        logger.info("Using direct tool calls for video production")
        
        try:
            # Step 1: Generate video clips
            prompts_json = json.dumps([prompt.model_dump() for prompt in video_prompts])
            char_images_json = json.dumps(metadata.get('character_images', []))
            
            generation_result = self.video_generation_tool._run(
                video_prompts=prompts_json,
                character_images=char_images_json,
                project_id=project_id
            )
            
            generation_data = json.loads(generation_result)
            
            if generation_data.get('status') != 'completed':
                raise Exception(f"Video generation failed: {generation_data}")
            
            # Step 2: Assemble final video
            clips_json = json.dumps(generation_data['clips'])
            
            assembly_result = self.video_editing_tool._run(
                video_clips=clips_json,
                project_id=project_id,
                video_title=metadata.get('title', 'Generated Video'),
                total_duration=str(metadata.get('duration', 60))
            )
            
            assembly_data = json.loads(assembly_result)
            
            if assembly_data.get('status') != 'completed':
                raise Exception(f"Video assembly failed: {assembly_data}")
            
            # Combine results
            return {
                "project_id": project_id,
                "video_generation": generation_data,
                "video_assembly": assembly_data,
                "final_videos": assembly_data.get('outputs', {}),
                "thumbnail": assembly_data.get('thumbnail', ''),
                "metadata": {
                    "title": metadata.get('title'),
                    "total_clips": generation_data.get('total_prompts', 0),
                    "successful_clips": generation_data.get('successful_clips', 0),
                    "final_duration": assembly_data.get('metadata', {}).get('final_duration', 0)
                },
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Direct processing failed: {e}")
            return {
                "project_id": project_id,
                "status": "failed",
                "error": str(e)
            }
    
    def _parse_crew_results(self, crew_result, project_id: str, metadata: Dict) -> Dict[str, Any]:
        """Parse crew execution results into structured data."""
        try:
            # The crew result should contain the final task output
            final_output = str(crew_result)
            
            # Try to extract JSON from the result
            # This is a simplified parsing - in practice, you might want more sophisticated parsing
            try:
                if '{' in final_output and '}' in final_output:
                    # Extract JSON part
                    start = final_output.find('{')
                    end = final_output.rfind('}') + 1
                    json_part = final_output[start:end]
                    result_data = json.loads(json_part)
                else:
                    # Fallback: create basic result structure
                    result_data = {
                        "status": "completed",
                        "outputs": {},
                        "metadata": metadata
                    }
            except json.JSONDecodeError:
                result_data = {
                    "status": "completed",
                    "outputs": {},
                    "metadata": metadata
                }
            
            result_data["project_id"] = project_id
            return result_data
            
        except Exception as e:
            logger.error(f"Error parsing crew results: {e}")
            return {
                "project_id": project_id,
                "status": "failed",
                "error": str(e)
            }
    
    def _save_results(self, project_id: str, results: Dict[str, Any]):
        """Save video production results to the project."""
        try:
            project_dir = Path("projects/projects") / project_id
            videos_dir = project_dir / "videos"
            videos_dir.mkdir(exist_ok=True)
            
            # Save production summary
            summary_path = videos_dir / "production_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved video production results for project {project_id}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise