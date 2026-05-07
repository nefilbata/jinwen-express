# 金文速递 (Jinwen Express)

自动聚合金文（青铜器铭文）与古文字研究最新学术论文，AI 一句话解读核心发现。

## 功能

- **多源聚合**：CNKI 期刊 RSS · Semantic Scholar · arXiv · Google Scholar · 学术机构官网
- **AI 解读**：每篇论文自动生成一句话中文摘要（支持 DeepSeek / OpenAI 兼容接口）
- **信源筛选**：按期刊、数据库分类浏览
- **每日自动更新**：定时抓取，无需手动操作

## 快速开始

### 1. 环境要求

- Python 3.11+
- Node.js 20+
- Chrome（用于部分需要浏览器会话的抓取）

### 2. 安装后端

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置 AI 摘要（可选）

复制 `.env.example` 为 `.env`，填入 API Key：

```env
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-v4-flash
```

支持所有 OpenAI 兼容接口（DeepSeek、通义千问、GLM 等）。

### 4. 配置期刊 RSS

编辑 `backend/journals.txt`，每行一个源：

```
期刊名称 | RSS地址或网站URL
```

已内置 20+ 个金文核心期刊的 CNKI RSS 地址。

### 5. 安装前端

```bash
cd frontend
npm install
```

### 6. 启动

双击 `start.bat`，或分别运行：

```bash
# 终端1 - 后端 (port 8000)
cd backend
python main.py

# 终端2 - 前端 (port 3000)
cd frontend
npm run dev
```

访问 `http://localhost:3000`

### 7. 手动触发抓取

```bash
curl -X POST "http://localhost:8000/api/v1/admin/crawl?api_key=jinwen-admin-2026"
```

## 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | FastAPI (Python) |
| 定时任务 | APScheduler |
| 数据库 | SQLite |
| AI | DeepSeek V4 Flash / OpenAI 兼容 |
| 前端 | Next.js 14 + Tailwind CSS |
| 设计 | 青铜考古档案风格 |

## 项目结构

```
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── api.py               # REST 路由
│   ├── models.py            # 数据库模型
│   ├── crawlers/            # 爬虫模块
│   │   ├── journal_rss.py   # 期刊 RSS / 网站爬虫
│   │   ├── semantic_scholar.py
│   │   ├── arxiv.py
│   │   └── google_scholar.py
│   ├── services/
│   │   ├── ai_summary.py    # AI 摘要生成
│   │   └── dedup.py         # 论文去重
│   └── journals.txt         # 期刊 RSS 配置
├── frontend/
│   └── src/
│       ├── app/latest/      # 最新论文
│       ├── app/featured/    # 精选
│       └── app/archive/     # 归档统计
└── start.bat
```

## API

```
GET  /api/v1/latest?source=&page=&size=30     # 最新论文
GET  /api/v1/featured?page=&size=20            # 精选（AI 已解读）
GET  /api/v1/papers/daily/today                # 今日日报
GET  /api/v1/search?q=&page=&size=             # 搜索
GET  /api/v1/stats                              # 统计
POST /api/v1/admin/crawl?api_key=KEY           # 手动抓取
```

## License

MIT
