# 保险理赔助手Web应用

这是一个基于大模型技术的保险理赔辅助Web系统，能够自动处理理赔文档和影像资料，实现智能分类、关键信息提取和责任判定。

## 系统架构

本项目采用前后端分离架构：

- **前端**：React + TypeScript + Ant Design，提供用户友好的界面
- **后端**：FastAPI + Python，提供RESTful API服务
- **AI模型**：集成大语言模型进行文档理解与信息提取
- **数据库**：PostgreSQL存储结构化数据

## 功能模块

### 1. 数据准备与基础建设
- 构建产品条款知识库
- 整理历史理赔语料库
- 搭建多模态数据处理管道

### 2. 核心功能模块
- 单据分类模块（支持59类单证分类）
- 信息提取模块（自动提取建单和发票字段）
- AI判责与风险研判模块
- 调查报告总结模块

### 3. 用户界面功能
- 文档上传与管理
- 实时处理进度显示
- 结果展示与编辑
- 历史记录查询

## 技术栈

### 前端
- React 18
- TypeScript
- Ant Design 5.x
- Axios
- React Router

### 后端
- Python 3.9+
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Celery (异步任务处理)

## 快速开始

### 前端启动
```bash
cd frontend
npm install
npm start
```

### 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## API接口

- `POST /api/upload`: 上传理赔文档
- `GET /api/claims/{claim_id}`: 获取理赔详情
- `GET /api/classify`: 文档分类
- `POST /api/extract`: 信息提取
- `POST /api/evaluate`: 责任评估
- `GET /api/reports/{claim_id}`: 生成报告