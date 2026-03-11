"""
文档加载与处理模块
"""
from typing import List

from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    """文档处理器"""
    def __init__(
            self,
            chunk_size: int = 1000,
            chunk_overlap: int = 200
    ):
        """
        初始化文档处理器

        Args:
            chunk_size: 文本块大小
            chunk_overlap: 重叠大小
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]  # 分割文本时优先使用的分隔符列表，按优先级从高到低排列
        )

    def load_text_file(self, file_path: str) -> List[Document]:
        """
        加载文本文件

        Args:
            file_path: 文件路径

        Returns:
            文档列表
        """
        loader = TextLoader(file_path=file_path, encoding="utf-8")
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def load_PDF_file(self, file_path: str) -> List[Document]:
        """
        加载PDF文件

        Args:
           file_path: 文件路径

        Returns:
           文档列表
       """
        loader = PyPDFLoader(file_path=file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def load_directory(
            self,
            directory_path: str,
            glob: str = "**/*.txt"
    ) -> List[Document]:
        """
        加载目录下的所有文档

        Args:
            directory_path: 目录路径
            glob: 文件匹配模式

        Returns:
            文档列表
        """
        loader = DirectoryLoader(
            path=directory_path,
            glob=glob,
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def create_document_from_text(
            self,
            texts: List[str],
            metadatas: List[dict] = None,
    ) -> List[Document]:
        """
        从文本列表创建文档

        Args:
            text:文本列表
            metadatas: 元数据列表

        Returns:
            文档列表
        """
        documents = [
            Document(
                page_content=text,
                metadata=metadatas[i] if metadatas else {}
            ) for i, text in enumerate(texts)
        ]
        return self.text_splitter.split_documents(documents)







