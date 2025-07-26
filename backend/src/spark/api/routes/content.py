"""
内容生成相关的API路由 - 增强版本支持outline和角色图片传递
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import logging
import json
from pathlib import Path

from ...chatbot.idea_structurer import IdeaStructurer
from ...chatbot.character_generator import CharacterProfileGenerator
from ...models import UserIdea, StoryOutline, CharacterProfile
from .chat import get_session_id, get_chatbot_for_session

logger = logging.getLogger(__name__)

# 创建蓝图
content_bp = Blueprint('content', __name__, url_prefix='/api/content')

# 全局组件实例
idea_structurer = IdeaStructurer()
character_generator = CharacterProfileGenerator()


@content_bp.route('/structure', methods=['POST'])
def structure_idea():
    """结构化用户创意"""
    try:
        session_id = get_session_id()
        chatbot = get_chatbot_for_session(session_id)
        
        conversation_history = chatbot.get_conversation_history()
        if not conversation_history:
            return jsonify({'error': '没有对话历史可结构化'}), 400
        
        user_idea = idea_structurer.structure_conversation(conversation_history)
        if not user_idea:
            return jsonify({'error': '结构化创意失败'}), 500
        
        # 验证完整性
        validation = idea_structurer.validate_idea_completeness(user_idea)
        
        return jsonify({
            'status': 'success',
            'user_idea': user_idea.model_dump(),
            'validation': validation,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"结构化创意时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@content_bp.route('/story/generate', methods=['POST'])
def generate_story_outline():
    """生成故事大纲"""
    try:
        data = request.get_json()
        if not data or 'user_idea' not in data:
            return jsonify({'error': '缺少用户创意数据'}), 400
        
        # 从JSON重建UserIdea对象
        user_idea = UserIdea(**data['user_idea'])
        
        story_outline = idea_structurer.generate_story_outline(user_idea)
        if not story_outline:
            return jsonify({'error': '生成故事大纲失败'}), 500
        
        return jsonify({
            'status': 'success',
            'story_outline': story_outline.model_dump(),
            'session_id': get_session_id(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"生成故事大纲时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@content_bp.route('/characters/generate', methods=['POST'])
def generate_characters():
    """生成角色档案"""
    try:
        data = request.get_json()
        if not data or 'user_idea' not in data:
            return jsonify({'error': '缺少用户创意数据'}), 400
        
        # 从JSON重建UserIdea对象
        user_idea = UserIdea(**data['user_idea'])
        
        if not user_idea.basic_characters:
            return jsonify({'error': '用户创意中没有角色信息'}), 400
        
        character_profiles = character_generator.generate_complete_character_profiles(
            user_idea.basic_characters,
            user_idea
        )
        
        if not character_profiles:
            return jsonify({'error': '生成角色档案失败'}), 500
        
        return jsonify({
            'status': 'success',
            'character_profiles': [char.model_dump() for char in character_profiles],
            'character_count': len(character_profiles),
            'session_id': get_session_id(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"生成角色档案时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@content_bp.route('/project/<project_id>/outline', methods=['GET'])
def get_project_outline():
    """获取项目的故事大纲"""
    try:
        project_dir = Path("projects/projects") / project_id
        outline_file = project_dir / "story_outline.json"
        
        if not outline_file.exists():
            return jsonify({'error': '项目大纲不存在'}), 404
        
        with open(outline_file, 'r', encoding='utf-8') as f:
            outline_data = json.load(f)
        
        return jsonify({
            'status': 'success',
            'project_id': project_id,
            'outline': outline_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取项目大纲时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@content_bp.route('/project/<project_id>/characters', methods=['GET'])
def get_project_characters():
    """获取项目的角色信息和图片"""
    try:
        project_dir = Path("projects/projects") / project_id
        characters_file = project_dir / "characters.json"
        character_images_file = project_dir / "character_images.json"
        
        if not characters_file.exists():
            return jsonify({'error': '项目角色信息不存在'}), 404
        
        # 读取角色基本信息
        with open(characters_file, 'r', encoding='utf-8') as f:
            characters_data = json.load(f)
        
        # 读取角色图片信息
        character_images = []
        if character_images_file.exists():
            with open(character_images_file, 'r', encoding='utf-8') as f:
                character_images = json.load(f)
        
        # 合并角色信息和图片
        for character in characters_data:
            character_name = character.get('name')
            for img_info in character_images:
                if img_info.get('character_name') == character_name:
                    character['image_url'] = img_info.get('image_url')
                    character['visual_tags'] = img_info.get('visual_tags', [])
                    break
        
        return jsonify({
            'status': 'success',
            'project_id': project_id,
            'characters': characters_data,
            'character_count': len(characters_data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取项目角色时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@content_bp.route('/project/<project_id>/character/<character_name>/image', methods=['GET'])
def get_character_image(project_id, character_name):
    """获取特定角色的图片（代理图片URL）"""
    try:
        project_dir = Path("projects/projects") / project_id
        character_images_file = project_dir / "character_images.json"
        
        if not character_images_file.exists():
            return jsonify({'error': '角色图片信息不存在'}), 404
        
        with open(character_images_file, 'r', encoding='utf-8') as f:
            character_images = json.load(f)
        
        # 查找指定角色的图片
        for img_info in character_images:
            if img_info.get('character_name') == character_name:
                image_url = img_info.get('image_url')
                if image_url:
                    return jsonify({
                        'status': 'success',
                        'project_id': project_id,
                        'character_name': character_name,
                        'image_url': image_url,
                        'visual_tags': img_info.get('visual_tags', []),
                        'timestamp': datetime.now().isoformat()
                    })
        
        return jsonify({'error': f'角色 {character_name} 的图片不存在'}), 404
        
    except Exception as e:
        logger.error(f"获取角色图片时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@content_bp.route('/project/<project_id>/complete', methods=['GET'])
def get_complete_project_content():
    """获取项目的完整内容（大纲+角色+图片）"""
    try:
        project_dir = Path("projects/projects") / project_id
        approved_content_file = project_dir / "approved_content.json"
        
        if not approved_content_file.exists():
            return jsonify({'error': '项目内容不存在'}), 404
        
        with open(approved_content_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # 确保包含所有必要信息
        response_data = {
            'status': 'success',
            'project_id': project_id,
            'project_name': project_data.get('project_name', ''),
            'created_at': project_data.get('created_at', ''),
            'user_idea': project_data.get('user_idea', {}),
            'story_outline': project_data.get('story_outline', {}),
            'character_profiles': project_data.get('character_profiles', []),
            'status': project_data.get('status', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"获取完整项目内容时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@content_bp.route('/validate', methods=['POST'])
def validate_content():
    """验证内容完整性"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '缺少数据'}), 400
        
        validation_results = {}
        
        # 验证用户创意
        if 'user_idea' in data:
            try:
                user_idea = UserIdea(**data['user_idea'])
                validation = idea_structurer.validate_idea_completeness(user_idea)
                validation_results['user_idea'] = validation
            except Exception as e:
                validation_results['user_idea'] = {
                    'is_valid': False,
                    'error': str(e)
                }
        
        # 验证故事大纲
        if 'story_outline' in data:
            try:
                story_outline = StoryOutline(**data['story_outline'])
                validation_results['story_outline'] = {
                    'is_valid': True,
                    'title_length': len(story_outline.title),
                    'summary_length': len(story_outline.summary),
                    'narrative_length': len(story_outline.narrative_text),
                    'estimated_duration': story_outline.estimated_duration
                }
            except Exception as e:
                validation_results['story_outline'] = {
                    'is_valid': False,
                    'error': str(e)
                }
        
        # 验证角色档案
        if 'character_profiles' in data:
            try:
                character_profiles = [CharacterProfile(**char) for char in data['character_profiles']]
                validation_results['character_profiles'] = {
                    'is_valid': True,
                    'character_count': len(character_profiles),
                    'characters_with_images': sum(1 for char in character_profiles if char.image_url),
                    'average_motivations': sum(len(char.motivations) for char in character_profiles) / len(character_profiles) if character_profiles else 0
                }
            except Exception as e:
                validation_results['character_profiles'] = {
                    'is_valid': False,
                    'error': str(e)
                }
        
        return jsonify({
            'status': 'success',
            'validation_results': validation_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"验证内容时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500