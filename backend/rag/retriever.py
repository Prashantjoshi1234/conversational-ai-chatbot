from typing import List
from langchain_core.documents import Document

from rag.vector_store import get_retriever


class RAGRetriever:
    def __init__(self, top_k: int = 4):
        """
        Initializes retriever with top_k results
        """
        self.retriever = get_retriever(k=top_k)

    def retrieve(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents for a user query
        """
        if not query or not query.strip():
            return []

        documents = self.retriever.invoke(query)
        return documents
