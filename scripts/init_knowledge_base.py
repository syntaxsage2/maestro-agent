"""
初始化知识库脚本
"""
from intentrouter.db.document_loader import DocumentProcessor
from intentrouter.db.vector_store import get_vector_store


def main():
    print("😄 开始初始化知识库...")

    # 1.获取向量数据库
    vector_store = get_vector_store()

    # 2.加载文档
    processor = DocumentProcessor()
    documents = processor.load_text_file("data/knowledge/sample_docs.txt")

    print(f"🚢 加载了 {len(documents)} 个文档块")

    # 3.添加到向量库
    ids = vector_store.add_document(documents)

    print(f" 成功添加 {len(ids)} 个文档到知识库")
    print(f" 存储位置: {vector_store.persist_directory}")

    # 4. 测试检索
    print("\n? 测试检索...")
    test_query = "什么是 AsyncIO？"
    results = vector_store.similarity_search(test_query, k=2)

    print(f"查询: {test_query}")
    print(f"检索到 {len(results)} 个相关文档:")
    for i, doc in enumerate(results, 1):
        print(f"\n--- 文档 {i} ---")
        print(doc.page_content[:200] + "...")


if __name__ == "__main__":
    main()