import operator # 🌟 必须导入这个标准库
from typing import List, Annotated, Union
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages

class ProductResult(BaseModel):
    platform: str
    name: str
    price: str
    summary: str

class ComparisonReport(BaseModel):
    products: List[ProductResult]
    recommendation: str

class AgentState(BaseModel):
    # 1. 消息列表：保持不变，它本身就使用了 add_messages 这个 Reducer
    messages: Annotated[list, add_messages] = []
    
    # 2. 核心数据：🌟 关键修改！
    # 使用 Annotated 和 operator.add。
    # 这样当多个并行节点同时返回数据时，LangGraph 会将它们“相加”（即列表合并）
    # 而不是让后完成的节点覆盖先完成的节点。
    collected_data: Annotated[List[ProductResult], operator.add] = []
    
    # 3. 配置信息
    platforms: List[str] = ["Amazon", "JD.com", "Reddit"]
    
    # 4. 索引：在并行模式下，current_idx 其实不再需要了，
    # 因为我们会直接给每个节点分配具体的任务。
    current_idx: int = 0