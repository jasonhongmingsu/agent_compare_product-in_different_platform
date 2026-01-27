from functools import partial
from langgraph.graph import StateGraph, START, END
from schema import AgentState
from nodes.search import search_node
from nodes.reporter import report_node

def create_graph():
    """
    通过 Fan-out (扇出) 模式实现多平台并行比价。
    """
    # 1. 初始化图
    workflow = StateGraph(AgentState)
    
    # 2. 注册汇总报告节点
    workflow.add_node("generate_report", report_node)
    
    # 3. 动态配置并行平台
    # 注意：这里的列表建议与 schema.py 中的默认值保持一致
    platforms = ["Amazon", "JD.com", "Reddit"]
    
    # 🌟 并行编排核心逻辑
    for i, platform in enumerate(platforms):
        node_name = f"search_{platform}"
        
        # 使用 partial 预先绑定当前循环的索引 i 给 search_node
        # 这样当这个节点启动时，它收到的 state 虽然是全局的，
        # 但我们可以通过一种方式让它知道自己负责第 i 个平台。
        # (另一种更简单的方法是直接在 search_node 里根据 node_name 识别，如下：)
        
        workflow.add_node(
            node_name, 
            # 这里的 lambda 确保每个节点执行时能拿到它独特的索引
            lambda state, idx=i: search_specific_platform(state, idx)
        )
        
        # 设置并行路径：START -> 所有搜索节点
        workflow.add_edge(START, node_name)
        
        # 设置汇聚路径：所有搜索节点 -> 报告节点
        workflow.add_edge(node_name, "generate_report")

    # 4. 报告完成后结束流程
    workflow.add_edge("generate_report", END)
    
    # 5. 编译
    app = workflow.compile()
    return app

def search_specific_platform(state: AgentState, idx: int):
    """
    辅助函数：将正确的索引注入到 search_node 中。
    """
    # 临时修改 state 中的索引，确保 search_node 抓到正确的平台
    state.current_idx = idx
    return search_node(state)

# 导出编译好的应用
comparison_app = create_graph()