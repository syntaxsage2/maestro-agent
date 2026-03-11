"""
文件操作工具
"""
from pathlib import Path

from langchain_core.tools import tool

from intentrouter.config import settings

# 定义允许访问的目录（安全限制）
ALLOWED_DIRS = [
    settings.BASE_DIR,
    settings.KNOWLEDGE_BASE_DIR
]


@tool
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    读取本地文件内容。支持文本文件（txt, md, py, json 等）。

    Args:
        file_path: 文件路径（相对或绝对路径）
        encoding: 文件编码，默认 utf-8

    Returns:
        str: 文件内容
    """
    path = Path(file_path).resolve()

    # 安全检查：是否在允许的目录内
    allowed_dirs_resolved = [Path(d).resolve() for d in ALLOWED_DIRS]
    if not any(path.is_relative_to(allowed) for allowed in allowed_dirs_resolved):
        raise PermissionError(f"无权访问此文件: {file_path}")

    # 检查文件是否存在
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if not path.is_file():
        raise ValueError(f"不是文件: {file_path}")

    # 读取文件
    try:
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        return content
    except Exception as e:
        raise RuntimeError(f"读取文件失败: {str(e)}")


@tool
def delete_file(file_path: str) -> str:
    """
    删除本地文件。这是一个高风险操作，需要人工确认。

    Args:
        file_path: 文件路径（相对或绝对路径）

    Returns:
        str: 删除结果信息
    """
    path = Path(file_path).resolve()

    # 安全检查：是否在允许的目录内
    allowed_dirs_resolved = [Path(d).resolve() for d in ALLOWED_DIRS]
    if not any(path.is_relative_to(allowed) for allowed in allowed_dirs_resolved):
        raise PermissionError(f"无权删除此文件: {file_path}")

    # 检查文件是否存在
    if not path.exists():
        return f"文件不存在: {file_path}"

    if not path.is_file():
        raise ValueError(f"不是文件: {file_path}")

    # 删除文件
    try:
        path.unlink()
        return f"✓ 文件已删除: {file_path}"
    except Exception as e:
        raise RuntimeError(f"删除文件失败: {str(e)}")