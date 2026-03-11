"""
Vision Agent 调试脚本 - 诊断多模态问题
"""
import base64
from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from intentrouter import settings
from intentrouter.utils.image_utils import resize_image_if_needed


def test_basic_vision():
    """测试基础视觉能力"""
    print("=" * 80)
    print("🔍 Vision API 诊断")
    print("=" * 80)

    # 配置信息
    print(f"\n📋 当前配置:")
    print(f"  模型: {settings.model_name}")
    print(f"  Base URL: {settings.openai_base_url}")
    print(f"  API Key: {settings.openai_api_key[:10]}...{settings.openai_api_key[-4:]}")

    # 创建一个简单的测试图片（红色方块）
    test_image_base64 = create_test_image()

    print(f"\n🖼️  测试图片: 简单红色方块 (base64长度: {len(test_image_base64)})")

    # 测试不同的模型配置
    models_to_test = [
        ("gpt-4o-mini", "OpenAI GPT-4o-mini（支持视觉）"),
        ("gpt-4o", "OpenAI GPT-4o（支持视觉）"),
        ("gpt-4-vision-preview", "OpenAI GPT-4 Vision（旧版）"),
    ]

    for model_name, description in models_to_test:
        print(f"\n{'─' * 80}")
        print(f"测试模型: {model_name} - {description}")
        print("─" * 80)

        try:
            llm = init_chat_model(
                model=model_name,
                model_provider="openai",
                base_url=settings.openai_base_url,
                api_key=settings.openai_api_key,
                temperature=0.2,
            )

            # 构建多模态消息
            message = HumanMessage(content=[
                {
                    "type": "text",
                    "text": "这张图片是什么颜色的？请简短回答。"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": test_image_base64,
                        "detail": "low"  # 降低精度减少token
                    }
                }
            ])

            print("📤 发送请求...")
            response = llm.invoke([message])

            print(f"✅ 成功！响应:")
            print(f"   {response.content}")

            # 检查是否真的识别了
            if any(word in response.content.lower() for word in ["无法", "不能", "抱歉", "sorry"]):
                print("⚠️  模型返回了拒绝性回答，可能不支持视觉")
            else:
                print("✅ 模型正常识别了图片内容")

        except Exception as e:
            print(f"❌ 失败: {str(e)}")


def create_test_image():
    """创建一个简单的测试图片（红色方块）"""
    # 1x1 红色像素的 PNG（最小测试图片）
    red_pixel_png = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
        b'\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx'
        b'\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x18\xdd\x8d\xb4'
        b'\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    base64_image = base64.b64encode(red_pixel_png).decode('utf-8')
    return f"data:image/png;base64,{base64_image}"


def test_with_real_image():
    """使用真实图片测试"""
    print("\n\n" + "=" * 80)
    print("🖼️  真实图片测试")
    print("=" * 80)

    # 让用户输入图片路径
    image_path = input("\n请输入测试图片路径（直接回车跳过）: ").strip()

    if not image_path:
        print("⏭️  跳过真实图片测试")
        return

    path = Path(image_path)
    if not path.exists():
        print(f"❌ 图片不存在: {image_path}")
        return

    # 读取并编码
    with open(path, "rb") as f:
        image_data = f.read()

    print(f"📊 原始图片信息:")
    print(f"   文件大小: {len(image_data) / 1024:.2f} KB")
    
    # 压缩图片以避免 413 错误
    print("\n🔧 压缩图片...")
    compressed_data = resize_image_if_needed(image_data, max_size=800, quality=75)
    
    print(f"✅ 压缩后大小: {len(compressed_data) / 1024:.2f} KB")
    
    base64_image = base64.b64encode(compressed_data).decode('utf-8')
    data_url = f"data:image/jpeg;base64,{base64_image}"
    
    print(f"   Base64长度: {len(base64_image)}")

    try:
        llm = init_chat_model(
            model="gpt-4o-mini",
            model_provider="openai",
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )

        message = HumanMessage(content=[
            {
                "type": "text",
                "text": "请详细描述这张图片的内容。"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": data_url,
                    "detail": "high"
                }
            }
        ])

        print("\n📤 发送请求...")
        response = llm.invoke([message])

        print(f"\n✅ 响应:")
        print(response.content)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")


def test_official_api():
    """测试官方 API（对比）"""
    print("\n\n" + "=" * 80)
    print("🌐 官方 API 对比测试")
    print("=" * 80)

    print("\n如果你有 OpenAI 官方 API Key，可以对比测试：")
    official_key = input("输入官方 API Key（直接回车跳过）: ").strip()

    if not official_key:
        print("⏭️  跳过官方 API 测试")
        return

    try:
        # 使用官方 API（不设置 base_url）
        llm = init_chat_model(
            model="gpt-4o-mini",
            model_provider="openai",
            api_key=official_key,
            temperature=0.2,
        )

        test_image = create_test_image()

        message = HumanMessage(content=[
            {"type": "text", "text": "这是什么颜色？"},
            {
                "type": "image_url",
                "image_url": {"url": test_image, "detail": "low"}
            }
        ])

        print("\n📤 调用官方 API...")
        response = llm.invoke([message])

        print(f"✅ 官方 API 响应:")
        print(f"   {response.content}")

    except Exception as e:
        print(f"❌ 官方 API 错误: {str(e)}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║            Vision API 多模态功能诊断工具                      ║
╚══════════════════════════════════════════════════════════════╝

本工具将帮助你诊断多模态 API 是否正常工作。

""")

    # 运行测试
    test_basic_vision()
    test_with_real_image()
    test_official_api()

    print("\n\n" + "=" * 80)
    print("📋 诊断总结")
    print("=" * 80)
    print("""
如果所有测试都失败，可能的原因：

1. ❌ 第三方 API 不支持多模态
   → 解决：更换支持视觉的 API 提供商，或使用官方 API

2. ❌ 模型名称配置错误
   → 解决：询问 API 提供商正确的视觉模型名称

3. ❌ Base64 图片过大
   → 解决：压缩图片或使用图片 URL

4. ❌ API 额度不足或权限问题
   → 解决：检查账户状态

推荐解决方案：
✅ 使用官方 OpenAI API
✅ 或使用可靠的支持多模态的第三方服务（如 OneAPI、API2D）
""")

