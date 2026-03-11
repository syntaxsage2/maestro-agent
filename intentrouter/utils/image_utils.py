"""
图片处理工具
"""
import base64
import mimetypes
from io import BytesIO
from pathlib import Path
from typing import Union


def encode_image_to_base64(image_path: Union[str, Path]) -> str:
    """
    将本地图片编码为 base64

    Args:
        image_path: 图片路径
    Returns:
        str: base64编码图片数据
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"图片不存在: {image_path}")

    # 读取图片
    with open(image_path, "rb") as f:
        image_data = f.read()

    # 编码
    base64_data = base64.b64encode(image_data).decode("utf-8")

    # 获取MIME类型
    mime_type,_ = mimetypes.guess_type(str(image_path))
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = 'image/jpeg' # 默认

    return f"data:{mime_type}; base64,{base64_data}"


def encode_image_bytes_to_base64(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    将图片字节编为base64

    Args:
        image_bytes: 图片字节数据
        mime_type: MIME 类型
    Returns
        str: base64 编码的图片数据
    """
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{base64_data}"


def validate_image_url(url: str) -> bool:
    """
    验证图片 URL 是否有效

    Args:
        url: 图片 URL

    Returns:
        bool: 是否有效
    """

    # 支持http/https 和 data URL
    if url.startswith(("http://", "https://", "data:image/")):
        return True
    return False


def get_image_info(image_path: Union[str, Path]) -> dict:
    """
   获取图片信息

   Args:
       image_path: 图片路径

   Returns:
       dict: 图片信息
   """

    try:
        from PIL import Image
    except ImportError:
        raise ImportError("请安装 Pillow: pip install Pillow")

    path = Path(image_path)

    with Image.open(path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "size": img.size,
            "mode": img.mode,  # 色彩模式
            "file_size": path.stat().st_size,
        }


def resize_image_if_needed(
        image_bytes: bytes,
        max_size: int = 2000,
        quality: int = 85,
) -> bytes:
    """
    如果图片过大,调整大小(降低token)消耗

    Args:
        image_bytes: 图片字节
        max_size: 最大尺寸（像素）
        quality: 压缩质量（1-100）

    Returns:
        bytes: 调整后的图片字节
    """
    try:
        from PIL import Image
    except ImportError:
        # 没有 PIL，返回原图
        return image_bytes

    img = Image.open(BytesIO(image_bytes))

    # 检查是否需要调整
    if max(img.size) <= max_size:
        return image_bytes

    # 计算新尺寸
    ratio = max_size / max(img.size)
    new_size = tuple(int(dim * ratio) for dim in img.size)

    # 调整大小
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

    # 转换为字节
    output = BytesIO()
    # 图片保存到字节流中
    img_resized.save(output, format=img.format or 'JPEG', quality=quality)
    # 处理后的图片字节（可直接写入文件或通过网络传输）
    return output.getvalue()