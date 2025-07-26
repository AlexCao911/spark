# VEO 3.0 API迁移指南

## 概述

本项目已从Google Cloud Vertex AI迁移到Google AI Gemini API，以便更简单地使用VEO 3.0视频生成功能。

## 主要变化

### 1. API端点变更
- **之前**: Google Cloud Vertex AI
  ```
  https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/veo-3.0-generate-preview:predict
  ```
- **现在**: Google AI Gemini API
  ```
  https://generativelanguage.googleapis.com/v1beta/models/veo-3.0-generate:generateContent
  ```

### 2. 认证方式简化
- **之前**: 需要Google Cloud项目、服务账户或gcloud认证
- **现在**: 只需要Google AI API密钥

### 3. 配置简化
- **之前**: 需要配置项目ID、区域、认证等多个参数
- **现在**: 只需要配置API密钥

## 迁移步骤

### 1. 获取新的API密钥
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 创建新的API密钥
3. 复制API密钥

### 2. 更新环境配置
更新`.env`文件：
```env
# 新的配置
VIDEO_GENERATE_API_KEY=your_google_ai_api_key
VEO3_MOCK_MODE=false

# 旧的配置（可以删除或注释）
# GOOGLE_CLOUD_PROJECT_ID=central-diode-467003-e0
# GOOGLE_CLOUD_LOCATION=us-central1
```

### 3. 运行配置向导
```bash
python configure_veo3.py
```

### 4. 测试新配置
```bash
# 简单测试
python test_gemini_veo3.py

# 完整测试
python test_veo3_vertex_ai.py
```

## 代码变化

### VEO3RealTool类的主要变化

1. **初始化简化**:
   ```python
   # 之前
   self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
   self.location = os.getenv('GOOGLE_CLOUD_LOCATION')
   self.generate_url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/..."
   
   # 现在
   self.base_url = "https://generativelanguage.googleapis.com/v1beta"
   self.generate_url = f"{self.base_url}/models/veo-3.0-generate:generateContent"
   ```

2. **认证简化**:
   ```python
   # 之前
   def _get_access_token(self):
       # 复杂的gcloud认证逻辑
   
   # 现在
   def _get_api_key(self):
       return self.api_key
   ```

3. **请求格式更新**:
   ```python
   # 之前 (Vertex AI格式)
   payload = {
       "instances": [{
           "prompt": {"parts": prompt_parts},
           "generation_config": {...}
       }]
   }
   
   # 现在 (Gemini API格式)
   payload = {
       "contents": [{"parts": prompt_parts}],
       "generationConfig": {...}
   }
   ```

## 兼容性

### 向后兼容
- 所有现有的接口和方法保持不变
- VideoPrompt模型无需修改
- 上层应用代码无需修改

### 功能对等
- 支持文本提示词生成视频
- 支持参考图像
- 支持自定义生成参数
- 支持状态查询和进度跟踪

## 优势

### 1. 配置简化
- 无需Google Cloud项目设置
- 无需复杂的认证配置
- 只需一个API密钥即可开始

### 2. 部署简化
- 无需gcloud CLI
- 无需服务账户管理
- 更适合容器化部署

### 3. 开发体验改善
- 更快的设置时间
- 更少的依赖项
- 更清晰的错误信息

## 故障排除

### 1. API密钥问题
```bash
# 检查API密钥配置
python -c "import os; print(os.getenv('VIDEO_GENERATE_API_KEY', 'Not found'))"

# 测试API连接
python test_gemini_veo3.py
```

### 2. 模型访问权限
如果遇到模型不可用的问题：
1. 检查VEO 3.0是否需要特殊访问权限
2. 访问Google AI文档获取最新信息
3. 尝试申请访问权限

### 3. 配额限制
- 在Google AI Studio中监控API使用情况
- 考虑升级到付费计划
- 实施适当的请求限流

## 测试

### 可用的测试脚本
1. `test_gemini_veo3.py` - 专门测试新的Gemini API
2. `test_veo3_vertex_ai.py` - 更新后的完整测试
3. `test_veo3_simple.py` - 基础功能测试

### 测试覆盖
- API连接测试
- 模型列表查询
- 文本生成测试
- 视频生成请求测试
- 图像到视频测试
- 工具集成测试

## 支持

如果遇到问题：
1. 查看测试脚本的详细输出
2. 检查Google AI Studio中的API状态
3. 参考最新的Google AI文档
4. 检查项目的错误日志

## 相关资源

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API文档](https://ai.google.dev/gemini-api/docs)
- [视频生成文档](https://ai.google.dev/gemini-api/docs/video)
- [API密钥管理](https://aistudio.google.com/app/apikey)