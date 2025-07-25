# Wanx2.1-t2i-turbo 图片生成问题解决方案

## 🔍 问题诊断

### 当前状态
- ✅ Chatbot对话功能正常
- ✅ 想法结构化正常  
- ✅ 剧情大纲生成正常
- ❌ **图片生成失败** - API密钥问题

### 错误信息
```
Image generation failed: 401 - {"code":"InvalidApiKey","message":"Invalid API-key provided."}
```

### 根本原因
**API密钥格式不正确**：
- 当前密钥格式：`AIzaSyAn...` (这是Google API密钥格式)
- 需要的格式：`sk-...` (阿里云DashScope格式)

## 🎯 解决方案

### 步骤1: 获取正确的阿里云DashScope API密钥

1. **访问阿里云DashScope控制台**
   - 网址：https://dashscope.console.aliyun.com/
   
2. **注册/登录阿里云账号**

3. **开通通义万相服务**
   - 找到「通义万相」服务
   - 点击「立即开通」
   - 确认服务条款

4. **获取API密钥**
   - 进入「API-KEY管理」
   - 创建新的API-KEY
   - 复制生成的密钥（格式应为 `sk-xxxxxxxxxx`）

### 步骤2: 设置环境变量

**临时设置（当前会话）：**
```bash
export IMAGE_GEN_API_KEY='sk-your-actual-dashscope-key'
```

**永久设置（.env文件）：**
```bash
echo 'IMAGE_GEN_API_KEY=sk-your-actual-dashscope-key' >> .env
```

### 步骤3: 验证配置

```bash
# 诊断当前配置
python diagnose_image_generation.py

# 测试图片生成
python test_image_generation.py
```

### 步骤4: 运行完整测试

```bash
# 带真实图片生成的完整测试
python test_complete_chatbot_flow.py

# 或者先用模拟图片验证流程
python test_chatbot_with_mock_images.py
```

## 🛠️ 技术细节

### Wanx2.1-t2i-turbo API调用

**端点**: `https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis`

**请求格式**:
```json
{
  "model": "wanx-v1",
  "input": {
    "prompt": "描述文本",
    "style": "anime",
    "size": "1024*1024",
    "n": 1
  }
}
```

**认证头**:
```
Authorization: Bearer sk-your-dashscope-key
Content-Type: application/json
```

### 当前实现位置

**主要文件**:
- `src/spark/chatbot/character_generator.py` - 角色图片生成
- `src/spark/config.py` - API配置管理

**核心类**:
- `WanxImageGenerator` - Wanx2.1-t2i-turbo调用封装
- `CharacterProfileGenerator` - 角色档案和图片生成

## 📊 测试脚本

### 可用的测试工具

1. **diagnose_image_generation.py** - 诊断API配置问题
2. **test_image_generation.py** - 专门测试图片生成功能
3. **setup_dashscope_api.py** - API设置指南
4. **test_chatbot_with_mock_images.py** - 使用模拟图片的完整流程

### 运行顺序建议

```bash
# 1. 诊断问题
python diagnose_image_generation.py

# 2. 设置API密钥（按指南操作）
python setup_dashscope_api.py

# 3. 验证图片生成
python test_image_generation.py

# 4. 完整流程测试
python test_chatbot_with_mock_images.py  # 模拟版本
# 或
python test_complete_chatbot_flow.py     # 真实版本
```

## 🔄 模拟模式

如果暂时无法获取DashScope API密钥，可以使用模拟模式：

**特点**:
- ✅ 完整流程演示
- ✅ 生成模拟图片URL
- ✅ 所有其他功能正常
- 📝 输出显示 `https://mock-images.spark-ai.com/character_*.png`

**运行**:
```bash
python test_chatbot_with_mock_images.py
```

## 💰 费用说明

### 阿里云通义万相计费
- **按生成次数计费**
- **免费额度**: 新用户通常有一定免费调用次数
- **付费标准**: 参考阿里云官方定价

### 建议
1. 先使用免费额度测试
2. 确认功能正常后再考虑购买
3. 可以先用模拟模式验证完整流程

## 🎉 预期结果

配置正确后，你将看到：

```
✅ 角色图片生成成功!
🎨 图片: https://dashscope-result.oss-accelerate.aliyuncs.com/xxx.png
```

角色档案将包含：
- 完整的角色信息（姓名、外观、性格等）
- 真实的图片URL链接
- 可在浏览器中直接查看的图片

---

**下一步**: 按照上述步骤获取正确的DashScope API密钥，即可启用完整的图片生成功能！ 