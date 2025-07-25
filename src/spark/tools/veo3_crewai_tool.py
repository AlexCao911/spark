"""
VEO3 custom tool for CrewAI integration.
Following CrewAI best practices for custom tool creation.
"""

import os
import json
import time
from typing import Dict, List, Optional
from pathlib import Path
from crewai_tools import tool
from ..models import VideoPrompt
from .veo3_real_tool import VEO3RealTool


@tool("VEO3 Video Generation Tool")
def generate_video_with_veo3(prompt_text: str, duration: int, reference_images: List[str], shot_id: int) -> str:
    """
    Generate a video clip using VEO3 API with the given prompt and reference images.
    
    Args:
        prompt_text (str): The VEO3-optimized prompt for video generation
        duration (int): Duration of the video in seconds  
        reference_images (List[str]): List of character reference image URLs
        shot_id (int): Unique identifier for this video shot
        
    Returns:
        str: Path to the generated video file or error message
    """
    try:
        # Create VideoPrompt object
        video_prompt = VideoPrompt(
            shot_id=shot_id,
            veo3_prompt=prompt_text,
            duration=duration,
            character_reference_images=reference_images
        )
        
        # Initialize VEO3 tool
        veo3_tool = VEO3RealTool()
        
        # Validate prompt compatibility
        if not veo3_tool.validate_prompt_compatibility(video_prompt):
            return f"Error: Prompt {shot_id} is not compatible with VEO3"
        
        # Generate video
        result = veo3_tool.generate_video_clip(video_prompt)
        
        if result.startswith("error_"):
            return f"Video generation failed for shot {shot_id}: {result}"
        elif result.startswith("job_"):
            # Handle job-based generation
            job_id = result[4:]  # Remove "job_" prefix
            return f"Video generation job started for shot {shot_id}: {job_id}"
        else:
            # Direct URL returned
            return f"Video generated successfully for shot {shot_id}: {result}"
            
    except Exception as e:
        return f"Error generating video for shot {shot_id}: {str(e)}"


@tool("Project Video Prompts Loader") 
def load_project_video_prompts(project_id: str) -> str:
    """
    Load video prompts from a project's scripts directory.
    
    Args:
        project_id (str): The unique project identifier
        
    Returns:
        str: JSON string containing the video prompts or error message
    """
    try:
        # Path to video prompts file
        prompts_path = Path("projects/projects") / project_id / "scripts" / "video_prompts.json"
        
        if not prompts_path.exists():
            return f"Error: Video prompts file not found for project {project_id}"
        
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
        
        return json.dumps(prompts_data, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"Error loading video prompts for project {project_id}: {str(e)}"


@tool("VEO3 Job Status Checker")
def check_veo3_job_status(job_id: str) -> str:
    """
    Check the status of a VEO3 video generation job.
    
    Args:
        job_id (str): The VEO3 job identifier
        
    Returns:
        str: Status information as JSON string
    """
    try:
        veo3_tool = VEO3RealTool()
        status = veo3_tool.check_generation_status(job_id)
        return json.dumps(status, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"Error checking job status {job_id}: {str(e)}"


@tool("Video Assembly Tool")
def assemble_video_clips(project_id: str, video_file_paths: List[str]) -> str:
    """
    Assemble multiple video clips into a final video.
    
    Args:
        project_id (str): The project identifier
        video_file_paths (List[str]): List of paths to video clips to assemble
        
    Returns:
        str: Path to the final assembled video or error message
    """
    try:
        # Import video processing libraries
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips
        except ImportError:
            return "Error: MoviePy not installed. Please install with: pip install moviepy"
        
        project_dir = Path("projects/projects") / project_id
        videos_dir = project_dir / "videos"
        videos_dir.mkdir(exist_ok=True)
        
        # Load video clips
        clips = []
        for file_path in video_file_paths:
            if os.path.exists(file_path):
                try:
                    clip = VideoFileClip(file_path)
                    clips.append(clip)
                except Exception as e:
                    return f"Error loading video clip {file_path}: {str(e)}"
            else:
                return f"Video file not found: {file_path}"
        
        if not clips:
            return "Error: No valid video clips to assemble"
        
        # Concatenate clips
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Output settings
        output_path = videos_dir / "final_video.mp4"
        
        # Render final video
        final_clip.write_videofile(
            str(output_path),
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Clean up clips
        for clip in clips:
            clip.close()
        final_clip.close()
        
        return str(output_path)
        
    except Exception as e:
        return f"Error assembling video: {str(e)}"


@tool("Video File Downloader")
def download_video_from_url(video_url: str, output_path: str) -> str:
    """
    Download a video from URL to local storage.
    
    Args:
        video_url (str): URL of the video to download
        output_path (str): Local path to save the video
        
    Returns:
        str: Success message with file path or error message
    """
    try:
        import requests
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Download video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return f"Video downloaded successfully to: {output_path}"
        
    except Exception as e:
        return f"Error downloading video from {video_url}: {str(e)}" 