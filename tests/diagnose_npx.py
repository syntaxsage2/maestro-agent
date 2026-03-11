"""
诊断 npx 在 Windows 上的问题
"""
import subprocess
import os
import sys

def test_npx_methods():
    """测试不同的方式调用 npx"""

    print("="*60)
    print("🔍 诊断 npx 问题")
    print("="*60)
    print(f"操作系统: {sys.platform}\n")

    # 方法1: 直接在命令行测试
    print("方法1: 在命令行测试 npx")
    print("-" * 40)
    try:
        result = subprocess.run(
            ["cmd", "/c", "npx", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"✅ 成功！npx 版本: {result.stdout.strip()}")
        print(f"   返回码: {result.returncode}")
        if result.stderr:
            print(f"   错误信息: {result.stderr}")
    except Exception as e:
        print(f"❌ 失败: {e}")

    # 方法2: 使用 npx.cmd
    print("\n方法2: 使用 npx.cmd")
    print("-" * 40)
    try:
        result = subprocess.run(
            ["npx.cmd", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"✅ 成功！npx 版本: {result.stdout.strip()}")
        print(f"   返回码: {result.returncode}")
    except FileNotFoundError:
        print(f"❌ 找不到 npx.cmd")
    except Exception as e:
        print(f"❌ 失败: {e}")

    # 方法3: 使用 shell=True
    print("\n方法3: 使用 shell=True")
    print("-" * 40)
    try:
        result = subprocess.run(
            "npx --version",
            capture_output=True,
            text=True,
            shell=True,
            timeout=5
        )
        print(f"✅ 成功！npx 版本: {result.stdout.strip()}")
        print(f"   返回码: {result.returncode}")
    except Exception as e:
        print(f"❌ 失败: {e}")

    # 方法4: 查找 npx 的位置
    print("\n方法4: 查找 npx 的位置")
    print("-" * 40)
    try:
        result = subprocess.run(
            ["cmd", "/c", "where", "npx"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ 找到 npx 位置:")
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        else:
            print(f"❌ 未找到 npx")
    except Exception as e:
        print(f"❌ 失败: {e}")

    # 方法5: 检查 Node.js
    print("\n方法5: 检查 Node.js")
    print("-" * 40)
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"✅ Node.js 版本: {result.stdout.strip()}")
    except FileNotFoundError:
        print(f"❌ 找不到 node")
    except Exception as e:
        print(f"❌ 失败: {e}")

    print("\n" + "="*60)
    print("💡 建议:")
    print("="*60)
    print("如果方法1或方法3成功，说明 npx 可用，")
    print("但需要在 Python 中使用特殊方式调用。")
    print("\n推荐使用:")
    print("  - Windows: shell=True 或 ['cmd', '/c', 'npx', ...]")
    print("  - 或使用完整路径: 'C:\\\\...\\\\npx.cmd'")

if __name__ == "__main__":
    test_npx_methods()

