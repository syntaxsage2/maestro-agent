"""
用户会话隔离和用户画像功能测试脚本
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api"

def test_user_isolation():
    """测试用户会话隔离功能"""

    print("=" * 80)
    print("测试1: 用户会话隔离")
    print("=" * 80)

    # 1. 创建两个测试用户并登录
    print("\n步骤1: 创建并登录两个用户...")

    # 用户A
    try:
        requests.post(f"{BASE_URL}/auth/register", json={
            "username": "test_userA",
            "email": "userA@test.com",
            "password": "password123",
            "full_name": "测试用户A"
        })
    except:
        pass

    response_a = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "test_userA",
        "password": "password123"
    })
    token_a = response_a.json()["access_token"]
    print(f"✅ 用户A登录成功")

    # 用户B
    try:
        requests.post(f"{BASE_URL}/auth/register", json={
            "username": "test_userB",
            "email": "userB@test.com",
            "password": "password123",
            "full_name": "测试用户B"
        })
    except:
        pass

    response_b = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "test_userB",
        "password": "password123"
    })
    token_b = response_b.json()["access_token"]
    print(f"✅ 用户B登录成功")

    # 2. 两个用户使用相同的thread_id发送对话
    print("\n步骤2: 两个用户使用相同的thread_id发送对话...")

    thread_id = "isolation_test_001"

    # 用户A的对话
    response_a = requests.post(f"{BASE_URL}/chat",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "message": "我叫张三，我是一名Python开发者",
            "thread_id": thread_id
        }
    )
    print(f"✅ 用户A发送消息: '我叫张三，我是一名Python开发者'")
    
    response_a_data = response_a.json()
    ai_reply_a = response_a_data.get('message', '')
    print(f"   AI回复: {ai_reply_a[:100]}...")

    # 用户B的对话 (使用相同的thread_id)
    response_b = requests.post(f"{BASE_URL}/chat",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "message": "我叫李四，我是一名Java开发者",
            "thread_id": thread_id
        }
    )
    print(f"✅ 用户B发送消息: '我叫李四，我是一名Java开发者' (相同thread_id)")
    
    response_b_data = response_b.json()
    ai_reply_b = response_b_data.get('message', '')
    print(f"   AI回复: {ai_reply_b[:100]}...")

    # 3. 验证会话隔离
    print("\n步骤3: 验证会话是否隔离...")
    
    import time
    time.sleep(1)  # 等待数据库写入

    # 用户A查询历史
    try:
        response_a = requests.get(f"{BASE_URL}/history/{thread_id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        history_a = response_a.json()
        print(f"✅ 用户A查询历史成功 (状态码: {response_a.status_code})")
    except Exception as e:
        print(f"⚠️  用户A查询历史失败: {e}")
        history_a = {}

    # 用户B查询历史
    try:
        response_b = requests.get(f"{BASE_URL}/history/{thread_id}",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        history_b = response_b.json()
        print(f"✅ 用户B查询历史成功 (状态码: {response_b.status_code})")
    except Exception as e:
        print(f"⚠️  用户B查询历史失败: {e}")
        history_b = {}

    # 检查隔离
    messages_a = [msg["content"] for msg in history_a.get("messages", [])]
    messages_b = [msg["content"] for msg in history_b.get("messages", [])]

    has_zhangsan_in_a = any("张三" in msg for msg in messages_a)
    has_lisi_in_b = any("李四" in msg for msg in messages_b)
    has_lisi_in_a = any("李四" in msg for msg in messages_a)
    has_zhangsan_in_b = any("张三" in msg for msg in messages_b)

    print(f"\n用户A的历史记录:")
    for msg in history_a.get("messages", []):
        print(f"  - [{msg.get('role', 'unknown')}] {msg.get('content', '')[:80]}...")
    
    print(f"\n用户B的历史记录:")
    for msg in history_b.get("messages", []):
        print(f"  - [{msg.get('role', 'unknown')}] {msg.get('content', '')[:80]}...")
    
    # 调试信息
    print(f"\n调试信息:")
    print(f"  用户A历史响应: {history_a}")
    print(f"  用户B历史响应: {history_b}")

    print("\n" + "=" * 80)
    print("隔离测试结果:")
    print("=" * 80)

    if has_zhangsan_in_a and not has_lisi_in_a:
        print("✅ 用户A的历史只包含自己的消息")
    else:
        print("❌ 用户A的历史包含了用户B的消息")

    if has_lisi_in_b and not has_zhangsan_in_b:
        print("✅ 用户B的历史只包含自己的消息")
    else:
        print("❌ 用户B的历史包含了用户A的消息")

    if has_zhangsan_in_a and has_lisi_in_b and not has_lisi_in_a and not has_zhangsan_in_b:
        print("\n🎉 会话隔离测试通过！")
        return True
    else:
        print("\n❌ 会话隔离测试失败！")
        return False


def test_user_profile():
    """测试用户画像加载功能"""

    print("\n" + "=" * 80)
    print("测试2: 用户画像加载")
    print("=" * 80)

    # 1. 登录
    print("\n步骤1: 登录用户...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "test_userA",
        "password": "password123"
    })
    token = response.json()["access_token"]
    print("✅ 登录成功")

    # 2. 添加用户记忆
    print("\n步骤2: 添加用户记忆...")
    from intentrouter.db.user_manager import get_user_manager
    from intentrouter.db.ltm_manager import get_ltm_manager

    # 获取用户ID
    user_manager = get_user_manager()
    user = user_manager.get_user_by_username("test_userA")
    user_id = str(user.id)

    # 添加记忆
    ltm_manager = get_ltm_manager()

    # 先清空旧记忆
    old_memories = ltm_manager.get_user_memories(user_id, limit=100)
    for mem in old_memories:
        ltm_manager.delete_memory(mem.id)

    # 添加新记忆
    memories = [
        {"type": "fact", "content": "我叫张三", "importance": 0.9},
        {"type": "fact", "content": "我是一名AI工程师", "importance": 0.9},
        {"type": "skill", "content": "擅长Python和LangGraph", "importance": 0.8},
    ]

    for mem in memories:
        ltm_manager.add_memory(
            user_id=user_id,
            memory_type=mem["type"],
            content=mem["content"],
            importance=mem["importance"]
        )

    print(f"✅ 为用户 {user_id} 添加了 {len(memories)} 条记忆")

    # 3. 新建会话测试
    print("\n步骤3: 新建会话，测试AI是否能识别用户...")

    response = requests.post(f"{BASE_URL}/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "你知道我是谁吗？我的技能是什么？",
            "thread_id": "profile_test_001"  # 新的thread_id
        }
    )

    response_data = response.json()
    ai_reply = response_data.get("message", "")
    print(f"\n🤖 AI回复:\n{ai_reply}")

    # 4. 验证
    print("\n" + "=" * 80)
    print("用户画像测试结果:")
    print("=" * 80)

    has_name = "张三" in ai_reply
    has_skill = "Python" in ai_reply or "LangGraph" in ai_reply

    if has_name:
        print("✅ AI识别出了用户名字")
    else:
        print("❌ AI没有识别出用户名字")

    if has_skill:
        print("✅ AI识别出了用户技能")
    else:
        print("❌ AI没有识别出用户技能")

    if has_name and has_skill:
        print("\n🎉 用户画像加载测试通过！")
        return True
    else:
        print("\n❌ 用户画像加载测试失败！")
        print("\n💡 提示: 请检查以下几点:")
        print("   1. Entry节点是否正确加载了用户画像")
        print("   2. Output节点是否使用了用户画像")
        print("   3. 数据库中是否有用户记忆记录")
        return False


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  用户会话隔离和用户画像功能测试                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # 测试1: 会话隔离
        result1 = test_user_isolation()

        # 测试2: 用户画像
        result2 = test_user_profile()

        # 总结
        print("\n" + "=" * 80)
        print("总结")
        print("=" * 80)

        if result1 and result2:
            print("🎉 所有测试通过！")
        else:
            print("❌ 部分测试失败，请检查上述问题")

    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

