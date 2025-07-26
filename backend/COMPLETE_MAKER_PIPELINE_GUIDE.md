# Maker Crew 完整视频生成流水线使用指南

## 概述

这个完整的Maker Crew流水线实现了从项目提取视频提示词到生成视频片段再到剪辑成长视频的完整流程。

## 流程架构

```
项目数据 → 提取提示词 → 生成视频片段 → 拼接最终视频
    ↓           ↓            ↓            ↓
projects/   video_prompts   VEO3生成     视频编辑
projects/   .json文件      多个MP4片段    最终MP4视频
```

## 核心组件

### 1. CompleteMakerPipeline 主流水线类
- `extract_project_prompts()` - 从项目中提取视频提示词
- `generate_video_clips()` - 使用VEO3生成视频片段
- `assemble_final_video()` - 拼接最终视频
- `run_complete_pipeline()` - 运行完整流程

### 2. 工具集成
- **VEO3RealTool** - 真实的VEO3 API调用
- **VideoGenerationTool** - CrewAI视频生成工具
- **VideoEditingTool** - 视频编辑和拼接工具

### 3. 数据模型
- **VideoPrompt** - 视频提示词模型
- **VideoClip** - 视频片段信息模型

## 使用方法

### 快速开始

1. **运行完整流水线**
```bash
python complete_maker_pipeline.py
```

2. **选择项目**
程序会自动扫描 `projects/projects/` 目录下的项目，选择一个包含 `scripts/video_prompts.json` 的项目。

3. **输入视频标题**
为最终生成的视频输入标题（可选）。

4. **等待处理完成**
流水线会自动执行所有步骤并显示进度。

### 测试和演示

1. **快速演示**
```bash
python test_complete_pipeline.py demo
```

2. **运行测试套件**
```bash
python test_complete_pipeline.py test
```

## 项目结构要求

你的项目需要按以下结构组织：

```
projects/projects/
└── your_project_id/
    └── scripts/
        └── video_prompts.json  # 必需的提示词文件
```

### video_prompts.json 格式

```json
[
  {
    "shot_id": 1,
    "veo3_prompt": "A beautiful sunrise over mountains, cinematic shot",
    "duration": 5,
    "character_reference_images": ["url1", "url2"]
  },
  {
    "shot_id": 2,
    "veo3_prompt": "A peaceful lake with reflections, nature style",
    "duration": 5,
    "character_reference_images": []
  }
]
```

## 输出结果

### 生成的文件结构

```
projects/projects/your_project_id/
├── videos/                    # 视频片段目录
│   ├── shot_001.mp4          # 生成的视频片段
│   ├── shot_002.mp4
│   └── production_summary.json
└── final_videos/              # 最终视频目录
    ├── Your_Video_HQ.mp4     # 高质量版本
    ├── Your_Video_Web.mp4    # 网络优化版本
    ├── Your_Video_Mobile.mp4 # 移动版本
    └── Your_Video_thumbnail.jpg # 缩略图
```

### 输出版本说明

1. **高质量版本** (HQ) - 5000k码率，适合下载和存档
2. **网络优化版本** (Web) - 2000k码率，适合在线播放
3. **移动版本** (Mobile) - 1000k码率，720p分辨率，适合移动设备

## 配置要求

### 环境变量

在 `.env` 文件中设置：

```env
VIDEO_GENERATE_API_KEY=your_veo3_api_key
VEO3_MOCK_MODE=false  # 设为true使用模拟模式
OPENAI_API_KEY=your_openai_key  # 用于CrewAI
```

### 依赖安装

```bash
pip install -r requirements_api.txt
```

主要依赖：
- `google-generativeai` - VEO3 API
- `crewai` - CrewAI框架
- `moviepy` - 视频编辑
- `ffmpeg-python` - 视频处理

## 流程详解

### 步骤1: 提取项目提示词

```python
video_prompts = pipeline.extract_project_prompts(project_id)
```

- 从 `projects/projects/{project_id}/scripts/video_prompts.json` 读取数据
- 转换为标准的VideoPrompt格式
- 按shot_id排序确保正确顺序

### 步骤2: 生成视频片段

```python
video_clips = pipeline.generate_video_clips(project_id, video_prompts)
```

- 为每个提示词调用VEO3 API
- 实现重试机制和错误处理
- 下载生成的视频到本地
- 保存到 `projects/projects/{project_id}/videos/` 目录

### 步骤3: 拼接最终视频

```python
final_result = pipeline.assemble_final_video(project_id, video_clips, video_title)
```

- 验证视频片段文件
- 使用MoviePy或FFmpeg拼接
- 添加转场效果（淡入淡出）
- 生成多种格式和分辨率
- 创建缩略图

## 错误处理

### 常见问题和解决方案

1. **API密钥问题**
   - 检查 `.env` 文件中的 `VIDEO_GENERATE_API_KEY`
   - 确保API密钥有效且有足够配额

2. **项目文件不存在**
   - 确保项目目录结构正确
   - 检查 `video_prompts.json` 文件格式

3. **视频生成失败**
   - 检查网络连接
   - 验证提示词内容是否符合VEO3要求
   - 查看控制台错误信息

4. **视频拼接失败**
   - 确保MoviePy或FFmpeg正确安装
   - 检查视频片段文件是否完整
   - 验证磁盘空间是否充足

### 模拟模式

如果VEO3 API不可用，可以启用模拟模式：

```env
VEO3_MOCK_MODE=true
```

模拟模式会：
- 生成测试视频文件
- 模拟API响应
- 允许测试完整流程

## 性能优化

### 并发处理

当前实现是串行处理，可以通过以下方式优化：

1. **并行生成视频片段**
```python
# 使用线程池或异步处理
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(generate_clip, prompt) for prompt in prompts]
```

2. **批量状态检查**
```python
# 批量检查多个生成任务的状态
def check_multiple_jobs(job_ids):
    # 实现批量状态检查
    pass
```

### 缓存机制

1. **片段缓存** - 避免重复生成相同提示词的视频
2. **状态缓存** - 缓存生成状态避免频繁API调用

## 扩展功能

### 自定义转场效果

```python
# 在VideoEditingTool中添加更多转场效果
def add_custom_transitions(clips):
    # 实现自定义转场
    pass
```

### 音频处理

```python
# 添加背景音乐和音效
def add_background_audio(video_path, audio_path):
    # 实现音频混合
    pass
```

### 字幕生成

```python
# 自动生成字幕
def generate_subtitles(video_prompts):
    # 基于提示词生成字幕
    pass
```

## 监控和日志

### 日志配置

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maker_pipeline.log'),
        logging.StreamHandler()
    ]
)
```

### 进度跟踪

流水线提供详细的进度信息：
- 当前处理的镜头
- 生成进度百分比
- 预计剩余时间
- 成功/失败统计

## 最佳实践

1. **提示词优化**
   - 使用具体、描述性的提示词
   - 包含视觉风格和技术要求
   - 保持角色和场景的一致性

2. **资源管理**
   - 定期清理临时文件
   - 监控磁盘空间使用
   - 合理设置并发数量

3. **质量控制**
   - 验证生成的视频片段质量
   - 检查音视频同步
   - 确保转场效果自然

4. **备份策略**
   - 备份重要的项目数据
   - 保存生成配置和参数
   - 记录成功的提示词模板

## 故障排除

### 调试模式

启用详细日志：
```python
pipeline = CompleteMakerPipeline()
pipeline.debug_mode = True
```

### 手动干预

如果自动流程失败，可以手动执行各个步骤：

```python
# 手动提取提示词
prompts = pipeline.extract_project_prompts("project_id")

# 手动生成单个片段
clip = pipeline.generate_single_clip(prompt)

# 手动拼接视频
result = pipeline.assemble_final_video(project_id, clips)
```

## 支持和反馈

如果遇到问题或有改进建议，请：

1. 检查日志文件获取详细错误信息
2. 验证环境配置和依赖安装
3. 尝试使用模拟模式测试流程
4. 查看示例项目和测试用例

---

*最后更新: 2025年1月*