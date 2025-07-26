"""
聊天相关的API路由
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import logging
import uuid

from ...chatbot.core import ChatbotCore

logger = logging.getLogger(__name__)

# 创建蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# 全局chatbot实例
chatbot_core = ChatbotCore()


def get_session_id():
    """获取或创建会话ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


def get_chatbot_for_session(session_id):
    """为会话获取chatbot实例"""
    # 这里可以实现会话隔离，暂时使用全局实例
    return chatbot_core


@chat_bp.route('/send', methods=['POST'])
def send_message():
    """发送消息到聊天机器人"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': '缺少消息内容'}), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({'error': '消息不能为空'}), 400
        
        session_id = get_session_id()
        chatbot = get_chatbot_for_session(session_id)
        
        # 检查是否是第一条消息
        is_first_message = data.get('is_first_message', False)
        
        if is_first_message:
            response_data = chatbot.engage_user(message)
        else:
            response_data = chatbot.continue_conversation(message)
        
        # 添加会话信息
        response_data['session_id'] = session_id
        response_data['timestamp'] = datetime.now().isoformat()
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"发送消息时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'response': '处理消息时出现错误，请稍后重试'
        }), 500


@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    """获取聊天历史"""
    try:
        session_id = get_session_id()
        chatbot = get_chatbot_for_session(session_id)
        
        history = chatbot.get_conversation_history()
        context = chatbot.get_conversation_context()
        
        return jsonify({
            'session_id': session_id,
            'history': history,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取聊天历史时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/reset', methods=['POST'])
def reset_chat():
    """重置聊天会话"""
    try:
        session_id = get_session_id()
        chatbot = get_chatbot_for_session(session_id)
        
        chatbot.reset_conversation()
        
        return jsonify({
            'status': 'success',
            'message': '会话已重置',
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"重置会话时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/status', methods=['GET'])
def get_chat_status():
    """获取聊天状态"""
    try:
        session_id = get_session_id()
        chatbot = get_chatbot_for_session(session_id)
        
        context = chatbot.get_conversation_context()
        
        return jsonify({
            'session_id': session_id,
            'status': 'active',
            'message_count': context.get('message_count', 0),
            'last_analysis': context.get('last_analysis', {}),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取聊天状态时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500