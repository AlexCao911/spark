# Spark AI 视频生成管道

## 概述

Spark AI 视频生成管道是一个完整的AI驱动视频制作系统，能够将用户的创意想法转换为专业质量的视频内容。

## 架构

### 1. 完整流程

```
用户创意 → 聊天机器人交互 → 故事大纲 → 角色生成 → 用户确认 → 脚本生成 → 视频制作 → 最终视频
```

### 2. 主要组件

- **聊天机器人模块** (`src/spark/chatbot/`): 用户交互和创意收集
- **确认系统** (`src/spark/chatbot/confirmation_interface.py`): 用户确认和反馈处理
- **脚本生成团队** (`src/spark/crews/script/`): 使用CrewAI生成详细故事和视频提示词
- **视频制作团队** (`src/spark/crews/maker/`): 使用VEO3生成视频片段并拼接
- **视频生成管道** (`src/spark/video_generation_pipeline.py`): 整合所有组件的主管道
- **Flask API** (`src/spark/api/`): RESTful API接口

## 使用方法

### 1. 环境配置

确保 `.env` 文件包含必要的API密钥：

```bash
# VEO3视频生成
VIDEO_GENERATE_API_KEY=your_veo3_api_key

# 脚本生成（Qwen3）
DETAILED_STORY_API_KEY=your_qwen3_api_key
DASHSCOPE_API_KEY=your_dashscope_api_key

# 聊天机器人（GPT-4o）
CHATBOT_API_KEY=your_gpt4o_api_key

# 图像生成
IMAGE_GEN_API_KEY=your_image_gen_api_key
```

### 2. 启动API服务器

```bash
python run_api.py
```

服务器将在 `http://localhost:5000` 启动。

### 3. API端点

#### 视频生成相关

- `POST /api/video/generate` - 启动视频生成流程
- `GET /api/video/status/<job_id>` - 获取生成状态
- `GET /api/video/download/<project_id>/<video_type>` - 下载视频
- `GET /api/video/thumbnail/<project_id>` - 获取缩略图
- `GET /api/video/projects` - 列出所有项目
- `GET /api/video/project/<project_id>/status` - 获取项目状态

#### 使用示例

1. **启动视频生成**:
```bash
curl -X POST http://localhost:5000/api/video/generate \
  -H "Content-Type: application/json" \
  -d '{"project_id": "your_project_id"}'
```

2. **检查生成状态**:
```bash
curl http://localhost:5000/api/video/status/video_job_123456
```

3. **下载视频**:
```bash
curl http://localhost:5000/api/video/download/project_id/hq \
  -o video.mp4
```

### 4. 直接使用Python API

```python
from src.spark.video_generation_pipeline import video_pipeline

# 生成完整视频
result = video_pipeline.generate_complete_video("project_id")

# 检查项目状态
status = video_pipeline.get_project_status("project_id")

# 列出所有项目
projects = video_pipeline.list_available_projects()
```

## 技术规格

### 视频输出格式

- **高质量版本**: 1080p, H.264, 5000k bitrate
- **网络优化版本**: 1080p, H.264, 2000k bitrate  
- **移动版本**: 720p, H.264, 1000k bitrate

### 支持的功能

- ✅ 多语言支持（中文/英文）
- ✅ 角色一致性维护
- ✅ 专业电影级质量
- ✅ 自动重试和错误处理
- ✅ 进度跟踪
- ✅ 多格式输出
- ✅ 缩略图生成

## 测试

### 运行完整测试

```bash
python test_complete_pipeline.py
```

### 测试单个组件

```bash
# 测试脚本生成
python src/spark/crews/script/test_script_crew.py

# 测试视频制作
python src/spark/crews/maker/test_video_production.py
```

## 项目结构

```
src/spark/
├── chatbot/                    # 聊天机器人模块
├── crews/
│   ├── script/                 # 脚本生成团队
│   │   └── src/script/
│   │       ├── config/         # Agent和Task配置
│   │       ├── tools/          # 脚本生成工具
│   │       └── crew.py         # 主要crew实现
│   └── maker/                  # 视频制作团队
│       └── src/maker/
│           ├── config/         # Agent和Task配置
│           ├── tools/          # 视频生成和编辑工具
│           └── crew.py         # 主要crew实现
├── tools/
│   └── veo3_real_tool.py      # VEO3 API集成
├── api/
│   ├── routes/
│   │   └── video.py           # 视频API路由
│   └── app.py                 # Flask应用
├── video_generation_pipeline.py # 主管道
└── models.py                  # 数据模型
```

## 故障排除

### 常见问题

1. **API密钥错误**: 检查 `.env` 文件中的API密钥配置
2. **视频生成失败**: 检查VEO3 API配额和网络连接
3. **文件权限错误**: 确保项目目录有写入权限
4. **内存不足**: 视频处理需要足够的内存空间

### 日志查看

日志会输出到控制台，包含详细的错误信息和处理状态。

### 支持

如有问题，请检查：
1. API密钥是否正确配置
2. 网络连接是否正常
3. 项目文件是否完整
4. 依赖包是否正确安装

## 下一步开发

- [ ] 添加更多视频效果和转场
- [ ] 支持自定义音频
- [ ] 批量处理多个项目
- [ ] 视频质量优化
- [ ] 更多输出格式支持