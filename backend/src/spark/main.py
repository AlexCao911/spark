#!/usr/bin/env python
"""
Main entry point for the Spark AI Video Generation Pipeline.
"""

from crewai.flow import Flow, listen, start

from spark.models import VideoGenerationState
from spark.config import config
from spark.crews.script.src.script.crew import ScriptGenerationCrew
from spark.crews.maker.src.maker.crew import VideoProductionCrew


class VideoGenerationPipeline(Flow[VideoGenerationState]):
    """Main workflow orchestration for video generation pipeline."""
    
    def __init__(self):
        super().__init__()
        self.script_crew = ScriptGenerationCrew()
        self.video_crew = VideoProductionCrew()
        
        # Ensure configuration is valid
        config.ensure_temp_directory()
        missing_keys = config.get_missing_api_keys()
        if missing_keys:
            print(f"Warning: Missing API keys for: {', '.join(missing_keys)}")
    
    @start()
    def initialize_pipeline(self):
        """Initialize the video generation pipeline."""
        print("Initializing Spark AI Video Generation Pipeline")
        print(f"Configuration loaded: {len(config.get_missing_api_keys())} missing API keys")
        
        # Initialize state if needed
        if not self.state.user_idea.theme:
            print("Pipeline ready for user input")
        else:
            print(f"Resuming pipeline for theme: {self.state.user_idea.theme}")
    
    @listen(initialize_pipeline)
    def expand_story_narrative(self):
        """Expand approved content into detailed story."""
        if not self.state.approved_content.user_confirmed:
            print("Waiting for user confirmation before story expansion")
            return
        
        print("Expanding story narrative with Script Generation Crew")
        self.state.detailed_story = self.script_crew.expand_story_narrative(
            self.state.approved_content
        )
        print(f"Story expanded: {len(self.state.detailed_story.full_story_text)} characters")
    
    @listen(expand_story_narrative)
    def generate_video_prompts(self):
        """Generate VEO3-optimized video prompts."""
        if not self.state.detailed_story.full_story_text:
            print("No detailed story available for prompt generation")
            return
        
        print("Generating video prompts with Script Generation Crew")
        self.state.video_prompts = self.script_crew.break_into_shots_and_generate_prompts(
            self.state.detailed_story,
            self.state.approved_content.character_profiles
        )
        print(f"Generated {len(self.state.video_prompts)} video prompts")
    
    @listen(generate_video_prompts)
    def generate_video_clips(self):
        """Generate individual video clips."""
        if not self.state.video_prompts:
            print("No video prompts available for clip generation")
            return
        
        print("Generating video clips with Video Production Crew")
        self.state.video_clip_urls = self.video_crew.generate_video_clips(
            self.state.video_prompts
        )
        print(f"Generated {len(self.state.video_clip_urls)} video clips")
    
    @listen(generate_video_clips)
    def assemble_final_video(self):
        """Assemble final video from clips."""
        if not self.state.video_clip_urls:
            print("No video clips available for assembly")
            return
        
        print("Assembling final video with Video Production Crew")
        self.state.final_video_path = self.video_crew.assemble_final_video(
            self.state.video_clip_urls
        )
        print(f"Final video assembled: {self.state.final_video_path}")


def kickoff():
    """Start the video generation pipeline."""
    pipeline = VideoGenerationPipeline()
    pipeline.kickoff()


def plot():
    """Generate a plot diagram of the pipeline flow."""
    pipeline = VideoGenerationPipeline()
    pipeline.plot()


if __name__ == "__main__":
    kickoff()
