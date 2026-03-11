"""
Writer Agent 测试
"""
from langchain_core.messages import HumanMessage
from intentrouter.graph.main_graph import create_graph


def test_writer_agent():
    """测试 Writer Agent"""
    app = create_graph()

    test_cases = [
        # {
        #     "input": "写一份关于 LangGraph 的技术报告",
        #     "expected_type": "report"
        # },
        {
            # "input": "我叫小明, KIMI帮我解决了代码BUG(KIMI-CLI 对第三方的支持模块),我需要你帮我生成一份邮件,请帮我写一封感谢邮件给KIMI团队",
            # "expected_type": "email"
        },
        # {
        #     "input": "写一篇博客介绍 RAG 技术",
        #     "expected_type": "blog"
        # },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"测试用例 {i}/{len(test_cases)}")
        print(f"输入: {test['input']}")
        print("=" * 80)

        result = app.invoke({
            "messages": [HumanMessage(content=test["input"])],
            "thread_id": f"test-writer-{i}-v3",
            "document_type": test["expected_type"]  # 可以预设文档类型
        }, config={"configurable": {"thread_id": f"test-writer-{i}-v3"}})

        # 查看结果
        intent = result.get("intent")
        outline = result.get("outline")
        final_document = result.get("final_document")

        print(f"\n识别意图: {intent}")

        if outline:
            print(f"\n📋 生成大纲:")
            print(f"  标题: {outline.get('title')}")
            print(f"  章节数: {len(outline.get('sections', []))}")
            for section in outline.get("sections", []):
                print(f"    - {section['title']}")

        if final_document:
            print(f"\n📄 最终文档（前500字）:")
            print(final_document[:500] + "...")
            print(f"\n总字数: {len(final_document)}")

        # 验证
        if intent == "generation":
            print("\n✅ 意图识别正确")
        else:
            print(f"\n⚠️  意图识别为: {intent}")

        if final_document and len(final_document) > 100:
            print("✅ 文档生成成功")
        else:
            print("❌ 文档生成失败")


if __name__ == "__main__":
    test_writer_agent()