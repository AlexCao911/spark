"""
Character profile generation with visual design using Wanx2.1-t2i-turbo.
"""

import json
import logging
import requests
import base64
import io
from typing import List, Optional, Dict, Any
from PIL import Image
from ..models import CharacterProfile, UserIdea
from ..config import config
from ..error_handling import APIErrorHandler, retry_with_backoff

logger = logging.getLogger(__name__)


class WanxImageGenerator:
    """Wanx2.1-t2i-turbo image generation client."""
    
    def __init__(self):
        self.config = config
        self.api_key = self.config.IMAGE_GEN_API_KEY
        self.endpoint = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        self.error_handler = APIErrorHandler(self.config.retry_config)
    
    def generate_image(self, prompt: str, style: str = "photography", size: str = "1024*1024") -> Optional[str]:
        """Generate image using Wanx2.1-t2i-turbo model."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable"  # This API key requires async mode
            }
            
            payload = {
                "model": "wanx-v1",
                "input": {
                    "prompt": prompt,
                    "negative_prompt": "blurry, low quality, distorted, deformed, ugly, bad anatomy",
                    "style": style,
                    "size": size,
                    "n": 1,
                    "seed": None,
                    "ref_mode": "repaint"
                },
                "parameters": {
                    "style": style,
                    "size": size,
                    "n": 1
                }
            }
            
            logger.info(f"Generating image with prompt: {prompt[:100]}...")
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=60,
                verify=True  # Keep SSL verification enabled
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"API Response: {result}")
                
                # Handle sync response
                if "output" in result and "results" in result["output"]:
                    results = result["output"]["results"]
                    if results and len(results) > 0:
                        return results[0].get("url", "")
                
                # Handle async response (fallback)
                elif "output" in result and "task_id" in result["output"]:
                    task_id = result["output"]["task_id"]
                    return self._wait_for_async_result(task_id)
                
                logger.warning(f"Unexpected response format: {result}")
                return None
                
            else:
                logger.error(f"Image generation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None
    
    def _wait_for_async_result(self, task_id: str, max_wait: int = 60) -> Optional[str]:
        """Wait for async image generation to complete."""
        import time
        
        query_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        logger.info(f"Waiting for async task {task_id} to complete...")
        
        start_time = time.time()
        attempt = 0
        while time.time() - start_time < max_wait:
            try:
                attempt += 1
                logger.info(f"Querying task status (attempt {attempt}): {query_url}")
                
                response = requests.get(query_url, headers=headers, timeout=10)
                
                logger.info(f"Query response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Full API response: {result}")
                    
                    # task_status is inside the output object
                    output = result.get("output", {})
                    task_status = output.get("task_status", "")
                    
                    logger.info(f"Task status: {task_status}")
                    
                    if task_status == "SUCCEEDED":
                        results = output.get("results", [])
                        logger.info(f"Task succeeded, results: {results}")
                        
                        if results and len(results) > 0:
                            image_url = results[0].get("url", "")
                            logger.info(f"Generated image URL: {image_url}")
                            return image_url
                    
                    elif task_status == "FAILED":
                        logger.error(f"Async image generation failed: {result}")
                        return None
                    
                    elif task_status in ["PENDING", "RUNNING"]:
                        logger.info(f"Task still {task_status}, waiting...")
                        time.sleep(3)
                    else:
                        logger.warning(f"Unknown task status: {task_status}")
                        time.sleep(3)
                        
                else:
                    logger.error(f"Failed to query task status: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error querying async result: {str(e)}")
                time.sleep(3)
        
        logger.warning(f"Async image generation timed out for task {task_id} after {max_wait} seconds")
        return None


class CharacterProfileGenerator:
    """Creates comprehensive character profiles with images using Wanx2.1-t2i-turbo."""
    
    def __init__(self):
        self.image_generator = WanxImageGenerator()
        self.config = config
    
    def generate_complete_character_profiles(self, characters: List[str], user_idea: UserIdea) -> List[CharacterProfile]:
        """Generate complete character profiles with images from basic character descriptions."""
        profiles = []
        
        for i, character_desc in enumerate(characters):
            # Generate enhanced character profile
            profile = self._create_enhanced_profile(character_desc, i, user_idea)
            
            # Generate character image
            if self.config.IMAGE_GEN_API_KEY:
                image_url = self.generate_character_image(profile, user_idea)
                profile.image_url = image_url or ""
            
            profiles.append(profile)
        
        return profiles
    
    def _create_enhanced_profile(self, character_desc: str, index: int, user_idea: UserIdea) -> CharacterProfile:
        """Create an enhanced character profile with detailed attributes."""
        
        # Generate character name based on description and genre
        name = self._generate_character_name(character_desc, user_idea.genre, index)
        
        # Determine role
        role = "main" if index == 0 else "supporting"
        
        # Generate personality based on description and genre
        personality = self._generate_personality(character_desc, user_idea.genre)
        
        # Generate backstory
        backstory = self._generate_backstory(character_desc, user_idea.theme, user_idea.genre)
        
        # Generate motivations
        motivations = self._generate_motivations(character_desc, user_idea.theme)
        
        # Generate visual consistency tags
        visual_tags = self._generate_visual_tags(character_desc, user_idea.visual_style)
        
        return CharacterProfile(
            name=name,
            role=role,
            appearance=character_desc,
            personality=personality,
            backstory=backstory,
            motivations=motivations,
            relationships={},  # Will be populated later if needed
            image_url="",  # Will be generated
            visual_consistency_tags=visual_tags
        )
    
    def _generate_character_name(self, desc: str, genre: str, index: int) -> str:
        """Generate appropriate character name based on description and genre."""
        # Simple name generation based on genre and role
        genre_names = {
            "sci-fi": ["Alex", "Zara", "Kai", "Nova", "Rex"],
            "fantasy": ["Aria", "Theron", "Luna", "Darius", "Elara"],
            "action": ["Jake", "Maya", "Cole", "Raven", "Phoenix"],
            "comedy": ["Charlie", "Penny", "Max", "Ruby", "Sam"],
            "drama": ["Emma", "David", "Sarah", "Michael", "Grace"],
            "horror": ["Raven", "Damien", "Vera", "Marcus", "Lilith"]
        }
        
        names = genre_names.get(genre.lower(), ["Character", "Hero", "Ally", "Friend", "Companion"])
        return names[index % len(names)]
    
    def _generate_personality(self, desc: str, genre: str) -> str:
        """Generate personality traits based on description and genre."""
        desc_lower = desc.lower()
        
        if "brave" in desc_lower or "hero" in desc_lower:
            return "勇敢、坚定，面对困难从不退缩，有强烈的正义感"
        elif "wise" in desc_lower or "mentor" in desc_lower:
            return "睿智、耐心，经验丰富，善于指导他人"
        elif "villain" in desc_lower or "evil" in desc_lower:
            return "狡猾、野心勃勃，为达目的不择手段"
        elif "funny" in desc_lower or "comic" in desc_lower:
            return "幽默风趣，乐观开朗，总能在困境中找到希望"
        else:
            # Default based on genre
            genre_personalities = {
                "sci-fi": "理性、好奇，对科技和未知充满探索欲",
                "fantasy": "神秘、富有想象力，相信魔法和奇迹",
                "action": "果断、勇敢，行动力强，不畏艰险",
                "comedy": "乐观、幽默，总能化解尴尬局面",
                "drama": "深沉、敏感，情感丰富，善于思考",
                "horror": "谨慎、敏锐，在危险中保持冷静"
            }
            return genre_personalities.get(genre.lower(), "性格鲜明，有自己的独特魅力")
    
    def _generate_backstory(self, desc: str, theme: str, genre: str) -> str:
        """Generate character backstory."""
        return f"在{theme}的背景下成长，经历了许多挑战和考验。作为{desc}，他们的过去塑造了现在的性格和能力，为即将到来的冒险做好了准备。"
    
    def _generate_motivations(self, desc: str, theme: str) -> List[str]:
        """Generate character motivations."""
        desc_lower = desc.lower()
        
        if "hero" in desc_lower or "protagonist" in desc_lower:
            return ["拯救世界", "保护重要的人", "实现自我价值"]
        elif "villain" in desc_lower:
            return ["获得权力", "复仇", "改变世界秩序"]
        elif "mentor" in desc_lower:
            return ["传授知识", "指导年轻人", "完成使命"]
        else:
            return ["寻找真相", "保护家人", "实现梦想"]
    
    def _generate_visual_tags(self, desc: str, visual_style: str) -> List[str]:
        """Generate visual consistency tags for character design."""
        tags = []
        
        # Add style-based tags
        if visual_style:
            tags.append(visual_style.lower())
        
        # Add description-based tags
        desc_lower = desc.lower()
        if "young" in desc_lower:
            tags.append("youthful")
        if "old" in desc_lower or "elder" in desc_lower:
            tags.append("mature")
        if "strong" in desc_lower or "warrior" in desc_lower:
            tags.append("athletic")
        if "wise" in desc_lower or "scholar" in desc_lower:
            tags.append("intellectual")
        
        return tags
    
    def generate_character_image(self, character_profile: CharacterProfile, user_idea: UserIdea) -> Optional[str]:
        """Generate character image using Wanx2.1-t2i-turbo."""
        try:
            # Create detailed prompt for image generation
            prompt = self._create_image_prompt(character_profile, user_idea)
            
            # Determine style based on user idea
            style = self._determine_image_style(user_idea.visual_style, user_idea.genre)
            
            logger.info(f"Generating image for {character_profile.name} with style: {style}")
            
            # Generate image
            image_url = self.image_generator.generate_image(
                prompt=prompt,
                style=style,
                size="1024*1024"
            )
            
            if image_url:
                logger.info(f"Successfully generated image for {character_profile.name}")
                return image_url
            else:
                logger.warning(f"Failed to generate image for {character_profile.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating character image: {str(e)}")
            return None
    
    def _create_image_prompt(self, character_profile: CharacterProfile, user_idea: UserIdea) -> str:
        """Create detailed prompt for character image generation."""
        
        # Base character description
        prompt_parts = [
            f"A {character_profile.role} character",
            f"described as: {character_profile.appearance}",
            f"personality: {character_profile.personality}",
        ]
        
        # Add genre-specific elements
        genre_styles = {
            "sci-fi": "futuristic, high-tech, space age",
            "fantasy": "magical, medieval, mystical",
            "action": "dynamic, intense, heroic",
            "comedy": "colorful, expressive, cheerful",
            "drama": "realistic, emotional, detailed",
            "horror": "dark, atmospheric, mysterious"
        }
        
        if user_idea.genre.lower() in genre_styles:
            prompt_parts.append(genre_styles[user_idea.genre.lower()])
        
        # Add visual style
        if user_idea.visual_style:
            prompt_parts.append(f"visual style: {user_idea.visual_style}")
        
        # Add quality modifiers
        prompt_parts.extend([
            "high quality",
            "detailed",
            "professional",
            "character design",
            "concept art"
        ])
        
        return ", ".join(prompt_parts)
    
    def _determine_image_style(self, visual_style: str, genre: str) -> str:
        """Determine appropriate image style for Wanx generation."""
        
        # Map visual styles to Wanx styles (with proper format)
        style_mapping = {
            "cinematic": "<photography>",
            "animated": "<anime>",
            "realistic": "<photography>", 
            "cartoon": "<3d cartoon>",
            "comic": "<flat illustration>",
            "artistic": "<oil painting>",
            "sketch": "<sketch>",
            "watercolor": "<watercolor>",
            "chinese": "<chinese painting>",
            "portrait": "<portrait>"
        }
        
        # Check visual style first
        if visual_style and visual_style.lower() in style_mapping:
            return style_mapping[visual_style.lower()]
        
        # Fallback to genre-based style
        genre_styles = {
            "sci-fi": "<photography>",
            "fantasy": "<oil painting>",
            "action": "<photography>",
            "comedy": "<anime>",
            "drama": "<photography>",
            "horror": "<photography>"
        }
        
        return genre_styles.get(genre.lower(), "<photography>")