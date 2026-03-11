"""
向量数据库管理模块
"""
from pathlib import Path
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from intentrouter.config import settings


def get_project_root() -> Path:
    """获取项目根目录（包含 pyproject.toml 的目录）"""
    current_file = Path(__file__).resolve()
    # 从当前文件向上查找，直到找到 pyproject.toml
    for parent in [current_file.parent] + list(current_file.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    # 如果没找到，返回当前工作目录
    return Path.cwd()


class VectorStoreManager:
    def __init__(
            self,
            persist_directory: str | None = None,
            collection_name: str = "knowledge_base"
    ):
        """
        初始化向量存储

        Args:
            persist_directory: 持久化目录（相对于项目根目录，或绝对路径）
            collection_name: 集合名称
        """
        # 如果没有指定路径，使用配置中的路径
        if persist_directory is None:
            persist_directory = settings.chroma_persist_directory
        
        # 转换为绝对路径
        persist_path = Path(persist_directory)
        if not persist_path.is_absolute():
            # 相对路径，基于项目根目录
            persist_path = get_project_root() / persist_directory
        
        self.persist_directory = str(persist_path)
        self.collection_name = collection_name

        # 创建目录 parents自动创建所有缺失父目录, exist_ok目录存在不报错
        persist_path.mkdir(parents=True, exist_ok=True)

        # 初始化嵌入模型
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )

        # 初始化Chroma
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
        )

    def add_document(self, document: List[Document]) -> List[str]:
        """
        添加到文档到向量数据库

        Args:
            document:文档列表

        Returns:
            文档ID列表
        """
        return self.vectorstore.add_documents(document)

    def similarity_search(self, query: str, k: int = 4, filter: Optional[dict] = None) -> List[Document]:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回文档数
            filter: 元数据过滤条件

        Returns:
            相关文档列表
        """
        return self.vectorstore.similarity_search(query, k=k, filter=filter)

    def as_retriever(self, **kwargs):
        """
        转换为Retriever接口

        Returns
            VectorStoreRetriever
        """
        return self.vectorstore.as_retriever(**kwargs)

    def delete_collection(self):
        """删除集合"""
        self.vectorstore.delete_collection()


# 单例模式
_vector_store = None


def get_vector_store() -> VectorStoreManager:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreManager()
    return _vector_store
