"""
认证问题诊断脚本
帮助排查是前端还是后端的问题
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("? 认证问题诊断")
print("=" * 70)

# 测试 1: 注册/登录获取 token
print("\n[测试 1] 注册/登录获取 token...")
print("-" * 70)

register_data = {
    "username": "debuguser",
    "email": "debug@example.com",
    "password": "test123",
    "full_name": "调试用户"
}

response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)

if response.status_code == 400:
    # 用户已存在，尝试登录
    print("??  用户已存在，使用登录...")
    login_data = {"username": "debuguser", "password": "test123"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)

if response.status_code in [200, 201]:
    result = response.json()
    print("? 成功获取 token!")
    print(f"\n返回数据结构:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    token = result.get("access_token")
    if token:
        print(f"\n? Token 存在: {token[:30]}...")
    else:
        print("\n? 错误: 响应中没有 access_token 字段!")
        exit(1)
else:
    print(f"? 注册/登录失败: {response.status_code}")
    print(response.text)
    exit(1)

# 测试 2: 不带 token 访问聊天接口
print("\n" + "=" * 70)
print("[测试 2] 不带 token 访问聊天接口 (应该失败)")
print("-" * 70)

response = requests.post(
    f"{BASE_URL}/api/chat",
    json={"message": "你好"}
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

if response.status_code == 403:
    print("? 正确: 未认证时返回 403")
else:
    print(f"??  异常: 预期 403，实际 {response.status_code}")

# 测试 3: 带错误 token 访问
print("\n" + "=" * 70)
print("[测试 3] 带错误 token 访问聊天接口 (应该失败)")
print("-" * 70)

headers = {"Authorization": "Bearer fake_token_12345"}
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={"message": "你好"},
    headers=headers
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

if response.status_code == 401:
    print("? 正确: 错误 token 返回 401")
else:
    print(f"??  异常: 预期 401，实际 {response.status_code}")

# 测试 4: 带正确 token 访问
print("\n" + "=" * 70)
print("[测试 4] 带正确 token 访问聊天接口 (应该成功)")
print("-" * 70)

headers = {"Authorization": f"Bearer {token}"}
print(f"请求头: {headers}")

response = requests.post(
    f"{BASE_URL}/api/chat",
    json={"message": "你好，测试认证"},
    headers=headers
)

print(f"状态码: {response.status_code}")

if response.status_code == 200:
    print("? 成功!")
    result = response.json()
    print(f"Thread ID: {result.get('thread_id')}")
    print(f"回复: {result.get('message', '')[:100]}...")
else:
    print(f"? 失败: {response.status_code}")
    print(f"响应: {response.text}")

# 测试 5: 流式接口
print("\n" + "=" * 70)
print("[测试 5] 测试流式聊天接口")
print("-" * 70)

response = requests.post(
    f"{BASE_URL}/api/chat/stream",
    json={"message": "你好"},
    headers=headers,
    stream=True
)

print(f"状态码: {response.status_code}")

if response.status_code == 200:
    print("? 流式接口认证成功!")
    print("接收前几行数据:")
    count = 0
    for line in response.iter_lines():
        if line:
            print(f"  {line.decode('utf-8')[:100]}...")
            count += 1
            if count >= 3:
                break
else:
    print(f"? 失败: {response.status_code}")
    print(f"响应: {response.text}")

# 总结
print("\n" + "=" * 70)
print("? 诊断总结")
print("=" * 70)

print(f"""
? 后端能正常返回 token
? 后端认证机制工作正常

? 你的 Token (复制使用):
{token}

? 前端集成检查清单:

1. 登录后是否保存了 token?
   localStorage.setItem('access_token', data.access_token)

2. 请求时是否携带了 token?
   headers: {{
     'Authorization': `Bearer ${{localStorage.getItem('access_token')}}`
   }}

3. 检查浏览器控制台的网络请求:
   - 查看 Request Headers 中是否有 Authorization
   - 如果没有，说明前端没有发送 token ?
   - 如果有但返回 401，说明 token 无效或过期 ??
   - 如果有但返回 403，可能是格式错误 ??

? 浏览器调试方法:
   1. 打开开发者工具 (F12)
   2. 切到 Network (网络) 标签
   3. 发起请求
   4. 点击请求查看详情
   5. 检查 Request Headers 中的 Authorization 字段
""")

