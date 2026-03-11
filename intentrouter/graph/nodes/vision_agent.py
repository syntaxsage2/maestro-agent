"""
Vision Agent 节点 - 通用多模态图片理解
支持 OpenAI、Claude、GLM 等多种视觉模型
"""
import base64
import re
import httpx
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage

from intentrouter.config import settings
from intentrouter.graph.prompts import (
    VISION_UNDERSTANDING_PROMPT,
    IMAGE_DESCRIPTION_PROMPT,
    OCR_EXTRACTION_PROMPT,
    CHART_ANALYSIS_PROMPT
)
from intentrouter.graph.state import AgentState
from intentrouter.utils.image_utils import resize_image_if_needed


# 模型配置
VISION_MODEL_CONFIG = {
    "model": "claude-sonnet-4-20250514",  # 可选: gpt-4o, gpt-4o-mini, GLM-4.5V, claude-sonnet-4-5-20250929
    "base_url": "https://aizex.top/v1",
    "api_key": "sk-VtnVdUQasp09RErRFIdKaRCOI7oLN5CIwkazx5PRHpCzVwpN",
}


def vision_agent_node(state: AgentState) -> dict:
    """
    Vision Agent 节点 - 使用多模态模型处理图片

    流程:
    1. 提取图片附件
    2. 构建多模态消息
    3. 根据用户意图选择分析类型
    4. 调用视觉模型 API
    5. 返回分析结果

    Args:
        state: Agent 状态

    Returns:
        dict: 状态更新
    """

    # 1. 提取信息
    attachments = state.get("attachments", [])
    user_message = state["messages"][-1].content

    if not attachments:
        return {
            "error": "没有图片附件",
            "messages": [AIMessage(content="❌ 请上传图片")]
        }

    # 2. 判断分析类型
    analysis_type = _detect_analysis_type(user_message)

    # 3. 调用视觉模型
    analysis_result = _analyze_with_vision(
        user_query=user_message,
        attachments=attachments,
        analysis_type=analysis_type
    )

    # 4. 格式化结果
    formatted_result = _format_analysis_result(
        result=analysis_result,
        analysis_type=analysis_type,
        image_count=len(attachments)
    )

    return {
        "multimodal_analysis": {
            "type": analysis_type,
            "images_count": len(attachments),
            "result": analysis_result
        },
        "messages": [AIMessage(content=formatted_result)]
    }


def _detect_analysis_type(user_query: str) -> str:
    """
    检测用户想要的分析类型

    Args:
        user_query: 用户查询

    Returns:
        str: 分析类型
    """
    query_lower = user_query.lower()

    # OCR相关关键词
    if any(kw in user_query for kw in ["提取文字", "识别文字", "ocr", "读取文字", "文字内容"]):
        return "ocr"

    # 图表分析关键词
    if any(kw in query_lower for kw in ["图表", "数据", "分析图", "统计", "趋势"]):
        return "chart"

    # 对比分析关键词
    if any(kw in query_lower for kw in ["对比", "比较", "差异", "区别"]):
        return "comparison"

    # 描述关键词
    if any(kw in query_lower for kw in ["描述", "是什么", "看到什么", "这是"]):
        return "description"

    # 默认：视觉问答
    return "vqa"


def _get_model_provider(model_name: str) -> Literal["openai", "claude", "glm"]:
    """
    根据模型名称判断提供商

    Args:
        model_name: 模型名称

    Returns:
        str: 提供商类型
    """
    model_lower = model_name.lower()
    
    if "claude" in model_lower or "sonnet" in model_lower:
        return "claude"
    elif "glm" in model_lower:
        return "glm"
    else:
        return "openai"


def _analyze_with_vision(
    user_query: str,
    attachments: list[dict],
    analysis_type: str
) -> str:
    """
    使用视觉模型分析 - 通用方法

    Args:
        user_query: 用户查询
        attachments: 图片附件
        analysis_type: 分析类型

    Returns:
        str: 分析结果
    """
    model_name = VISION_MODEL_CONFIG["model"]
    provider = _get_model_provider(model_name)

    print(f"🤖 使用模型: {model_name} (提供商: {provider})")

    # 根据不同提供商构建消息
    if provider == "claude":
        return _call_claude_vision(user_query, attachments, analysis_type)
    elif provider == "glm":
        return _call_glm_vision(user_query, attachments, analysis_type)
    else:
        return _call_openai_vision(user_query, attachments, analysis_type)


def _call_openai_vision(
    user_query: str,
    attachments: list[dict],
    analysis_type: str
) -> str:
    """调用 OpenAI 格式的 API (包括 GLM)"""
    # 选择 prompt
    text_prompt = _get_prompt(user_query, analysis_type)

    # OpenAI 格式的消息
    content = [{"type": "text", "text": text_prompt}]

    for attachment in attachments:
        image_url = attachment.get("url") or attachment.get("data")
        if image_url:
            compressed_url = _compress_image_url(image_url)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": compressed_url
                }
            })

    # 构建请求（智能处理 base_url）
    base_url = VISION_MODEL_CONFIG['base_url'].rstrip('/')
    # 如果 base_url 已经包含 /v1，就不再添加
    if base_url.endswith('/v1'):
        url = f"{base_url}/chat/completions"
    else:
        url = f"{base_url}/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {VISION_MODEL_CONFIG['api_key']}"
    }

    payload = {
        "model": VISION_MODEL_CONFIG["model"],
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.1,
        "max_tokens": 1024
    }

    return _make_http_request(url, headers, payload)


def _call_glm_vision(
    user_query: str,
    attachments: list[dict],
    analysis_type: str
) -> str:
    """调用 GLM 格式的 API"""
    # GLM 使用 OpenAI 兼容格式
    return _call_openai_vision(user_query, attachments, analysis_type)


def _call_claude_vision(
    user_query: str,
    attachments: list[dict],
    analysis_type: str
) -> str:
    """调用 Claude 格式的 API"""
    # 选择 prompt
    text_prompt = _get_prompt(user_query, analysis_type)

    # Claude 格式的消息
    content = [{"type": "text", "text": text_prompt}]

    print(f"🔍 [调试] attachments 数量: {len(attachments)}")
    for idx, attachment in enumerate(attachments):
        print(f"🔍 [调试] attachment[{idx}] 键: {attachment.keys()}")
        
        image_url = attachment.get("url") or attachment.get("data")
        print(f"🔍 [调试] image_url 前缀: {image_url[:50] if image_url else 'None'}")
        
        if image_url:
            # 压缩图片
            compressed_url = _compress_image_url(image_url)
            
            # 解析 base64 数据
            if compressed_url.startswith("data:image/"):
                # 兼容 "data:image/jpeg;base64," 和 "data:image/jpeg; base64," 两种格式
                match = re.match(r'data:image/(\w+);\s*base64,(.+)', compressed_url)
                if match:
                    media_type = f"image/{match.group(1)}"
                    base64_data = match.group(2)
                    
                    print(f"✅ [调试] 成功解析图片: {media_type}, base64长度: {len(base64_data)}")
                    
                    # Claude 格式
                    image_block = {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_data  # 注意：不包含 data:image/... 前缀
                        }
                    }
                    content.append(image_block)
                    print(f"✅ [调试] 已添加图片到 content")
                else:
                    print(f"❌ [调试] 无法解析 base64 格式")
            else:
                print(f"❌ [调试] 图片不是 data:image/ 格式: {compressed_url[:100]}")

    # 构建请求（智能处理 base_url）
    base_url = VISION_MODEL_CONFIG['base_url'].rstrip('/')
    # 如果 base_url 已经包含 /v1，就不再添加
    if base_url.endswith('/v1'):
        url = f"{base_url}/messages"
    else:
        url = f"{base_url}/v1/messages"
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": VISION_MODEL_CONFIG['api_key'],
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": VISION_MODEL_CONFIG["model"],
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 1024
    }

    print(f"🔍 [调试] 最终 content 长度: {len(content)}")
    for idx, item in enumerate(content):
        print(f"🔍 [调试] content[{idx}] type: {item.get('type')}")

    try:
        print(f"📤 发送 Claude 请求到: {url}")
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Claude 响应格式
            if "content" in result and len(result["content"]) > 0:
                return result["content"][0]["text"]
            else:
                return f"Claude API 返回格式异常: {result}"

    except httpx.HTTPStatusError as e:
        return f"HTTP 错误 {e.response.status_code}: {e.response.text}"
    except Exception as e:
        import traceback
        return f"请求失败: {str(e)}\n{traceback.format_exc()}"


def _make_http_request(url: str, headers: dict, payload: dict) -> str:
    """
    发送 HTTP 请求的通用方法

    Args:
        url: API URL
        headers: 请求头
        payload: 请求体

    Returns:
        str: API 响应内容
    """
    try:
        print(f"📤 发送请求到: {url}")
        print(f"📊 Payload 大小: {len(str(payload)) / 1024:.1f} KB")
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # OpenAI 格式响应
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"API 返回格式异常: {result}"

    except httpx.HTTPStatusError as e:
        return f"HTTP 错误 {e.response.status_code}: {e.response.text}"
    except Exception as e:
        import traceback
        return f"请求失败: {str(e)}\n{traceback.format_exc()}"


def _get_prompt(user_query: str, analysis_type: str) -> str:
    """获取 prompt"""
    prompt_map = {
        "ocr": OCR_EXTRACTION_PROMPT,
        "chart": CHART_ANALYSIS_PROMPT,
        "description": IMAGE_DESCRIPTION_PROMPT,
        "vqa": VISION_UNDERSTANDING_PROMPT.format(user_query=user_query),
        "comparison": f"请对比分析这些图片。用户问题：{user_query}"
    }

    return prompt_map.get(analysis_type, VISION_UNDERSTANDING_PROMPT.format(user_query=user_query))


def _format_analysis_result(result: str, analysis_type: str, image_count: int) -> str:
    """
    格式化分析结果

    Args:
        result: 原始分析结果
        analysis_type: 分析类型
        image_count: 图片数量

    Returns:
        str: 格式化后的结果
    """

    type_names = {
        "ocr": "📝 文字提取",
        "chart": "📊 图表分析",
        "description": "🖼️ 图片描述",
        "vqa": "🔍 视觉问答",
        "comparison": "🔀 对比分析"
    }

    type_name = type_names.get(analysis_type,  "🔍 图片分析")

    lines = [
        f"## {type_name}",
        f"*分析了 {image_count} 张图片*",
        "",
        "---",
        "",
        result
    ]

    return "\n".join(lines)


def _compress_image_url(image_url: str, max_size: int = 800, quality: int = 75) -> str:
    """
    压缩 base64 图片以减少请求体大小
    
    Args:
        image_url: 图片 URL (data:image/...;base64,...)
        max_size: 最大边长（像素）
        quality: JPEG 压缩质量（1-100）
    
    Returns:
        str: 压缩后的图片 URL
    """
    # 如果不是 base64 格式，直接返回
    if not image_url.startswith("data:image/"):
        return image_url
    
    try:
        # 解析 base64 数据（兼容有空格和无空格两种格式）
        match = re.match(r'data:image/(\w+);\s*base64,(.+)', image_url)
        if not match:
            return image_url
        
        image_format = match.group(1)
        base64_data = match.group(2)
        
        # 解码图片
        image_bytes = base64.b64decode(base64_data)
        
        # 检查图片大小
        original_size_kb = len(image_bytes) / 1024
        print(f"📊 原始图片大小: {original_size_kb:.1f} KB")
        
        # 如果图片小于 500KB，直接返回
        if original_size_kb < 500:
            print("✅ 图片大小合适，无需压缩")
            return image_url
        
        # 压缩图片
        compressed_bytes = resize_image_if_needed(
            image_bytes, 
            max_size=max_size, 
            quality=quality
        )
        
        compressed_size_kb = len(compressed_bytes) / 1024
        print(f"✅ 压缩后大小: {compressed_size_kb:.1f} KB (节省 {original_size_kb - compressed_size_kb:.1f} KB)")
        
        # 重新编码为 base64
        compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
        return f"data:image/jpeg;base64,{compressed_base64}"
        
    except Exception as e:
        print(f"⚠️  图片压缩失败，使用原图: {str(e)}")
        return image_url
