"""
Vision Agent 测试
"""
from pathlib import Path
from langchain_core.messages import HumanMessage
from intentrouter.graph.main_graph import create_graph
from intentrouter.utils.image_utils import encode_image_to_base64


def test_vision_agent():
    """测试 Vision Agent"""
    app = create_graph()

    # 测试图片路径（请替换为实际图片）
    test_image_path = Path("C:/Users/94067/Desktop/微信图片_20250409222231.jpg")

    if not test_image_path.exists():
        print("⚠️ 测试图片不存在，请准备测试图片")
        print(f"预期路径: {test_image_path.absolute()}")
        return

    # 编码图片
    image_base64 = encode_image_to_base64(test_image_path)

    test_cases = [
        {
            "message": "这张图片里有什么？",
            "expected_type": "description"
        },
        # {
        #     "message": "提取图片中的所有文字",
        #     "expected_type": "ocr"
        # },
        # {
        #     "message": "分析这个图表的数据",
        #     "expected_type": "chart"
        # },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"测试用例 {i}/{len(test_cases)}")
        print(f"问题: {test['message']}")
        print("=" * 80)

        result = app.invoke({
            "messages": [HumanMessage(content=test["message"])],
            "attachments": [
                {
                    "url": image_base64,
                    "data": image_base64,
                    "name": "test.jpg",
                    "mime_type": "image/jpeg"
                }
            ],
            "thread_id": f"test-vision-{i}-5"
        }, config={"configurable": {"thread_id": f"test-vision-{i}-5"}})

        # 查看结果
        intent = result.get("intent")
        multimodal_analysis = result.get("multimodal_analysis")
        final_message = result["messages"][-1].content

        print(f"\n识别意图: {intent}")

        if multimodal_analysis:
            print(f"\n📊 多模态分析:")
            print(f"  类型: {multimodal_analysis.get('type')}")
            print(f"  图片数: {multimodal_analysis.get('images_count')}")

        print(f"\n📝 分析结果:")
        print(final_message[:500] + "...")

        # 验证
        if intent == "multimodal":
            print("\n✅ 意图识别正确")
        else:
            print(f"\n⚠️  意图识别为: {intent}")

        if multimodal_analysis:
            print("✅ 多模态分析成功")
        else:
            print("❌ 多模态分析失败")


def test_multiple_images():
    """测试多图片对比"""
    print("\n" + "=" * 80)
    print("测试多图片对比")
    print("=" * 80)

    # 准备多张图片
    # ...（类似上面的逻辑）


if __name__ == "__main__":
    test_vision_agent()