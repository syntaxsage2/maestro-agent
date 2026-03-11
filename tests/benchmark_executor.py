"""
Executor 性能对比测试
对比串行 vs 并行执行的性能差异
"""
import time
from langchain_core.messages import HumanMessage
from intentrouter.graph.main_graph import create_graph


def simulate_serial_execution(steps: list[dict], state: dict) -> dict:
    """
    模拟串行执行（用于对比）
    """
    from intentrouter.graph.runnables import create_step_runnable

    results = {}
    start_time = time.time()

    for step in steps:
        if step["type"] == "synthesis":
            continue

        runnable = create_step_runnable(step)
        step_start = time.time()
        config = {"configurable": {"thread_id": "benchmark-parallel-3"}}

        try:
            result = runnable.invoke(state, config=config)
            step_time = time.time() - step_start

            results[step["id"]] = {
                "success": True,
                "execution_time": step_time
            }
        except Exception as e:
            results[step["id"]] = {
                "success": False,
                "error": str(e)
            }

    total_time = time.time() - start_time
    return results, total_time


def benchmark_parallel_vs_serial():
    """对比并行 vs 串行执行"""

    # 测试用例
    test_message = "帮我做以下事情：1) 查询 LangGraph 文档，2) 搜索最新 AI 新闻，3) 计算 100*200，最后给我总结"

    print("=" * 80)
    print("🏁 性能对比测试：串行 vs 并行")
    print("=" * 80)
    print(f"测试任务: {test_message}\n")

    # 1. 使用优化后的并行执行
    print("🔵 测试 1: 并行执行（RunnableParallel）")
    print("-" * 80)

    app = create_graph()
    config = {"configurable": {"thread_id": "benchmark-parallel-2"}}

    parallel_start = time.time()
    result_parallel = app.invoke({
        "messages": [HumanMessage(content=test_message)],
        "thread_id": "benchmark-parallel"
    }, config=config)
    parallel_time = time.time() - parallel_start

    print(f"✅ 并行执行完成: {parallel_time:.2f}秒")

    # 2. 提取计划并模拟串行执行
    plan = result_parallel.get("plan")
    if plan and plan.get("steps"):
        print(f"\n🔴 测试 2: 串行执行（模拟）")
        print("-" * 80)

        # 只执行非 synthesis 步骤
        executable_steps = [s for s in plan["steps"] if s["type"] != "synthesis"]

        serial_results, serial_time = simulate_serial_execution(
            executable_steps,
            {"messages": [HumanMessage(content=test_message)]}
        )

        print(f"✅ 串行执行完成: {serial_time:.2f}秒")

        # 3. 对比结果
        print("\n" + "=" * 80)
        print("📊 性能对比结果")
        print("=" * 80)

        speedup = serial_time / parallel_time if parallel_time > 0 else 0
        time_saved = serial_time - parallel_time
        improvement = (time_saved / serial_time * 100) if serial_time > 0 else 0

        print(f"\n并行执行时间: {parallel_time:.2f}秒")
        print(f"串行执行时间: {serial_time:.2f}秒")
        print(f"加速比: {speedup:.2f}x")
        print(f"节省时间: {time_saved:.2f}秒")
        print(f"性能提升: {improvement:.1f}%")

        print("\n详细对比:")
        parallel_results = result_parallel.get("subtask_results", {})

        for step_id in parallel_results.keys():
            if step_id in serial_results:
                p_time = parallel_results[step_id].get("execution_time", 0)
                s_time = serial_results[step_id].get("execution_time", 0)
                print(f"  {step_id}:")
                print(f"    并行: {p_time:.2f}s | 串行: {s_time:.2f}s")

        print("\n" + "=" * 80)

        if speedup > 1.5:
            print("✅ 并行优化效果显著！")
        elif speedup > 1.1:
            print("✅ 并行优化有效果")
        else:
            print("⚠️  并行优化效果不明显（可能任务太简单或网络延迟主导）")

    else:
        print("\n⚠️  未生成执行计划，无法对比")


if __name__ == "__main__":
    benchmark_parallel_vs_serial()