# api.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from graph import comparison_app # 导入你的 LangGraph
import os

app = FastAPI()

# 1. 配置静态文件目录（存放 HTML, CSS, JS）
if not os.path.exists("static"):
    os.makedirs("static")

# 2. 数据请求模型
class QueryRequest(BaseModel):
    product_name: str

# 3. 比价接口
@app.post("/compare")
async def compare_api(request: QueryRequest):
    initial_state = {
        "messages": [{"role": "user", "content": request.product_name}],
        "platforms": ["Amazon", "JD.com", "Reddit"],
        "collected_data": [] # 依赖 Reducer 进行并行数据汇总
    }
    # ainvoke 是异步运行，非常适合网页场景
    final_state = await comparison_app.ainvoke(initial_state)
    return {"status": "success", "data": final_state["collected_data"]}

# 4. 首页接口：直接返回我们写的 HTML
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)