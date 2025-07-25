"""
Flask API应用 - Spark AI视频生成聊天机器人后端
"""

import os
import logging
from flask import Flask, jsonify, session, request
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
import uuid

from .config import config
from .routes.chat import chat_bp
from .routes.content import content_bp
from .routes.projects import projects_bp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 确保session目录存在
    if app.config['SESSION_TYPE'] == 'filesystem':
        os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # 初始化扩展
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'])
    Session(app)
    
    # 注册蓝图
    app.register_blueprint(chat_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(projects_bp)
    
    # 基础路由
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': config_name
        })
    
    @app.route('/api/session/info', methods=['GET'])
    def get_session_info():
        """获取会话信息"""
        try:
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            return jsonify({
                'session_id': session['session_id'],
                'timestamp': datetime.now().isoformat(),
                'status': 'active'
            })
            
        except Exception as e:
            logger.error(f"获取会话信息时出错: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/docs', methods=['GET'])
    def api_docs():
        """API文档"""
        docs = {
            'title': 'Spark AI Video Generation API',
            'version': '1.0.0',
            'description': 'AI视频生成聊天机器人后端API',
            'endpoints': {
                'chat': {
                    'POST /api/chat/send': '发送消息到聊天机器人',
                    'GET /api/chat/history': '获取聊天历史',
                    'POST /api/chat/reset': '重置聊天会话',
                    'GET /api/chat/status': '获取聊天状态'
                },
                'content': {
                    'POST /api/content/structure': '结构化用户创意',
                    'POST /api/content/story/generate': '生成故事大纲',
                    'POST /api/content/characters/generate': '生成角色档案',
                    'POST /api/content/validate': '验证内容完整性'
                },
                'projects': {
                    'GET /api/projects': '获取项目列表',
                    'POST /api/projects': '创建新项目',
                    'GET /api/projects/<id>': '获取特定项目',
                    'DELETE /api/projects/<id>': '删除项目',
                    'GET /api/projects/search': '搜索项目',
                    'GET /api/projects/<id>/export': '导出项目',
                    'POST /api/projects/<id>/characters/<name>/regenerate': '重新生成角色图片'
                },
                'system': {
                    'GET /api/health': '健康检查',
                    'GET /api/session/info': '获取会话信息',
                    'GET /api/docs': '查看API文档'
                }
            }
        }
        return jsonify(docs)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': '接口不存在',
            'message': '请检查URL路径是否正确',
            'available_endpoints': '/api/docs'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': '请求方法不允许',
            'message': '请检查HTTP方法是否正确'
        }), 405
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': '请求格式错误',
            'message': '请检查请求数据格式'
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"内部服务器错误: {str(error)}")
        return jsonify({
            'error': '内部服务器错误',
            'message': '服务器处理请求时出现错误'
        }), 500
    
    # 请求日志中间件
    @app.before_request
    def log_request_info():
        """记录请求信息"""
        logger.info(f"Request: {request.method} {request.url}")
    
    @app.after_request
    def log_response_info(response):
        """记录响应信息"""
        logger.info(f"Response: {response.status_code}")
        return response
    
    return app


def run_app(config_name='default', host='0.0.0.0', port=5000, debug=None):
    """运行应用"""
    app = create_app(config_name)
    
    if debug is None:
        debug = config[config_name].DEBUG
    
    logger.info(f"启动Spark AI API服务器...")
    logger.info(f"配置环境: {config_name}")
    logger.info(f"监听地址: {host}:{port}")
    logger.info(f"调试模式: {debug}")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    import sys
    
    # 支持命令行参数
    config_name = sys.argv[1] if len(sys.argv) > 1 else 'default'
    run_app(config_name)