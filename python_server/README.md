# 火山引擎API接入服务

## 项目介绍

本项目是一个基于Flask的Web服务器，用于接入火山引擎API，实现对话脚本生成、文生图和图生视频功能。

## 功能特性

- 对话脚本生成API
- 文生图API
- 图生视频API

## 环境要求

- Python 3.7+
- Flask
- requests
- python-dotenv

## 安装步骤

1. 克隆项目到本地
2. 进入项目目录
3. 创建并激活虚拟环境：
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. 安装依赖：
   ```bash
   pip3 install -r requirements.txt
   ```
5. 配置环境变量：
   编辑 `.env` 文件，填写火山引擎的访问密钥：
   ```
   VOLCENGINE_ACCESS_KEY=your_access_key_here
   VOLCENGINE_SECRET_KEY=your_secret_key_here
   ```

## 启动服务

```bash
python3 app.py
```

服务将在 `http://localhost:5000` 运行。

## API接口

### 1. 对话脚本生成

**接口**：`POST /api/dialogue`

**请求体**：
```json
{
  "prompt": "生成一个关于朋友聚会的对话脚本"
}
```

**响应**：
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "ep-20240316164822-d58k5",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "对话脚本内容"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 100,
    "total_tokens": 110
  }
}
```

### 2. 文生图

**接口**：`POST /api/text2image`

**请求体**：
```json
{
  "prompt": "一只可爱的小猫在阳光下玩耍"
}
```

**响应**：
```json
{
  "created": 1677858242,
  "data": [
    {
      "url": "https://example.com/image.png"
    }
  ]
}
```

### 3. 图生视频

**接口**：`POST /api/image2video`

**请求体**：
```json
{
  "image_url": "https://example.com/image.png"
}
```

**响应**：
```json
{
  "created": 1677858242,
  "data": [
    {
      "url": "https://example.com/video.mp4"
    }
  ]
}
```

## 注意事项

1. 请确保您已经在火山引擎控制台创建了相应的API密钥
2. 替换 `.env` 文件中的访问密钥为实际的值
3. 替换代码中的模型ID为您在火山引擎中创建的实际模型ID
4. 本服务仅用于开发测试，生产环境请使用专业的WSGI服务器

## 故障排除

- 确保网络连接正常
- 检查API密钥是否正确
- 检查模型ID是否正确
- 查看服务器日志获取详细错误信息
