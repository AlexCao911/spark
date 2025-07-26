# Spark AI Flask API

这是Spark AI视频生成聊天机器人的Flask后端API，提供RESTful接口供前端调用。

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements_api.txt
```

### 启动服务器

```bash
# 开发环境
python run_api.py --config development

# 生产环境
python run_api.py --config production --host 0.0.0.0 --port 8000

# 查看帮助
python run_api.py --help
```

### 访问API

- **API文档**: http://localhost:5000/api/docs
- **健康检查**: http://localhost:5000/api/health
- **会话信息**: http://localhost:5000/api/session/info

## 📚 API接口文档

### 聊天接口

#### 发送消息
```http
POST /api/chat/send
Content-Type: application/json

{
  "message": "我想制作一个科幻视频",
  "is_first_message": true
}
```

响应：
```json
{
  "status": "engaged",
  "response": "很棒的想法！科幻视频有很多可能性...",
  "is_complete": false,
  "missing_elements": ["characters", "plot"],
  "session_id": "uuid",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### 获取聊天历史
```http
GET /api/chat/history
```

#### 重置聊天会话
```http
POST /api/chat/reset
```

### 内容生成接口

#### 结构化用户创意
```http
POST /api/content/structure
```

#### 生成故事大纲
```http
POST /api/content/story/generate
Content-Type: application/json

{
  "user_idea": {
    "theme": "太空冒险",
    "genre": "科幻",
    "target_audience": "成年人",
    "duration_preference": 180,
    "basic_characters": ["宇航员", "AI助手"],
    "plot_points": ["发现信号", "太空旅行", "外星接触"],
    "visual_style": "电影级",
    "mood": "紧张刺激"
  }
}
```

#### 生成角色档案
```http
POST /api/content/characters/generate
Content-Type: application/json

{
  "user_idea": { ... }
}
```

### 项目管理接口

#### 获取项目列表
```http
GET /api/projects?page=1&per_page=10&status=approved
```

#### 创建项目（确认内容）
```http
POST /api/projects
Content-Type: application/json

{
  "user_idea": { ... },
  "story_outline": { ... },
  "character_profiles": [ ... ],
  "project_name": "我的科幻项目"
}
```

#### 获取特定项目
```http
GET /api/projects/{project_id}
```

#### 删除项目
```http
DELETE /api/projects/{project_id}
```

#### 搜索项目
```http
GET /api/projects/search?q=科幻
```

#### 导出项目
```http
GET /api/projects/{project_id}/export?format=json
```

#### 重新生成角色图片
```http
POST /api/projects/{project_id}/characters/{character_name}/regenerate
Content-Type: application/json

{
  "feedback": "让角色看起来更年轻一些"
}
```

## 🔧 配置

### 环境配置

- **development**: 开发环境，启用调试模式
- **production**: 生产环境，优化性能和安全性
- **testing**: 测试环境，用于单元测试

### 配置文件

配置在 `src/spark/api/config.py` 中定义：

```python
class DevelopmentConfig(Config):
    DEBUG = True
    CORS_ORIGINS = ['*']  # 开发环境允许所有来源

class ProductionConfig(Config):
    DEBUG = False
    CORS_ORIGINS = ['https://your-domain.com']  # 生产环境限制来源
    SESSION_TYPE = 'redis'  # 使用Redis存储session
```

### 环境变量

```bash
# 必需
SECRET_KEY=your-secret-key-here

# 可选
REDIS_URL=redis://localhost:6379  # 生产环境Redis URL
```

## 🧪 测试

```bash
# 运行所有API测试
python -m pytest tests/test_api.py -v

# 运行特定测试
python -m pytest tests/test_api.py::TestChatAPI::test_send_message_success -v
```

## 📦 部署

### 使用Gunicorn（推荐生产环境）

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:8000 "src.spark.api.app:create_app('production')"
```

### 使用Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt

COPY . .

EXPOSE 5000
CMD ["python", "run_api.py", "--config", "production", "--host", "0.0.0.0"]
```

### 使用systemd服务

```ini
[Unit]
Description=Spark AI API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/spark
ExecStart=/path/to/venv/bin/python run_api.py --config production
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔒 安全考虑

1. **CORS配置**: 生产环境限制允许的来源域名
2. **Session安全**: 使用安全的SECRET_KEY
3. **输入验证**: 所有输入都经过验证
4. **错误处理**: 不暴露敏感的错误信息
5. **日志记录**: 记录所有请求和错误

## 📊 监控和日志

### 日志配置

日志记录在控制台和文件中：

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 健康检查

```bash
curl http://localhost:5000/api/health
```

### 性能监控

可以集成APM工具如New Relic、DataDog等：

```python
# 示例：集成New Relic
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

@newrelic.agent.wsgi_application()
def application(environ, start_response):
    return app(environ, start_response)
```

## 🔄 API版本管理

当前版本：v1.0.0

未来版本可以通过URL前缀管理：
- `/api/v1/...` - 版本1
- `/api/v2/...` - 版本2

## 🤝 开发指南

### 添加新接口

1. 在相应的蓝图文件中添加路由
2. 添加相应的测试
3. 更新API文档

### 错误处理

使用统一的错误响应格式：

```json
{
  "error": "错误类型",
  "message": "详细错误信息",
  "timestamp": "2024-01-01T00:00:00"
}
```

### 响应格式

成功响应格式：

```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2024-01-01T00:00:00"
}
```

## 📞 支持

如有问题，请查看：

1. API文档：`/api/docs`
2. 健康检查：`/api/health`
3. 日志文件
4. 测试用例

## 🎯 路线图

- [ ] 添加用户认证和授权
- [ ] 实现API限流
- [ ] 添加缓存机制
- [ ] 支持WebSocket实时通信
- [ ] 集成更多AI模型
- [ ] 添加批量操作接口