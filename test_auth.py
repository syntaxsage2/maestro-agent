"""
认证系统测试脚本
快速测试注册、登录、聊天流程
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """测试完整的认证流程"""
    
    print("=" * 60)
    print("? 测试认证系统")
    print("=" * 60)
    
    # 1. 注册新用户
    print("\n? 步骤 1: 注册新用户...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "full_name": "测试用户"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=register_data
    )
    
    if response.status_code == 201:
        print("? 注册成功!")
        result = response.json()
        token = result["access_token"]
        user = result["user"]
        print(f"   用户: {user['username']} ({user['full_name']})")
        print(f"   Token: {token[:50]}...")
    elif response.status_code == 400:
        # 用户已存在，尝试登录
        print("??  用户已存在，尝试登录...")
        
        # 2. 登录
        print("\n? 步骤 2: 用户登录...")
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data
        )
        
        if response.status_code == 200:
            print("? 登录成功!")
            result = response.json()
            token = result["access_token"]
            user = result["user"]
            print(f"   用户: {user['username']} ({user['full_name']})")
            print(f"   Token: {token[:50]}...")
        else:
            print(f"? 登录失败: {response.json()}")
            return
    else:
        print(f"? 注册失败: {response.json()}")
        return
    
    # 3. 获取用户信息
    print("\n? 步骤 3: 获取当前用户信息...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )
    
    if response.status_code == 200:
        print("? 获取成功!")
        user_info = response.json()
        print(f"   ID: {user_info['id']}")
        print(f"   用户名: {user_info['username']}")
        print(f"   邮箱: {user_info['email']}")
    else:
        print(f"? 获取失败: {response.json()}")
        return
    
    # 4. 发送聊天消息
    print("\n? 步骤 4: 发送聊天消息...")
    chat_data = {
        "message": "你好，请介绍一下你自己"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=chat_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print("? 聊天成功!")
        result = response.json()
        print(f"   Thread ID: {result['thread_id']}")
        print(f"   回复: {result['message'][:100]}...")
    else:
        print(f"? 聊天失败: {response.json()}")
        return
    
    # 5. 获取用户画像
    print("\n? 步骤 5: 获取用户画像...")
    response = requests.get(
        f"{BASE_URL}/api/auth/profile",
        headers=headers
    )
    
    if response.status_code == 200:
        print("? 获取成功!")
        profile = response.json()
        print(f"   总记忆数: {profile['total_memories']}")
        print(f"   Facts: {len(profile['facts'])}")
        print(f"   Preferences: {len(profile['preferences'])}")
        print(f"   Skills: {len(profile['skills'])}")
    else:
        print(f"? 获取失败: {response.json()}")
    
    print("\n" + "=" * 60)
    print("? 测试完成!")
    print("=" * 60)
    print(f"\n? 你的 Token (请保存):\n{token}\n")
    print("? 使用方法:")
    print('   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/chat \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"message": "你好"}\'')
    print("\n")


if __name__ == "__main__":
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("? 错误: 无法连接到 API 服务器")
        print("   请确保服务器正在运行: uvicorn intentrouter.api.main:app --reload")
    except Exception as e:
        print(f"? 错误: {e}")

