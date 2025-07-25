"""
Flask API测试
"""

import pytest
import json
from src.spark.api.app import create_app


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


class TestHealthAPI:
    """健康检查API测试"""
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data


class TestSessionAPI:
    """会话API测试"""
    
    def test_session_info(self, client):
        """测试获取会话信息"""
        response = client.get('/api/session/info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'session_id' in data
        assert data['status'] == 'active'
        assert 'timestamp' in data


class TestChatAPI:
    """聊天API测试"""
    
    def test_send_message_missing_data(self, client):
        """测试发送消息 - 缺少数据"""
        response = client.post('/api/chat/send')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_send_message_empty_message(self, client):
        """测试发送消息 - 空消息"""
        response = client.post('/api/chat/send', 
                             json={'message': ''})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_send_message_success(self, client):
        """测试发送消息 - 成功"""
        response = client.post('/api/chat/send', 
                             json={
                                 'message': '我想制作一个科幻视频',
                                 'is_first_message': True
                             })
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'response' in data
        assert 'session_id' in data
        assert 'timestamp' in data
    
    def test_get_chat_history(self, client):
        """测试获取聊天历史"""
        # 先发送一条消息
        client.post('/api/chat/send', 
                   json={
                       'message': '测试消息',
                       'is_first_message': True
                   })
        
        # 获取历史
        response = client.get('/api/chat/history')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'history' in data
        assert 'session_id' in data
        assert 'context' in data
    
    def test_reset_chat(self, client):
        """测试重置聊天"""
        response = client.post('/api/chat/reset')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'session_id' in data


class TestContentAPI:
    """内容生成API测试"""
    
    def test_structure_idea_no_history(self, client):
        """测试结构化创意 - 没有对话历史"""
        response = client.post('/api/content/structure')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_generate_story_missing_data(self, client):
        """测试生成故事大纲 - 缺少数据"""
        response = client.post('/api/content/story/generate')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_generate_characters_missing_data(self, client):
        """测试生成角色 - 缺少数据"""
        response = client.post('/api/content/characters/generate')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data


class TestProjectsAPI:
    """项目管理API测试"""
    
    def test_list_projects(self, client):
        """测试获取项目列表"""
        response = client.get('/api/projects')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'projects' in data
        assert 'pagination' in data
    
    def test_get_project_not_found(self, client):
        """测试获取不存在的项目"""
        response = client.get('/api/projects/non-existent-id')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_delete_project_not_found(self, client):
        """测试删除不存在的项目"""
        response = client.delete('/api/projects/non-existent-id')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data or data['status'] == 'error'
    
    def test_search_projects_no_query(self, client):
        """测试搜索项目 - 没有查询"""
        response = client.get('/api/projects/search')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_search_projects_with_query(self, client):
        """测试搜索项目 - 有查询"""
        response = client.get('/api/projects/search?q=test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'results' in data
        assert data['query'] == 'test'


class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_error(self, client):
        """测试404错误"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_405_error(self, client):
        """测试405错误"""
        response = client.put('/api/health')  # health只支持GET
        assert response.status_code == 405
        
        data = json.loads(response.data)
        assert 'error' in data


class TestAPIDocumentation:
    """API文档测试"""
    
    def test_api_docs(self, client):
        """测试API文档"""
        response = client.get('/api/docs')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'title' in data
        assert 'version' in data
        assert 'endpoints' in data
        assert 'chat' in data['endpoints']
        assert 'content' in data['endpoints']
        assert 'projects' in data['endpoints']