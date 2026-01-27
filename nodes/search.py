import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from schema import AgentState, ProductResult
from config import get_llm

# 初始化搜索工具
search_tool = TavilySearchResults(max_results=2)

def search_node(state: AgentState) -> Dict[str, Any]:
    """
    并行搜索节点：
    每个节点实例会根据当前的 platform 独立运行。
    """
    # 1. 获取 LLM 实例
    llm = get_llm()
    
    # 2. 获取当前节点的任务平台
    # 在并行模式下，Graph 会为每个节点分配任务。
    # 我们这里通过 current_idx 来锁定具体平台（配合 graph.py 中的循环）
    platform = state.platforms[state.current_idx]
    user_query = state.messages[0].content
    
    print(f"--- [Parallel Node] 正在检索: {platform} ---")
    
    # 3. 构造适配平台的 Query
    if "JD" in platform.upper() or "天猫" in platform:
        search_query = f"{user_query} {platform} 2026 最新价格 官网"
    else:
        search_query = f"{user_query} price on {platform} 2026"

    # 4. 执行真实搜索
    try:
        search_results = search_tool.invoke(search_query)
    except Exception as e:
        print(f"搜索工具调用失败: {e}")
        search_results = "No data found."

    # 5. 使用结构化输出提取信息
    extractor = llm.with_structured_output(ProductResult)
    
    prompt = f"""
    你是一个专业的比价助手。请从搜索结果中提取 {platform} 的产品信息。
    搜索结果: {search_results}
    
    注意：如果搜索结果中没有明确价格，请提取相关的版本或成色描述。
    """
    
    try:
        product_info = extractor.invoke(prompt)
    except Exception as e:
        print(f"数据提取失败: {e}")
        product_info = ProductResult(
            platform=platform,
            name="提取失败",
            price="N/A",
            summary="无法解析数据"
        )

    # 6. 返回数据
    # 🌟 关键：返回一个列表，由于 schema.py 中使用了 operator.add，
    # 多个并行节点返回的列表会自动合并成一个大列表。
    return {
        "collected_data": [product_info] 
    }