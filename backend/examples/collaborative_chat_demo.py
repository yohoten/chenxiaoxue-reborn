"""
模型协作与聚合功能 - 快速开始示例

演示如何使用多模型协作系统解决复杂问题
"""

import asyncio
import json
from app.services.ai_router import ai_router, TaskType


async def example_basic_collaboration():
    """示例1: 基础协作模式"""
    print("=" * 60)
    print("示例1: 基础协作模式")
    print("=" * 60)
    
    result = await ai_router.collaborative_chat(
        messages=[
            {
                "role": "user",
                "content": "请分析2024年人工智能行业的发展趋势，包括技术突破、市场变化和投资机会"
            }
        ],
        task_type=TaskType.COMPLEX,
        enable_collaboration=True
    )
    
    print("\n📝 最终回答:")
    print(result["response"][:500] + "...")
    
    print(f"\n🤖 使用模型: {', '.join(result['models_used'])}")
    print(f"⏱️  总耗时: {result['latency_ms']:.0f}ms")
    print(f"💰 总成本: ${result['total_cost']:.4f}")
    
    print(f"\n📊 子任务详情:")
    for i, subtask in enumerate(result["subtask_results"], 1):
        print(f"  {i}. [{subtask['type']}] {subtask['model']}")
        print(f"     置信度: {subtask['confidence']:.2f}")
        print(f"     耗时: {subtask['execution_time_ms']:.0f}ms")


async def example_comparison():
    """示例2: 协作模式 vs 单模型对比"""
    print("\n" + "=" * 60)
    print("示例2: 协作模式 vs 单模型对比")
    print("=" * 60)
    
    question = "设计一个支持百万并发的即时通讯系统架构"
    
    # 方式1: 单模型
    print("\n【方式1】单模型处理:")
    single_result = await ai_router.chat_completion(
        messages=[{"role": "user", "content": question}],
        task_type=TaskType.CODE,
        complexity=TaskType.HARD
    )
    print(f"  耗时: {single_result['latency_ms']:.0f}ms")
    print(f"  成本: ${single_result['usage']['total_tokens'] * 0.001:.4f}")
    print(f"  回答长度: {len(single_result['response'])} 字符")
    
    # 方式2: 协作模式
    print("\n【方式2】协作模式:")
    collab_result = await ai_router.collaborative_chat(
        messages=[{"role": "user", "content": question}],
        task_type=TaskType.COMPLEX,
        enable_collaboration=True
    )
    print(f"  耗时: {collab_result['latency_ms']:.0f}ms")
    print(f"  成本: ${collab_result['total_cost']:.4f}")
    print(f"  回答长度: {len(collab_result['response'])} 字符")
    print(f"  使用模型: {len(collab_result['models_used'])} 个")
    
    print(f"\n📈 对比分析:")
    print(f"  质量提升: {'✓' if len(collab_result['response']) > len(single_result['response']) else '✗'}")
    print(f"  多维度分析: {'✓' if len(collab_result['subtask_results']) > 1 else '✗'}")
    print(f"  成本增加: {(collab_result['total_cost'] / (single_result['usage']['total_tokens'] * 0.001)):.1f}x")


async def example_custom_decomposition():
    """示例3: 自定义任务分解（通过提示词引导）"""
    print("\n" + "=" * 60)
    print("示例3: 自定义任务分解")
    print("=" * 60)
    
    # 通过详细的提示词引导分解方向
    result = await ai_router.collaborative_chat(
        messages=[
            {
                "role": "user",
                "content": """
请帮我全面评估这个创业想法：开发一个AI辅助的在线教育平台

要求从以下维度分析：
1. 市场需求和竞争格局
2. 技术可行性和实现难度
3. 商业模式和盈利路径
4. 潜在风险和应对策略
5. 启动计划和里程碑

每个维度都需要深入分析，最后给出综合建议。
"""
            }
        ],
        task_type=TaskType.COMPLEX,
        enable_collaboration=True
    )
    
    print(f"\n📋 任务分解结果:")
    print(f"  子任务数量: {len(result['subtask_results'])}")
    
    for i, subtask in enumerate(result["subtask_results"], 1):
        print(f"\n  子任务 {i}:")
        print(f"    类型: {subtask['type']}")
        print(f"    模型: {subtask['model']}")
        print(f"    置信度: {subtask['confidence']:.2f}")
        print(f"    内容预览: {subtask['content_preview'][:100]}...")


async def example_error_handling():
    """示例4: 错误处理和降级策略"""
    print("\n" + "=" * 60)
    print("示例4: 错误处理和降级策略")
    print("=" * 60)
    
    # 模拟一个可能导致部分模型失败的任务
    result = await ai_router.collaborative_chat(
        messages=[
            {
                "role": "user",
                "content": "请用Python写一个高性能的Web服务器，支持WebSocket和HTTP/2"
            }
        ],
        task_type=TaskType.COMPLEX,
        enable_collaboration=True
    )
    
    print(f"\n✅ 执行状态:")
    print(f"  协作是否成功: {result.get('collaboration_used', False)}")
    print(f"  完成的子任务: {len(result['subtask_results'])}/{len(result['subtask_results'])}")
    
    # 检查是否有低置信度的结果
    low_confidence_tasks = [
        t for t in result['subtask_results'] 
        if t['confidence'] < 0.7
    ]
    
    if low_confidence_tasks:
        print(f"\n⚠️  警告: {len(low_confidence_tasks)} 个子任务置信度较低")
        for task in low_confidence_tasks:
            print(f"  - [{task['type']}] 置信度: {task['confidence']:.2f}")
    else:
        print(f"\n✅ 所有子任务置信度良好")


async def example_cost_control():
    """示例5: 成本控制策略"""
    print("\n" + "=" * 60)
    print("示例5: 成本控制策略")
    print("=" * 60)
    
    MAX_BUDGET = 0.10  # 预算上限 $0.10
    
    result = await ai_router.collaborative_chat(
        messages=[
            {
                "role": "user",
                "content": "解释量子计算的基本原理和应用前景"
            }
        ],
        task_type=TaskType.COMPLEX,
        enable_collaboration=True
    )
    
    actual_cost = result['total_cost']
    
    print(f"\n💰 成本分析:")
    print(f"  预算上限: ${MAX_BUDGET:.2f}")
    print(f"  实际成本: ${actual_cost:.4f}")
    print(f"  预算使用率: {(actual_cost / MAX_BUDGET * 100):.1f}%")
    
    if actual_cost > MAX_BUDGET:
        print(f"\n❌ 超出预算! 建议使用更简单的任务或降低复杂度")
    else:
        print(f"\n✅ 在预算范围内")
    
    print(f"\n📊 各模型成本分布:")
    # 这里可以添加更详细的成本分析


async def main():
    """运行所有示例"""
    print("🚀 陈筱雪 AI 助手 - 模型协作功能演示\n")
    
    try:
        await example_basic_collaboration()
        await example_comparison()
        await example_custom_decomposition()
        await example_error_handling()
        await example_cost_control()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例执行完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())