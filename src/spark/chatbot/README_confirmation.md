# 用户确认系统

这是一个简化的用户确认系统，用于在chatbot生成story outline和角色档案后，让用户确认并保存这些数据。

## 系统架构

### 核心组件

1. **SimpleConfirmationManager** (`simple_confirmation.py`)
   - 负责保存、加载、管理用户确认的内容
   - 提供项目管理功能（列表、删除等）
   - 支持角色图片重新生成请求

2. **ConfirmationGradioInterface** (`confirmation_interface.py`)
   - 扩展的Gradio界面，集成确认功能
   - 提供完整的工作流程：聊天 → 生成 → 确认 → 保存
   - 包含项目管理界面

## 工作流程

```
1. 用户在chatbot中描述视频创意
   ↓
2. 系统结构化用户创意
   ↓
3. 生成故事大纲和角色档案
   ↓
4. 用户查看并确认内容
   ↓
5. 系统保存确认的数据到项目文件
```

## 数据存储结构

每个确认的项目会在 `projects/` 目录下创建一个子目录，包含：

```
projects/
└── {project_id}/
    ├── approved_content.json    # 完整的确认内容
    ├── story_outline.json       # 故事大纲
    ├── characters.json          # 角色档案
    └── character_images.json    # 角色图片信息（如果有）
```

### approved_content.json 结构

```json
{
  "project_id": "uuid",
  "project_name": "项目名称",
  "created_at": "2024-01-01T00:00:00",
  "user_idea": { ... },
  "story_outline": { ... },
  "character_profiles": [ ... ],
  "status": "approved",
  "user_confirmed": true
}
```

## 使用方法

### 1. 编程方式使用

```python
from src.spark.chatbot.simple_confirmation import confirmation_manager
from src.spark.models import UserIdea, StoryOutline, CharacterProfile

# 保存确认内容
result = confirmation_manager.save_approved_content(
    user_idea=user_idea,
    story_outline=story_outline,
    character_profiles=character_profiles,
    project_name="我的项目"
)

# 加载项目
project_data = confirmation_manager.load_approved_content(project_id)

# 列出所有项目
projects = confirmation_manager.list_projects()

# 删除项目
confirmation_manager.delete_project(project_id)
```

### 2. Gradio界面使用

```python
from src.spark.chatbot.confirmation_interface import launch_confirmation_interface

# 启动完整的确认界面
launch_confirmation_interface()
```

### 3. 运行演示

```bash
# 运行演示脚本
python demo_confirmation_system.py

# 启动Gradio界面
python -m src.spark.chatbot.confirmation_interface
```

## 功能特性

### ✅ 已实现功能

1. **内容确认**
   - 故事大纲确认
   - 角色档案确认
   - 用户反馈收集

2. **数据存储**
   - JSON格式存储
   - 项目目录管理
   - 自动生成项目ID

3. **项目管理**
   - 项目列表查看
   - 项目加载
   - 项目删除

4. **Gradio界面**
   - 完整工作流程界面
   - 实时状态更新
   - 项目管理界面

5. **角色图片管理**
   - 重新生成请求记录
   - 反馈处理

### 🔄 可扩展功能

1. **图片重新生成**
   - 集成实际的图片生成API
   - 基于用户反馈的智能修改

2. **内容编辑**
   - 在线编辑故事大纲
   - 角色档案修改

3. **导出功能**
   - 导出为不同格式（PDF、Word等）
   - 批量导出

4. **版本管理**
   - 内容版本历史
   - 回滚功能

## 测试

```bash
# 运行所有测试
python -m pytest tests/test_simple_confirmation.py -v

# 运行界面测试
python -m pytest tests/test_confirmation_interface.py -v

# 运行演示
python demo_confirmation_system.py
```

## 配置

系统使用 `src/spark/config.py` 中的配置：

- `PROJECTS_STORAGE_PATH`: 项目存储路径（默认: "projects"）
- `ENABLE_AUTO_SAVE`: 是否启用自动保存（默认: True）
- `MAX_PROJECTS`: 最大项目数量（默认: 100）

## 错误处理

系统包含完善的错误处理机制：

1. **文件操作错误**: 自动创建目录，处理权限问题
2. **数据验证错误**: 验证输入数据的完整性
3. **API错误**: 优雅处理外部API调用失败
4. **用户输入错误**: 提供清晰的错误提示

## 日志记录

系统使用Python标准logging模块记录操作日志：

- 成功操作记录为INFO级别
- 错误记录为ERROR级别
- 警告记录为WARNING级别

## 安全考虑

1. **输入验证**: 所有用户输入都经过验证
2. **路径安全**: 防止路径遍历攻击
3. **数据清理**: 自动清理过期或无效数据

## 性能优化

1. **延迟加载**: 只在需要时加载项目数据
2. **缓存机制**: 缓存常用的项目列表
3. **异步处理**: 支持异步操作（可扩展）

这个简化的确认系统提供了核心的用户确认和数据存储功能，同时保持了代码的简洁性和可维护性。