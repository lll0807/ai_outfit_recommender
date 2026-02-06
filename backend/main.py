from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from agent.recommend import RecommendAgent
from typing import AsyncGenerator
import json

app = FastAPI(title="AI Chat API")

# 添加 CORS 中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应指定具体域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)


async def generate_sse_response(user_input: str) -> AsyncGenerator[str, None]:
    """
    生成 SSE 格式的流式响应
    SSE 格式: data: <json_content>\n\n
    """
    agent = RecommendAgent()


    try:
        # 调用 Agent 的流式方法
        async for chunk in agent.run_stream(user_input):
            # 包装为 SSE 格式
            sse_data = {
                "type": "chunk",
                "content": chunk
            }
            yield f"data: {json.dumps(sse_data, ensure_ascii=False)}\n\n"

            # 发送完成信号
        done_data = {"type": "done"}
        yield f"data: {json.dumps(done_data, ensure_ascii=False)}\n\n"

    except Exception as e:
        # 发送错误信号
        error_data = {"type": "error", "message": str(e)}
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"


@app.get("/")
async def root():
    return {"message": "AI Chat API is running"}


@app.get("/chat/stream")
async def chat_stream(message: str):
    """
    SSE 流式聊天接口

    使用方式:
    EventSource('/chat/stream?message=你好')
    """
    print("调用SSE")
    return StreamingResponse(
        generate_sse_response(message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)