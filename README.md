# AI 智能穿衣推荐系统

基于 Vue3 + FastAPI 构建的智能穿衣推荐系统，通过分析天气数据和用户需求，提供个性化的穿衣建议。

## 🌟 项目特点

- 🎯 **智能推荐**：结合天气数据和用户需求生成个性化穿衣建议
- 💬 **流式对话**：支持实时流式输出，提供类似 ChatGPT 的聊天体验
- 🔄 **实时天气**：通过天气 Agent 获取实时天气信息
- 🎨 **现代化 UI**：采用 Vue3 构建的响应式界面
- 🚀 **高性能**：使用 SSE（Server-Sent Events）实现实时通信

## 📋 功能列表

- ✅ 用户输入城市和日期
- ✅ 实时天气查询
- ✅ 智能穿衣推荐
- ✅ 流式聊天交互
- ✅ 消息历史记录
- ✅ 用户自定义头像
- ✅ 响应式设计

## 🏗️ 技术栈

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 快速的前端构建工具
- **CSS3** - 现代样式设计

### 后端
- **FastAPI** - 现代、快速的 Web 框架
- **OpenAI API** - 大语言模型集成
- **天气 Agent** - 智能天气查询系统
- **CORS** - 跨域资源共享支持
- **SSE** - 服务器推送事件

### 数据源
- **DeepSeek API** - 大语言模型
- **高德地图 API** - 地理位置和天气数据

## 📁 项目结构

```
AI/
├── backend/                    # 后端服务
│   ├── agent/                 # 智能体模块
│   │   ├── __init__.py
│   │   ├── recommend.py       # 推荐智能体
│   │   └── weather_agent.py   # 天气智能体
│   ├── main.py                # FastAPI 主程序
├── frontend/                 # 前端应用
│   ├── public/                # 静态资源
│   │   └── assets/           # 头像等资源
│   │       ├── user.jpg     # 用户头像
│   │       └── bot.png      # 机器人头像
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   │   ├── InputPage.vue # 输入页面
│   │   │   └── ChatPage.vue # 聊天页面
│   │   ├── router/           # 路由配置
│   │   │   └── index.js
│   │   ├── App.vue          # 根组件
│   │   └── main.js          # 应用入口
│   ├── package.json
│   └── vite.config.js
├── .env.example                     # 环境变量配置

```

## 🚀 快速开始

### 环境要求

- Python 3.13+
- Node.js 24+
- npm 或 yarn

#### 安装 Python 依赖

```bash
pip install -r requirements.txt
```

#### 配置环境变量

编辑 `.env` 文件，配置以下必要信息：

```env
# 配置env文件
cp .env.example .env

# LLM API 配置
LLM_MODEL_ID=you_model_id_here
LLM_BASE_URL=your_base_url_here
LLM_API_KEY=your_api_key_here

# 高德天气 API 配置 https://lbs.amap.com/
AMAP_API_KEY=your_amap_key_here
```

### 3. 配置前端环境

```bash
cd frontend
npm install
```

### 4. 运行项目

#### 启动后端服务

```bash
cd backend
python main.py
```
后端将在 `http://localhost:8000` 运行

#### 启动前端开发服务器

```bash
cd frontend
npm run dev
```
前端将在 `http://localhost:5173` 运行

### 5. 访问应用

打开浏览器访问 `http://localhost:5173`，即可使用智能穿衣推荐系统。

## 📖 API 文档

### 主要接口

#### SSE 流式聊天接口

```
GET /chat/stream?message={用户输入}
```

参数：
- `message` (required): 用户输入的自然语言

响应格式：
- Server-Sent Events (SSE)
- JSON 数据格式

#### 示例

```bash
curl "http://localhost:8000/chat/stream?message=2月6日去福州应该穿什么"
```

响应示例：
```
data: {"type": "chunk", "content": "根"}
data: {"type": "chunk", "content": "据"}
data: {"type": "chunk", "content": "天"}
...
data: {"type": "done"}
```

### 数据格式说明

#### 消息类型

- `chunk`: 流式输出内容
- `done`: 流式输出完成
- `error`: 错误信息

#### 错误处理

```json
{
  "type": "error",
  "message": "错误信息"
}
```

### 自定义头像

将自定义头像文件放置在 `frontend/public/assets/` 目录下：

- 用户头像：`user.png`
- 机器人头像：`bot.png`

支持的格式：PNG、JPG、SVG（建议正方形）

## 🎯 使用指南

### 基本使用

1. 在首页输入框中输入问题
   - 示例："2月6日去福州应该穿什么？"
2. 点击"发送"按钮
3. 等待系统返回流式回复
4. 可在聊天页面继续对话

### 使用提示

- 支持自然语言输入
- 可查询未来4天内的天气
- 系统会根据气温、温差、天气状况给出具体建议

## 🛠️ 开发指南

### 修改推荐逻辑

编辑 `backend/agent/recommend.py` 来修改推荐逻辑。

### 修改天气查询

编辑 `backend/agent/weather_agent.py` 来修改天气查询逻辑。

### 自定义样式

修改 `frontend/src/pages/` 中的 Vue 组件样式。

## 📊 项目架构

### 前端架构

```
frontend/
├── InputPage.vue    # 输入页面
└── ChatPage.vue     # 聊天页面（包含消息列表、输入框）
```

### 后端架构

```
backend/
├── main.py         # FastAPI 应用入口
└── agent/
    ├── recommend.py   # 推荐智能体
    └── weather_agent.py  # 天气智能体
```
---

**注意**：本项目仅用于学习和演示目的，请遵守相关 API 的使用条款。
