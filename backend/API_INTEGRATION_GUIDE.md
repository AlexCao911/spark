# Spark AI 前端集成指南

本指南详细说明如何与Spark AI视频生成系统的后端API进行交互，实现聊天对话、获取故事大纲、角色图片和最终视频的功能。

## 🚀 快速开始

### 1. 启动API服务器

```bash
# 开发环境
python run_api.py --config development --host 0.0.0.0 --port 5000

# 生产环境
python run_api.py --config production --host 0.0.0.0 --port 8000
```

### 2. 测试API功能

```bash
# 运行集成测试
python test_api_integration.py

# 打开前端示例
open frontend_example.html
```

## 📚 核心API接口

### 基础配置

```javascript
const API_BASE = 'http://localhost:5000/api';

// 使用session支持
const session = {
    credentials: 'include',
    headers: {
        'Content-Type': 'application/json'
    }
};
```

## 1. 💬 聊天机器人对话

### 发送消息

```javascript
async function sendMessage(message, isFirstMessage = false) {
    const response = await fetch(`${API_BASE}/chat/send`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            is_first_message: isFirstMessage
        })
    });
    
    const data = await response.json();
    return data;
}

// 使用示例
const result = await sendMessage("我想制作一个科幻视频", true);
console.log(result.response); // 机器人回复
console.log(result.status);   // 对话状态
```

### 获取聊天历史

```javascript
async function getChatHistory() {
    const response = await fetch(`${API_BASE}/chat/history`, {
        credentials: 'include'
    });
    
    const data = await response.json();
    return data.history; // 聊天记录数组
}
```

### 重置聊天会话

```javascript
async function resetChat() {
    const response = await fetch(`${API_BASE}/chat/reset`, {
        method: 'POST',
        credentials: 'include'
    });
    
    return response.ok;
}
```

## 2. 📖 获取故事大纲

### 获取项目大纲

```javascript
async function getProjectOutline(projectId) {
    const response = await fetch(`${API_BASE}/content/project/${projectId}/outline`);
    const data = await response.json();
    
    if (response.ok) {
        return {
            title: data.outline.title,
            summary: data.outline.summary,
            narrative: data.outline.narrative_text,
            duration: data.outline.estimated_duration
        };
    }
    
    throw new Error(data.error);
}

// 使用示例
try {
    const outline = await getProjectOutline('project-id-here');
    console.log('标题:', outline.title);
    console.log('概要:', outline.summary);
    console.log('详细叙述:', outline.narrative);
    console.log('预计时长:', outline.duration, '秒');
} catch (error) {
    console.error('获取大纲失败:', error.message);
}
```

## 3. 👥 获取角色图片

### 获取项目所有角色

```javascript
async function getProjectCharacters(projectId) {
    const response = await fetch(`${API_BASE}/content/project/${projectId}/characters`);
    const data = await response.json();
    
    if (response.ok) {
        return data.characters.map(char => ({
            name: char.name,
            role: char.role,
            appearance: char.appearance,
            personality: char.personality,
            imageUrl: char.image_url,
            visualTags: char.visual_tags || []
        }));
    }
    
    throw new Error(data.error);
}

// 使用示例
try {
    const characters = await getProjectCharacters('project-id-here');
    
    characters.forEach(character => {
        console.log('角色名:', character.name);
        console.log('外观:', character.appearance);
        console.log('图片URL:', character.imageUrl);
        
        // 在页面中显示角色图片
        if (character.imageUrl) {
            const img = document.createElement('img');
            img.src = character.imageUrl;
            img.alt = character.name;
            document.body.appendChild(img);
        }
    });
} catch (error) {
    console.error('获取角色失败:', error.message);
}
```

### 获取单个角色图片信息

```javascript
async function getCharacterImage(projectId, characterName) {
    const response = await fetch(`${API_BASE}/content/project/${projectId}/character/${characterName}/image`);
    const data = await response.json();
    
    if (response.ok) {
        return {
            imageUrl: data.image_url,
            visualTags: data.visual_tags
        };
    }
    
    throw new Error(data.error);
}
```

## 4. 🎥 获取最终视频

### 获取项目视频信息

```javascript
async function getProjectVideos(projectId) {
    const response = await fetch(`${API_BASE}/video/project/${projectId}/videos`);
    const data = await response.json();
    
    if (response.ok) {
        return {
            hasVideos: data.video_info.has_videos,
            videoCount: data.video_info.video_count,
            videos: data.video_info.available_videos.map(video => ({
                type: video.type,           // 'hq', 'web', 'mobile', 'final'
                filename: video.filename,
                sizeMB: video.size_mb,
                downloadUrl: `${API_BASE}${video.download_url}`,
                streamUrl: `${API_BASE}${video.stream_url}`
            })),
            thumbnailUrl: data.video_info.thumbnail_url ? 
                `${API_BASE}${data.video_info.thumbnail_url}` : null
        };
    }
    
    throw new Error(data.error);
}

// 使用示例
try {
    const videoInfo = await getProjectVideos('project-id-here');
    
    if (videoInfo.hasVideos) {
        console.log(`找到 ${videoInfo.videoCount} 个视频`);
        
        videoInfo.videos.forEach(video => {
            console.log(`${video.type} 版本: ${video.sizeMB}MB`);
            
            // 创建视频播放器
            const videoElement = document.createElement('video');
            videoElement.src = video.streamUrl;
            videoElement.controls = true;
            videoElement.style.width = '100%';
            videoElement.style.maxWidth = '600px';
            document.body.appendChild(videoElement);
            
            // 创建下载链接
            const downloadLink = document.createElement('a');
            downloadLink.href = video.downloadUrl;
            downloadLink.download = video.filename;
            downloadLink.textContent = `下载 ${video.type} 版本`;
            document.body.appendChild(downloadLink);
        });
        
        // 显示缩略图
        if (videoInfo.thumbnailUrl) {
            const thumbnail = document.createElement('img');
            thumbnail.src = videoInfo.thumbnailUrl;
            thumbnail.alt = '视频缩略图';
            thumbnail.style.maxWidth = '300px';
            document.body.appendChild(thumbnail);
        }
    } else {
        console.log('该项目暂无视频');
    }
} catch (error) {
    console.error('获取视频失败:', error.message);
}
```

### 直接下载视频

```javascript
function downloadVideo(projectId, videoType = 'final') {
    const downloadUrl = `${API_BASE}/video/download/${projectId}/${videoType}`;
    
    // 创建隐藏的下载链接
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `${projectId}_${videoType}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 使用示例
downloadVideo('project-id-here', 'hq'); // 下载高质量版本
```

## 5. 📁 项目管理

### 获取项目列表

```javascript
async function getProjects(page = 1, perPage = 10, status = '') {
    const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString()
    });
    
    if (status) {
        params.append('status', status);
    }
    
    const response = await fetch(`${API_BASE}/projects?${params}`);
    const data = await response.json();
    
    if (response.ok) {
        return {
            projects: data.projects,
            pagination: data.pagination
        };
    }
    
    throw new Error(data.error);
}

// 使用示例
const { projects, pagination } = await getProjects(1, 10, 'approved');
console.log(`第 ${pagination.page} 页，共 ${pagination.pages} 页`);
```

### 获取完整项目内容

```javascript
async function getCompleteProjectContent(projectId) {
    const response = await fetch(`${API_BASE}/content/project/${projectId}/complete`);
    const data = await response.json();
    
    if (response.ok) {
        return {
            projectId: data.project_id,
            projectName: data.project_name,
            createdAt: data.created_at,
            status: data.status,
            userIdea: data.user_idea,
            storyOutline: data.story_outline,
            characterProfiles: data.character_profiles
        };
    }
    
    throw new Error(data.error);
}
```

## 🎯 完整的前端集成示例

```javascript
class SparkAIClient {
    constructor(apiBase = 'http://localhost:5000/api') {
        this.apiBase = apiBase;
    }
    
    // 聊天功能
    async sendMessage(message, isFirstMessage = false) {
        const response = await fetch(`${this.apiBase}/chat/send`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, is_first_message: isFirstMessage })
        });
        return response.json();
    }
    
    // 获取项目列表
    async getProjects() {
        const response = await fetch(`${this.apiBase}/projects`);
        const data = await response.json();
        return data.projects;
    }
    
    // 获取故事大纲
    async getOutline(projectId) {
        const response = await fetch(`${this.apiBase}/content/project/${projectId}/outline`);
        const data = await response.json();
        return data.outline;
    }
    
    // 获取角色信息
    async getCharacters(projectId) {
        const response = await fetch(`${this.apiBase}/content/project/${projectId}/characters`);
        const data = await response.json();
        return data.characters;
    }
    
    // 获取视频信息
    async getVideos(projectId) {
        const response = await fetch(`${this.apiBase}/video/project/${projectId}/videos`);
        const data = await response.json();
        return data.video_info;
    }
}

// 使用示例
const client = new SparkAIClient();

// 完整的工作流程
async function completeWorkflow() {
    try {
        // 1. 聊天对话
        const chatResponse = await client.sendMessage("我想制作一个科幻视频", true);
        console.log('机器人回复:', chatResponse.response);
        
        // 2. 获取项目列表
        const projects = await client.getProjects();
        if (projects.length > 0) {
            const projectId = projects[0].project_id;
            
            // 3. 获取故事大纲
            const outline = await client.getOutline(projectId);
            console.log('故事标题:', outline.title);
            
            // 4. 获取角色图片
            const characters = await client.getCharacters(projectId);
            characters.forEach(char => {
                console.log(`角色 ${char.name}: ${char.image_url}`);
            });
            
            // 5. 获取最终视频
            const videos = await client.getVideos(projectId);
            if (videos.has_videos) {
                videos.available_videos.forEach(video => {
                    console.log(`视频 ${video.type}: ${video.stream_url}`);
                });
            }
        }
    } catch (error) {
        console.error('工作流程错误:', error);
    }
}
```

## 🔧 错误处理

```javascript
async function safeApiCall(apiFunction) {
    try {
        return await apiFunction();
    } catch (error) {
        if (error.name === 'TypeError') {
            console.error('网络错误:', error.message);
            return { error: '网络连接失败，请检查服务器状态' };
        } else {
            console.error('API错误:', error.message);
            return { error: error.message };
        }
    }
}

// 使用示例
const result = await safeApiCall(() => getProjectOutline('invalid-id'));
if (result.error) {
    console.log('处理错误:', result.error);
}
```

## 📱 响应式设计建议

```css
/* 视频播放器响应式样式 */
.video-container {
    position: relative;
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
}

.video-player {
    width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* 角色卡片响应式布局 */
.characters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    padding: 20px;
}

.character-card {
    background: white;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.character-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 10px;
}
```

## 🚀 部署建议

### 开发环境
```bash
python run_api.py --config development --host 127.0.0.1 --port 5000
```

### 生产环境
```bash
# 使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "src.spark.api.app:create_app('production')"

# 或使用内置服务器
python run_api.py --config production --host 0.0.0.0 --port 8000
```

### CORS配置
确保在生产环境中正确配置CORS：

```python
# src/spark/api/config.py
class ProductionConfig(Config):
    CORS_ORIGINS = [
        'https://your-frontend-domain.com',
        'https://your-app.com'
    ]
```

## 📞 技术支持

- **API文档**: `GET /api/docs`
- **健康检查**: `GET /api/health`
- **测试脚本**: `python test_api_integration.py`
- **前端示例**: `frontend_example.html`

## 🎉 总结

通过以上API接口，你可以实现：

1. ✅ **聊天机器人对话** - 实时交互式对话
2. ✅ **故事大纲传递** - 获取结构化的故事内容
3. ✅ **角色图片展示** - 显示AI生成的角色图像
4. ✅ **最终视频播放** - 流媒体播放和下载功能

所有接口都支持跨域请求、错误处理和会话管理，可以直接集成到你的前端应用中。