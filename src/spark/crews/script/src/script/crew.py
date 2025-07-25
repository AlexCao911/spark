"""
Script Generation Crew implementation.
Uses CrewAI framework to expand story narrative and generate professional VEO3 video prompts.
Based on CrewAI official documentation and best practices.
"""

import json
import logging
import math
import os
from pathlib import Path
from typing import List, Dict, Any

from crewai import Agent, Task, Crew, LLM
from crewai.project import CrewBase, agent, crew, task
import yaml

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.spark.models import ApprovedContent, DetailedStory, VideoPrompt, CharacterProfile, StoryOutline
from src.spark.project_manager import project_manager

logger = logging.getLogger(__name__)


@CrewBase
class ScriptGenerationCrew:
    """Script generation crew for expanding story narrative and generating VEO3 video prompts."""
    
    # Configure the LLM for all agents
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        """Initialize the script crew."""
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Set environment variables from .env file
        api_key = os.getenv("DETAILED_STORY_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No API key found. Please set DETAILED_STORY_API_KEY, DASHSCOPE_API_KEY, or OPENAI_API_KEY in .env file")
        
        api_base = os.getenv("OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        model_name = os.getenv("OPENAI_MODEL_NAME", "qwen-turbo-latest")
        
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = api_base
        os.environ["OPENAI_MODEL_NAME"] = model_name
        
        self.llm = LLM(
            model=model_name,
            api_key=api_key,
            base_url=api_base,
            temperature=0.7,
            max_tokens=2000
        )
        
        try:
            from openai import OpenAI
            self.backup_client = OpenAI(
                api_key=api_key,
                base_url=api_base
            )
            logger.info(f"Script generation crew initialized with {model_name} and backup client")
        except Exception as e:
            self.backup_client = None
            logger.warning(f"Backup client initialization failed: {e}")
    
    def _call_llm_with_fallback(self, messages: List[Dict[str, str]]) -> str:
        """Call LLM with fallback to backup client if CrewAI fails."""
        try:
            # Try CrewAI LLM first
            response = self.llm.call(messages)
            return response.content
        except Exception as e:
            logger.warning(f"CrewAI LLM call failed: {e}, using backup client")
            
            if self.backup_client:
                try:
                    # Use backup OpenAI client
                    completion = self.backup_client.chat.completions.create(
                        model="qwen-turbo-latest",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2000
                    )
                    return completion.choices[0].message.content
                except Exception as e2:
                    logger.error(f"Backup client also failed: {e2}")
            
            # Ultimate fallback
            raise Exception("Both CrewAI LLM and backup client failed")
    
    @agent
    def story_expansion_agent(self) -> Agent:
        """Story expansion agent for detailed narrative development."""
        return Agent(
            config=self.agents_config['story_expansion_agent'],
            llm=self.llm,
            verbose=True,
            max_iter=5,  # Reduced for faster execution
            memory=True,
            allow_delegation=False
        )
    
    @agent
    def shot_breakdown_agent(self) -> Agent:
        """Shot breakdown agent for VEO3 prompt generation."""
        return Agent(
            config=self.agents_config['shot_breakdown_agent'],
            llm=self.llm,
            verbose=True,
            max_iter=5,  # Reduced for faster execution
            memory=True,
            allow_delegation=False
        )
    
    @task
    def expand_story_task(self) -> Task:
        """Task for expanding story narrative."""
        return Task(
            config=self.tasks_config['expand_story_task'],
            agent=self.story_expansion_agent()
        )
    
    @task
    def generate_prompts_task(self) -> Task:
        """Task for generating VEO3 video prompts."""
        return Task(
            config=self.tasks_config['generate_prompts_task'],
            agent=self.shot_breakdown_agent(),
            context=[self.expand_story_task()]
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the script generation crew."""
        return Crew(
            agents=[self.story_expansion_agent(), self.shot_breakdown_agent()],
            tasks=[self.expand_story_task(), self.generate_prompts_task()],
            verbose=True,
            memory=True
        )
    
    def process_project(self, project_id: str) -> Dict[str, Any]:
        """Process a complete project through the script generation pipeline."""
        try:
            logger.info(f"Processing project {project_id} with CrewAI script crew")
            
            # Load project data
            project_data = project_manager.load_project_for_crew(project_id, "script")
            
            # Extract required data
            approved_content = self._extract_approved_content(project_data)
            
            # Try CrewAI first, fallback to direct processing if needed
            try:
                # Prepare inputs for the crew
                inputs = {
                    'story_title': approved_content.story_outline.title,
                    'story_summary': approved_content.story_outline.summary,
                    'story_narrative': approved_content.story_outline.narrative_text,
                    'target_duration': approved_content.story_outline.estimated_duration,
                    'characters': self._format_characters_for_crew(approved_content.character_profiles),
                    'num_shots': math.ceil(approved_content.story_outline.estimated_duration / 5)
                }
                
                # Execute the crew
                result = self.crew().kickoff(inputs=inputs)
                
                # Parse and structure the results
                detailed_story, video_prompts = self._parse_crew_results(result, approved_content)
                
            except Exception as crew_error:
                logger.warning(f"CrewAI execution failed: {crew_error}, using direct processing")
                # Fallback to direct processing
                detailed_story, video_prompts = self._process_with_direct_calls(approved_content)
            
            # Save results
            results = {
                "project_id": project_id,
                "detailed_story": detailed_story,
                "video_prompts": video_prompts,
                "processing_status": "completed"
            }
            
            self._save_results(project_id, results)
            
            logger.info(f"Successfully processed project {project_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error processing project {project_id}: {e}")
            raise
    
    def _process_with_direct_calls(self, approved_content: ApprovedContent) -> tuple[DetailedStory, List[VideoPrompt]]:
        """Process using direct LLM calls as fallback."""
        logger.info("Using direct LLM calls for processing")
        
        try:
            # Step 1: Expand story
            story_prompt = f"""
            将以下故事大纲扩展为完整、详细、富有视觉感的叙述文本：

            **故事信息：**
            - 标题：{approved_content.story_outline.title}
            - 摘要：{approved_content.story_outline.summary}
            - 原始叙述：{approved_content.story_outline.narrative_text}
            - 目标时长：{approved_content.story_outline.estimated_duration}秒

            **角色信息：**
            {self._format_characters_for_crew(approved_content.character_profiles)}

            请输出一个完整、详细、富有电影感的故事文本，为后续视频制作提供充分的视觉指导。
            """
            
            story_response = self._call_llm_with_fallback([
                {'role': 'system', 'content': '你是专业的故事编剧和视觉叙事专家。'},
                {'role': 'user', 'content': story_prompt}
            ])
            
            detailed_story = DetailedStory(
                title=approved_content.story_outline.title,
                full_story_text=story_response,
                total_duration=approved_content.story_outline.estimated_duration
            )
            
            # Step 2: Generate VEO3 prompts
            num_shots = math.ceil(approved_content.story_outline.estimated_duration / 5)
            
            prompt_generation = f"""
            基于以下详细故事，生成{num_shots}个专业的VEO3视频生成提示词。

            **故事内容：**
            {story_response}

            **角色信息：**
            {self._format_characters_for_crew(approved_content.character_profiles)}

            **要求：**
            请严格按照以下格式输出{num_shots}个VEO3提示词，每个提示词独占一行：

            1. [具体的场景描述，包含角色动作、环境、镜头角度、光线效果]
            2. [下一个场景的具体描述，包含角色动作、环境、镜头角度、光线效果]
            3. [继续下一个场景...]

            每个提示词要求：
            - 包含准确的角色外观描述
            - 指定具体的场景环境
            - 描述镜头角度（如：近景、远景、特写、俯视等）
            - 说明光线和色彩氛围
            - 描述角色的具体动作和表情
            - 控制在50-80字之间

            示例格式：
            1. 银白色太空服的女宇航员艾丽坐在驾驶舱内，通过舷窗凝视星空，蓝色仪表盘光芒映照在她坚毅的脸庞上，中景拍摄，冷色调科幻氛围
            2. 蓝色全息投影的AI助手ARIA在控制台上显示导航数据，艾丽伸手触摸全息界面，近景特写，暖色光线与冷蓝色形成对比

            请直接输出{num_shots}个编号的提示词，不要额外解释：
            """
            
            prompts_response = self._call_llm_with_fallback([
                {'role': 'system', 'content': '你是专业的分镜头艺术家和VEO3提示词工程师。请严格按照要求的格式输出提示词。'},
                {'role': 'user', 'content': prompt_generation}
            ])
            
            # Parse prompts
            video_prompts = self._parse_prompts_from_text(prompts_response, num_shots, approved_content.character_profiles)
            
            return detailed_story, video_prompts
            
        except Exception as e:
            logger.error(f"Direct processing failed: {e}")
            return self._generate_fallback_results(approved_content)
    
    def _parse_prompts_from_text(self, text: str, num_shots: int, character_profiles: List[CharacterProfile]) -> List[VideoPrompt]:
        """Parse prompts from AI-generated text."""
        lines = text.strip().split('\n')
        prompts = []
        char_images = [char.image_url for char in character_profiles if hasattr(char, 'image_url') and char.image_url]
        
        # 更精确的解析逻辑
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 查找编号的提示词
            for i in range(1, num_shots + 1):
                # 匹配各种可能的编号格式
                if (line.startswith(f"{i}.") or 
                    line.startswith(f"{i}、") or 
                    line.startswith(f"{i}：") or 
                    line.startswith(f"{i} ")):
                    
                    # 提取提示词内容
                    if line.startswith(f"{i}."):
                        clean_prompt = line[len(f"{i}."):].strip()
                    elif line.startswith(f"{i}、"):
                        clean_prompt = line[len(f"{i}、"):].strip()
                    elif line.startswith(f"{i}："):
                        clean_prompt = line[len(f"{i}："):].strip()
                    else:  # f"{i} "
                        clean_prompt = line[len(f"{i} "):].strip()
                    
                    # 只有当提示词长度合理时才添加
                    if len(clean_prompt) > 20:
                        prompts.append(VideoPrompt(
                            shot_id=i,
                            veo3_prompt=clean_prompt,
                            duration=5,
                            character_reference_images=char_images
                        ))
                        break
        
        # 如果解析出的提示词不够，用fallback填充
        while len(prompts) < num_shots:
            shot_id = len(prompts) + 1
            # 生成更具体的fallback提示词
            characters_str = "、".join([char.name for char in character_profiles])
            fallback_prompt = f"电影级画质，{characters_str}在未来科幻场景中的第{shot_id}个镜头，专业摄影，高质量渲染，细腻光影效果"
            
            prompts.append(VideoPrompt(
                shot_id=shot_id,
                veo3_prompt=fallback_prompt,
                duration=5,
                character_reference_images=char_images
            ))
        
        return prompts[:num_shots]
    
    def _extract_approved_content(self, project_data: Dict[str, Any]) -> ApprovedContent:
        """Extract ApprovedContent from project data."""
        try:
            # First try to get from approved_content if it exists
            if 'approved_content' in project_data:
                approved_data = project_data['approved_content']
                story_outline = StoryOutline(**approved_data['story_outline'])
                character_profiles = [CharacterProfile(**char) for char in approved_data['character_profiles']]
                return ApprovedContent(
                    story_outline=story_outline,
                    character_profiles=character_profiles,
                    user_confirmed=approved_data.get('user_confirmed', True)
                )
            
            # Fallback: load from individual files in project structure
            project_dir = Path(project_data.get('project_dir', ''))
            
            # Load story outline
            story_outline_data = project_data.get('story_outline')
            if not story_outline_data:
                story_file = project_dir / "story_outline.json"
                if story_file.exists():
                    with open(story_file, 'r', encoding='utf-8') as f:
                        story_outline_data = json.load(f)
                else:
                    raise ValueError("No story outline data found")
            
            # Load character profiles
            character_profiles_data = project_data.get('character_profiles', [])
            if not character_profiles_data:
                characters_dir = project_dir / "characters"
                if characters_dir.exists():
                    summary_file = characters_dir / "characters_summary.json"
                    if summary_file.exists():
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            summary_data = json.load(f)
                            character_profiles_data = summary_data.get('characters', [])
            
            # Convert to Pydantic models
            story_outline = StoryOutline(**story_outline_data)
            character_profiles = [CharacterProfile(**char) for char in character_profiles_data]
            
            return ApprovedContent(
                story_outline=story_outline,
                character_profiles=character_profiles,
                user_confirmed=True
            )
            
        except Exception as e:
            logger.error(f"Error extracting approved content: {e}")
            raise
    
    def _format_characters_for_crew(self, characters: List[CharacterProfile]) -> str:
        """Format character information for crew tasks."""
        formatted = []
        for char in characters:
            char_info = f"**{char.name}** ({char.role})\n"
            char_info += f"- 外观: {char.appearance}\n"
            char_info += f"- 性格: {char.personality}\n"
            if hasattr(char, 'image_url') and char.image_url:
                char_info += f"- 图像参考: {char.image_url}\n"
            formatted.append(char_info)
        return "\n".join(formatted)
    
    def _parse_crew_results(self, crew_result, approved_content: ApprovedContent) -> tuple[DetailedStory, List[VideoPrompt]]:
        """Parse crew execution results into structured data."""
        try:
            # The crew result should contain the final task output
            final_output = str(crew_result)
            
            # Try to extract detailed story and prompts from the result
            # This is a simplified parsing - in practice, you might want more sophisticated parsing
            lines = final_output.split('\n')
            
            # Look for detailed story section
            detailed_story_text = ""
            video_prompts = []
            
            current_section = ""
            prompt_count = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if "详细故事" in line or "完整故事" in line or "扩展故事" in line:
                    current_section = "story"
                    continue
                elif "视频提示词" in line or "VEO3" in line or "镜头" in line:
                    current_section = "prompts"
                    continue
                elif line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")) and current_section == "prompts":
                    # This looks like a prompt
                    prompt_count += 1
                    clean_prompt = line
                    # Remove numbering
                    if line.startswith(f"{prompt_count}."):
                        clean_prompt = line[len(f"{prompt_count}."):].strip()
                    
                    char_images = [char.image_url for char in approved_content.character_profiles 
                                 if hasattr(char, 'image_url') and char.image_url]
                    
                    video_prompts.append(VideoPrompt(
                        shot_id=prompt_count,
                        veo3_prompt=clean_prompt,
                        duration=5,
                        character_reference_images=char_images
                    ))
                elif current_section == "story":
                    detailed_story_text += line + " "
            
            # Create DetailedStory object
            if not detailed_story_text.strip():
                detailed_story_text = approved_content.story_outline.narrative_text
            
            detailed_story = DetailedStory(
                title=approved_content.story_outline.title,
                full_story_text=detailed_story_text.strip(),
                total_duration=approved_content.story_outline.estimated_duration
            )
            
            # Ensure we have the right number of prompts
            target_prompts = math.ceil(approved_content.story_outline.estimated_duration / 5)
            while len(video_prompts) < target_prompts:
                char_images = [char.image_url for char in approved_content.character_profiles 
                             if hasattr(char, 'image_url') and char.image_url]
                
                video_prompts.append(VideoPrompt(
                    shot_id=len(video_prompts) + 1,
                    veo3_prompt=f"{approved_content.story_outline.title}第{len(video_prompts) + 1}个场景，电影级画质，专业拍摄",
                    duration=5,
                    character_reference_images=char_images
                ))
            
            return detailed_story, video_prompts[:target_prompts]
            
        except Exception as e:
            logger.error(f"Error parsing crew results: {e}")
            # Fallback to basic generation
            return self._generate_fallback_results(approved_content)
    
    def _generate_fallback_results(self, approved_content: ApprovedContent) -> tuple[DetailedStory, List[VideoPrompt]]:
        """Generate fallback results if crew execution fails."""
        detailed_story = DetailedStory(
            title=approved_content.story_outline.title,
            full_story_text=approved_content.story_outline.narrative_text,
            total_duration=approved_content.story_outline.estimated_duration
        )
        
        target_prompts = math.ceil(approved_content.story_outline.estimated_duration / 5)
        char_images = [char.image_url for char in approved_content.character_profiles 
                     if hasattr(char, 'image_url') and char.image_url]
        
        video_prompts = []
        for i in range(target_prompts):
            video_prompts.append(VideoPrompt(
                shot_id=i + 1,
                veo3_prompt=f"{approved_content.story_outline.title}第{i+1}个场景，电影级画质，专业拍摄，高质量视频",
                duration=5,
                character_reference_images=char_images
            ))
        
        return detailed_story, video_prompts
    
    def _save_results(self, project_id: str, results: Dict[str, Any]):
        """Save script crew results to the project."""
        try:
            project_dir = Path("projects/projects") / project_id
            scripts_dir = project_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            
            # Save detailed story
            detailed_story_path = scripts_dir / "detailed_story.json"
            with open(detailed_story_path, 'w', encoding='utf-8') as f:
                json.dump(results['detailed_story'].model_dump(), f, indent=2, ensure_ascii=False)
            
            # Save video prompts
            video_prompts_path = scripts_dir / "video_prompts.json"
            prompts_data = [prompt.model_dump() for prompt in results['video_prompts']]
            with open(video_prompts_path, 'w', encoding='utf-8') as f:
                json.dump(prompts_data, f, indent=2, ensure_ascii=False)
            
            # Save processing summary
            summary_path = scripts_dir / "script_crew_summary.json"
            summary = {
                "project_id": project_id,
                "detailed_story": {
                    "title": results['detailed_story'].title,
                    "duration": results['detailed_story'].total_duration,
                    "word_count": len(results['detailed_story'].full_story_text.split())
                },
                "video_prompts": {
                    "total_shots": len(results['video_prompts']),
                    "total_duration": sum(p.duration for p in results['video_prompts']),
                    "veo3_optimized": True
                },
                "status": results['processing_status']
            }
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved script crew results for project {project_id}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise