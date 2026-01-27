import os
import asyncio
from dotenv import load_dotenv
from graph import comparison_app  # 从你的编排层导入

# 1. 启动时加载环境变量
# 这样系统会自动读取 .env 里的 MODEL_API_KEY, TAVILY_API_KEY, LANGCHAIN_API_KEY 等
load_dotenv()

async def run_comparison_flow():
    """
    主运行逻辑：处理用户输入并展示 Agent 的思考过程
    """
    print("="*50)
    print("🚀 企业级 AI 多源比价助手 已启动")
    print("="*50)
    
    query = input("\n🔎 请输入你想比价的产品名称: ")
    if not query.strip():
        print("❌ 输入不能为空，请重新运行。")
        return

    # 2. 构造初始状态
    # 这里的键名必须与我们在 schema.py 中定义的 AgentState 字段一致
    initial_input = {
        "messages": [("user", query)],
        "platforms": ["Amazon", "JD.com", "Reddit"], # 这里可以根据需求动态修改
        "current_idx": 0,
        "collected_data": []
    }

    print(f"\n[系统] 正在为你分析: {query}...\n")

    # 3. 使用流式输出运行图 (stream)
    # stream_mode="updates" 可以让你看到每一个节点执行完后的增量变化
    try:
        # 使用异步循环（如果你的 nodes 也是异步的，效果更佳）
        async for chunk in comparison_app.astream(initial_input, stream_mode="updates"):
            # 这里的 node_name 是你在 graph.py 中 add_node 时起的文字名
            for node_name, output in chunk.items():
                print(f"✅ 节点 [{node_name}] 处理完成")
                
                # 如果是搜索节点，我们可以打印出它刚刚抓到了哪个平台
                if node_name == "search" and "collected_data" in output:
                    last_item = output["collected_data"][-1]
                    print(f"   ﹂ 已获取 {last_item.platform} 数据: {last_item.price}")
                
                # 如果是报告节点，打印最终 AI 回复
                if node_name == "generate_report" and "messages" in output:
                    print("-" * 30)
                    print(f"🤖 最终建议:\n{output['messages'][-1][1]}")
                    print("-" * 30)

    except Exception as e:
        print(f"\n❌ 运行过程中发生错误: {e}")
        print("💡 提示：请检查 .env 中的 API Key 是否正确，以及网络是否通畅。")

if __name__ == "__main__":
    # 使用 asyncio 运行异步主函数
    try:
        asyncio.run(run_comparison_flow())
    except KeyboardInterrupt:
        print("\n👋 程序已由用户手动停止。")