# VEO 3.0 设置指南

本指南将帮助您配置VEO 3.0视频生成API，从模拟模式切换到真实API调用。

## 概述

VEO 3.0是Google的最新视频生成模型，现在通过Google AI Gemini API提供服务。本项目支持两种模式：
- **模拟模式**: 用于开发和测试，生成模拟视频文件
- **真实模式**: 调用实际的VEO 3.0 Gemini API生成视频

## 前置要求

1. **Google账户**: 需要有效的Google账户
2. **API访问权限**: 需要申请VEO 3.0访问权限
3. **API密钥**: 从Google AI Studio获取API密钥
4. **Google AI SDK**: 推荐安装以获得最佳体验

## 快速开始

### 1. 运行配置向导

```bash
python configure_veo3.py
```

配置向导将引导您完成以下步骤：
- 检查网络连接
- 配置API密钥
- 测试API连接
- 验证配置

### 2. 手动配置步骤

如果您更喜欢手动配置，请按照以下步骤：

#### 步骤1: 获取API密钥

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 登录您的Google账户
3. 创建新的API密钥
4. 复制API密钥

#### 步骤2: 安装Google AI SDK（推荐）

```bash
pip install google-generativeai
```

#### 步骤3: 配置环境变量

创建或更新`.env`文件：

```env
# Google AI API密钥
VIDEO_GENERATE_API_KEY=your_google_ai_api_key_here

# 模式设置
VEO3_MOCK_MODE=false
```

#### 步骤4: 测试配置

```bash
# 测试SDK方式（推荐）
python test_veo3_sdk.py

# 或测试REST API方式
python test_veo3_simple.py
```

## API密钥配置

### 获取API密钥

1. **访问Google AI Studio**:
   - 打开 https://aistudio.google.com/app/apikey
   - 使用Google账户登录

2. **创建API密钥**:
   - 点击"Create API Key"
   - 选择项目（或创建新项目）
   - 复制生成的API密钥

3. **配置环境变量**:
   ```env
   VIDEO_GENERATE_API_KEY=AIza...your_api_key_here
   VEO3_MOCK_MODE=false
   ```

### API密钥安全

- **不要提交到版本控制**: 确保`.env`文件在`.gitignore`中
- **限制API密钥权限**: 在Google AI Studio中设置适当的限制
- **定期轮换**: 定期更新API密钥
- **监控使用情况**: 在Google AI Studio中监控API使用情况

## VEO 3.0访问权限

VEO 3.0可能需要特殊访问权限：

1. **检查模型可用性**:
   ```bash
   python test_veo3_simple.py
   ```

2. **申请访问权限**:
   - 如果VEO模型不可用，可能需要申请访问权限
   - 访问 [Google AI文档](https://ai.google.dev/gemini-api/docs/video)
   - 按照说明申请访问权限

## 测试配置

### 运行简单测试

```bash
python test_veo3_simple.py
```

这个测试会：
- 检查API密钥配置
- 测试Gemini API连接
- 查找可用的VEO模型
- 尝试发送视频生成请求

### 运行完整测试

```bash
python test_veo3_vertex_ai.py
```

### 测试完整管道

```bash
python test_complete_pipeline.py
```

## API使用说明

### SDK方式（推荐）

```python
import google.generativeai as genai
from google.generativeai import types

# 配置API密钥
genai.configure(api_key="your_api_key")

# 创建客户端
client = genai.Client()

# 配置生成参数
config = types.GenerateVideosConfig(
    negative_prompt="cartoon, drawing, low quality",
    duration_seconds=3,
    aspect_ratio="16:9"
)

# 生成视频
operation = client.models.generate_videos(
    model="veo-3.0-generate-preview",
    prompt="一朵白云在蓝天中缓缓飘过，阳光明媚，画面清新自然",
    config=config
)

print(f"任务ID: {operation.name}")
```

### REST API方式（备用）

```python
import requests

api_key = "your_api_key"
url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.0-generate:generateContent?key={api_key}"

payload = {
    "contents": [{
        "parts": [{
            "text": "一朵白云在蓝天中缓缓飘过，阳光明媚，画面清新自然，电影级画质"
        }]
    }],
    "generationConfig": {
        "temperature": 0.7,
        "topK": 40,
        "topP": 0.95,
        "maxOutputTokens": 8192
    }
}

response = requests.post(url, json=payload)
```

### 添加参考图像

```python
import base64

# 读取图像文件
with open("reference_image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

payload = {
    "contents": [{
        "parts": [
            {"text": "基于这张图像生成视频"},
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            }
        ]
    }]
}
```

## 常见问题

### 1. API密钥无效

**问题**: API返回401认证错误

**解决方案**:
- 检查API密钥是否正确复制
- 确认API密钥没有过期
- 在Google AI Studio中检查密钥状态

### 2. 模型不可用

**问题**: 找不到VEO模型

**解决方案**:
- VEO 3.0可能需要特殊访问权限
- 检查Google AI文档获取最新信息
- 尝试申请访问权限

### 3. 配额限制

**问题**: API调用超出配额

**解决方案**:
- 在Google AI Studio中检查配额使用情况
- 考虑升级到付费计划
- 优化API调用频率

### 4. 网络连接问题

**问题**: 无法连接到API

**解决方案**:
- 检查网络连接
- 确认防火墙设置
- 尝试使用代理

### 5. 响应格式问题

**问题**: 无法解析API响应

**解决方案**:
- 检查API文档获取最新响应格式
- 查看完整的响应内容进行调试
- 更新代码以处理新的响应格式

## 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `VIDEO_GENERATE_API_KEY` | Google AI API密钥 | 无 | 是 |
| `VEO3_MOCK_MODE` | 是否使用模拟模式 | `true` | 否 |

## 生产部署建议

1. **API密钥管理**: 使用安全的密钥管理系统
2. **错误处理**: 实现完善的错误处理和重试机制
3. **配额监控**: 监控API使用情况和配额
4. **缓存策略**: 实现适当的缓存机制
5. **日志记录**: 记录API调用日志用于调试

## 支持

如果遇到问题：

1. 运行测试脚本查看详细错误信息
2. 检查Google AI Studio中的API使用情况
3. 查看Google AI文档获取最新信息
4. 检查项目的错误日志

## 相关链接

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API文档](https://ai.google.dev/gemini-api/docs)
- [视频生成文档](https://ai.google.dev/gemini-api/docs/video)
- [API密钥管理](https://aistudio.google.com/app/apikey)

## 📝 需要你提供的具体信息

请提供以下信息以完成配置：

### 1. Google AI API密钥
```
API密钥: _______________
```

### 2. VEO 3.0访问状态
```
是否已申请VEO 3.0访问: [ ] 是 [ ] 否
申请状态: [ ] 已批准 [ ] 等待中 [ ] 未申请
```

### 3. 预期使用量
```
预期每日视频生成数量: _______________
视频平均时长: _______________秒
```

## 🚀 配置完成后

配置完成后，运行以下命令测试完整管道：

```bash
# 设置为真实模式
export VEO3_MOCK_MODE=false

# 测试VEO 3.0 API
python test_veo3_simple.py

# 测试完整管道
python test_complete_pipeline.py

# 启动API服务器
python run_api.py
```

---

**请提供上述信息，我将帮助你完成VEO 3.0的真实API配置！** 🎬