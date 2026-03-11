"""
用户画像功能诊断脚本
检查用户画像加载是否正常
"""
import asyncio
from intentrouter.db.user_manager import get_user_manager
from intentrouter.db.ltm_manager import get_ltm_manager
from intentrouter.graph.main_graph import create_graph
from langchain_core.messages import HumanMessage


def check_user_memories():
    """检查数据库中的用户记忆"""
    print("=" * 80)
    print("步骤1: 检查数据库中的用户记忆")
    print("=" * 80)

    try:
        # 获取用户管理器
        user_manager = get_user_manager()

        # 列出所有用户
        print("\n📋 查询所有用户...")
        from intentrouter.db.checkpointer import _checkpointer_manager
        if _checkpointer_manager is None:
            from intentrouter.db.checkpointer import get_checkpointer
            get_checkpointer()

        with _checkpointer_manager.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, email FROM users LIMIT 10")
                users = cur.fetchall()

                if not users:
                    print("❌ 没有找到任何用户")
                    return None

                print(f"✅ 找到 {len(users)} 个用户:")
                for user_id, username, email in users:
                    print(f"   - ID: {user_id}, 用户名: {username}, 邮箱: {email}")

                # 使用第一个用户进行测试
                test_user_id = users[0][0]
                test_username = users[0][1]

                print(f"\n🔍 检查用户 {test_username} (ID: {test_user_id}) 的记忆...")

                # 查询用户记忆
                ltm_manager = get_ltm_manager()
                memories = ltm_manager.get_user_memories(str(test_user_id), limit=20)

                if not memories:
                    print(f"⚠️  用户 {test_username} 没有任何记忆记录")
                    print("\n💡 提示: 您需要先添加一些用户记忆，例如:")
                    print(f"""
from intentrouter.db.ltm_manager import get_ltm_manager
ltm = get_ltm_manager()
ltm.add_memory(
    user_id="{test_user_id}",
    memory_type="fact",
    content="我是一名Python开发者",
    importance=0.9
)
ltm.add_memory(
    user_id="{test_user_id}",
    memory_type="skill",
    content="擅长FastAPI和LangGraph",
    importance=0.8
)
                    """)
                    return test_user_id

                print(f"✅ 找到 {len(memories)} 条记忆:")
                for mem in memories:
                    print(f"   - [{mem.memory_type}] {mem.content} (重要度: {mem.importance})")

                return test_user_id

    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_graph_with_user_id(user_id: str):
    """测试图执行时是否正确加载用户画像"""
    print("\n" + "=" * 80)
    print("步骤2: 测试图执行时的用户画像加载")
    print("=" * 80)

    try:
        app = create_graph()

        test_messages = [
            "我是谁？",
            "你知道我的技能吗？",
            "我的背景是什么？"
        ]

        for msg in test_messages:
            print(f"\n📤 测试消息: {msg}")
            print("-" * 80)

            result = app.invoke({
                "messages": [HumanMessage(content=msg)],
                "user_id": str(user_id)
            })

            # 检查用户画像是否被加载
            user_context = result.get("metadata", {}).get("user_context", "")
            if user_context:
                print(f"✅ 用户画像已加载:\n{user_context}")
            else:
                print("❌ 用户画像未加载")

            # 打印AI回复
            assistant_reply = result["messages"][-1].content
            print(f"\n🤖 AI回复:\n{assistant_reply}")
            print("-" * 80)

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def add_sample_memories(user_id: str):
    """为用户添加示例记忆"""
    print("\n" + "=" * 80)
    print("步骤3: 添加示例用户记忆")
    print("=" * 80)

    try:
        ltm_manager = get_ltm_manager()

        sample_memories = [
            {
                "type": "fact",
                "content": "我叫测试用户",
                "importance": 0.9
            },
            {
                "type": "fact",
                "content": "我是一名AI工程师",
                "importance": 0.9
            },
            {
                "type": "skill",
                "content": "擅长Python、FastAPI和LangGraph",
                "importance": 0.8
            },
            {
                "type": "skill",
                "content": "了解向量数据库和RAG技术",
                "importance": 0.7
            },
            {
                "type": "preference",
                "content": "喜欢使用简洁的代码风格",
                "importance": 0.6
            },
            {
                "type": "preference",
                "content": "偏好使用GPT-4模型",
                "importance": 0.5
            }
        ]

        print(f"📝 为用户 {user_id} 添加 {len(sample_memories)} 条记忆...")

        for mem in sample_memories:
            mem_id = ltm_manager.add_memory(
                user_id=str(user_id),
                memory_type=mem["type"],
                content=mem["content"],
                importance=mem["importance"]
            )
            print(f"   ✅ 添加: [{mem['type']}] {mem['content']} (ID: {mem_id})")

        print(f"\n✅ 成功添加所有记忆!")

    except Exception as e:
        print(f"❌ 添加记忆失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        用户画像功能诊断工具                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # 步骤1: 检查用户记忆
    user_id = check_user_memories()

    if user_id is None:
        print("\n❌ 无法继续测试，请先创建用户")
        return

    # 询问是否添加示例记忆
    print("\n" + "=" * 80)
    response = input("是否要添加示例用户记忆? (y/n): ").strip().lower()
    if response == 'y':
        add_sample_memories(user_id)

    # 步骤2: 测试图执行
    print("\n" + "=" * 80)
    response = input("是否要测试图执行? (y/n): ").strip().lower()
    if response == 'y':
        test_graph_with_user_id(user_id)

    print("\n" + "=" * 80)
    print("✅ 诊断完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()

