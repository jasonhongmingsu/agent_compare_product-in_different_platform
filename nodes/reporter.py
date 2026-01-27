from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from config import get_llm
from schema import AgentState, ComparisonReport

# 初始化用于生成报告的模型
# 建议使用推理能力较强的模型（如 gpt-4o），因为它需要对比多个平台的差异
llm = get_llm()

def report_node(state: AgentState):
    """
    负责将所有搜集到的产品信息进行横向对比，并给出结构化的购买建议。
    """
    print("--- [Node: Reporter] 正在汇总数据并生成对比报告 ---")
    
    # 1. 检查是否有数据可分析
    if not state.collected_data:
        return {
            "messages": [("ai", "抱歉，我未能从任何平台搜集到有效的产品信息。")],
            "collected_data": []
        }

    # 2. 绑定结构化输出
    # 这一步是企业级开发的关键：确保 LLM 输出的直接就是 ComparisonReport 对象
    reporter_llm = llm.with_structured_output(ComparisonReport)
    
    # 3. 构造提示词 (Prompt)
    # 我们将之前所有搜集到的 ProductResult 喂给模型
    data_context = "\n".join([
        f"平台: {p.platform}, 名称: {p.name}, 价格: {p.price}, 核心卖点: {p.summary}"
        for p in state.collected_data
    ])
    
    system_prompt = f"""
    你是一个极其专业的数码产品评论家。
    请根据下方提供的各平台实时搜索数据，生成一份客观、严谨的比价报告。
    
    你的任务：
    1. 整理各平台的优势与劣势。
    2. 考虑价格因素，给出最终的『购买建议』。
    3. 如果某个平台的价格明显异常（过高或过低），请在建议中指出。

    搜集到的原始数据:
    {data_context}
    """
    
    # 4. 执行汇总
    try:
        final_report = reporter_llm.invoke(system_prompt)
    except Exception as e:
        print(f"报告生成失败: {e}")
        # 降级处理：生成一个简单的文本回复
        return {
            "messages": [("ai", "生成的报告格式有误，请稍后重试。")],
        }

    # 5. 返回结果
    # 这里返回的字典会更新图的全局状态
    return {
        "messages": [("ai", f"报告生成完毕！\n【最终建议】：{final_report.recommendation}")],
        # 保持 collected_data 的状态，方便前端或其他节点后续调用
        "collected_data": state.collected_data 
    }