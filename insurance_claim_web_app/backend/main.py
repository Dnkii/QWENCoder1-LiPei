"""
保险理赔助手Web应用 - 后端主程序
使用FastAPI框架提供RESTful API服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.claims import router as claims_router
from services.database import init_db

# 初始化应用
app = FastAPI(
    title="保险理赔助手API",
    description="基于大模型的保险理赔辅助系统API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()

# 注册API路由
app.include_router(claims_router)

# API根路径
@app.get("/")
async def root():
    return {"message": "保险理赔助手API服务正在运行"}

# 启动命令: uvicorn main:app --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)