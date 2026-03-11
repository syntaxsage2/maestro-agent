"""
Streamlit 聊天界面
"""
import streamlit as st
import requests
import json
import uuid
from datetime import datetime

# 配置
API_BASE_URL = "http://localhost:8000"

# 页面配置
st.set_page_config(
    page_title="IntentRouter Pro",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session_state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}  # {thread_id: messages}


def call_chat_api(message: str, thread_id: str) -> dict:
    """调用聊天 API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "thread_id": thread_id
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def load_history(thread_id: str) -> list:
    """加载历史记录"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/history/{thread_id}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("messages", [])
        return []
    except:
        return []


# ===== 侧边栏 =====
with st.sidebar:
    st.title("💬 IntentRouter Pro")

    st.markdown("---")

    # 当前会话信息
    st.subheader("📌 当前会话")
    st.text(f"ID: {st.session_state.thread_id[:8]}...")

    # 新建会话按钮
    if st.button("➕ 新建会话", use_container_width=True):
        # 保存当前会话到历史
        if st.session_state.messages:
            st.session_state.chat_history[st.session_state.thread_id] = {
                "messages": st.session_state.messages.copy(),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

        # 创建新会话
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # 历史会话
    st.subheader("📚 历史会话")
    if st.session_state.chat_history:
        for tid, session in list(st.session_state.chat_history.items()):
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(
                        f"🕐 {session['time']}",
                        key=f"history_{tid}",
                        use_container_width=True
                ):
                    st.session_state.thread_id = tid
                    st.session_state.messages = session["messages"]
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{tid}"):
                    del st.session_state.chat_history[tid]
                    st.rerun()
    else:
        st.info("暂无历史会话")

    st.markdown("---")

    # 清空所有
    if st.button("🗑️ 清空所有会话", use_container_width=True):
        st.session_state.chat_history = {}
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# ===== 主聊天区域 =====
st.title("💬 Agent 对话系统")

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # 显示元数据（如果有）
        if "metadata" in msg and msg["metadata"]:
            with st.expander("📊 详细信息"):
                st.json(msg["metadata"])

# 聊天输入
if prompt := st.chat_input("请输入您的问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # 调用 API
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            result = call_chat_api(prompt, st.session_state.thread_id)

            if "error" in result:
                st.error(f"❌ 错误: {result['error']}")
            else:
                # 显示回复
                st.markdown(result["message"])

                # 显示元数据
                metadata = {
                    "意图": result.get("intent"),
                    "路由": result.get("route"),
                    "检索文档数": result.get("retrieved_docs_count", 0)
                }

                with st.expander("📊 详细信息"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("意图", metadata["意图"] or "未知")
                    col2.metric("路由", metadata["路由"] or "未知")
                    col3.metric("文档数", metadata["检索文档数"])

                # 保存助手消息
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["message"],
                    "metadata": metadata
                })

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>IntentRouter Pro v0.1.0 | Powered by LangGraph & FastAPI</small>
    </div>
    """,
    unsafe_allow_html=True
)