"""
项目管理相关的API路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from ...chatbot.simple_confirmation import confirmation_manager
from ...models import UserIdea, StoryOutline, CharacterProfile

logger = logging.getLogger(__name__)

# 创建蓝图
projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@projects_bp.route('', methods=['GET'])
def list_projects():
    """获取项目列表"""
    try:
        # 支持分页和过滤
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status', '')
        
        projects = confirmation_manager.list_projects()
        
        # 状态过滤
        if status_filter:
            projects = [p for p in projects if p.get('status') == status_filter]
        
        # 分页
        total = len(projects)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_projects = projects[start:end]
        
        return jsonify({
            'status': 'success',
            'projects': paginated_projects,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取项目列表时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('/<project_id>', methods=['GET'])
def get_project(project_id):
    """获取特定项目"""
    try:
        project_data = confirmation_manager.load_approved_content(project_id)
        
        if not project_data:
            return jsonify({'error': '项目不存在'}), 404
        
        return jsonify({
            'status': 'success',
            'project': project_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取项目时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    try:
        result = confirmation_manager.delete_project(project_id)
        
        if result['status'] == 'success':
            result['timestamp'] = datetime.now().isoformat()
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"删除项目时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('', methods=['POST'])
def create_project():
    """创建新项目（确认并保存内容）"""
    try:
        data = request.get_json()
        required_fields = ['user_idea', 'story_outline', 'character_profiles']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 重建对象
        user_idea = UserIdea(**data['user_idea'])
        story_outline = StoryOutline(**data['story_outline'])
        character_profiles = [CharacterProfile(**char) for char in data['character_profiles']]
        
        project_name = data.get('project_name', '')
        
        # 保存确认内容
        result = confirmation_manager.save_approved_content(
            user_idea=user_idea,
            story_outline=story_outline,
            character_profiles=character_profiles,
            project_name=project_name if project_name.strip() else None
        )
        
        if result['status'] == 'success':
            result['timestamp'] = datetime.now().isoformat()
            return jsonify(result), 201
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"创建项目时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('/<project_id>/characters/<character_name>/regenerate', methods=['POST'])
def regenerate_character_image(project_id, character_name):
    """重新生成角色图片"""
    try:
        data = request.get_json()
        feedback = data.get('feedback', '') if data else ''
        
        result = confirmation_manager.regenerate_character_image(
            project_id=project_id,
            character_name=character_name,
            feedback=feedback
        )
        
        if result['status'] == 'success':
            result['timestamp'] = datetime.now().isoformat()
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"重新生成角色图片时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('/<project_id>/export', methods=['GET'])
def export_project(project_id):
    """导出项目数据"""
    try:
        project_data = confirmation_manager.load_approved_content(project_id)
        
        if not project_data:
            return jsonify({'error': '项目不存在'}), 404
        
        # 支持不同的导出格式
        export_format = request.args.get('format', 'json').lower()
        
        if export_format == 'json':
            return jsonify({
                'status': 'success',
                'format': 'json',
                'data': project_data,
                'exported_at': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': f'不支持的导出格式: {export_format}'}), 400
            
    except Exception as e:
        logger.error(f"导出项目时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('/search', methods=['GET'])
def search_projects():
    """搜索项目"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': '缺少搜索查询'}), 400
        
        projects = confirmation_manager.list_projects()
        
        # 简单的文本搜索
        matching_projects = []
        query_lower = query.lower()
        
        for project in projects:
            if (query_lower in project.get('project_name', '').lower() or
                query_lower in project.get('project_id', '').lower()):
                matching_projects.append(project)
        
        return jsonify({
            'status': 'success',
            'query': query,
            'results': matching_projects,
            'result_count': len(matching_projects),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"搜索项目时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500