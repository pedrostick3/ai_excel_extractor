import logging
from langchain_core.documents import Document
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from modules.ai.core.agents.vectordb_embeddings_agent.enums.vectordb_client_service_enum import VectordbClientServiceEnum
from langchain_chroma import Chroma

class VectordbEmbeddingsAgent:
    """
    This class is a LangChain implementation of Vector DB with embeddings.
    """

    def __init__(
        self,
        embedding_llm,
        retrieval_llm,
        documents: list[Document] = [],
        save_chat_history: bool = False,
        client_service: VectordbClientServiceEnum = VectordbClientServiceEnum.FAISS,
        force_add_documents: bool = False,
        collection_name: str = None,
    ):
        """
        Initialize the AI Agent.
        """
        self.embedding_llm = embedding_llm
        self.retrieval_llm = retrieval_llm
        self.client_service = client_service

        if self.client_service == VectordbClientServiceEnum.FAISS:
            self.embeddings_vector_llm = FAISS.from_documents(documents, self.embedding_llm)
        elif self.client_service == VectordbClientServiceEnum.CHROMA:
            if force_add_documents:
                self.embeddings_vector_llm = Chroma.from_documents(
                    documents,
                    self.embedding_llm,
                    persist_directory=VectordbClientServiceEnum.CHROMA.value["persist_directory"],
                    collection_name=collection_name if collection_name else VectordbClientServiceEnum.CHROMA.value["collection_name"],
                )
            else:
                self.embeddings_vector_llm = Chroma(
                    embedding_function=self.embedding_llm,
                    persist_directory=VectordbClientServiceEnum.CHROMA.value["persist_directory"],
                    collection_name=collection_name if collection_name else VectordbClientServiceEnum.CHROMA.value["collection_name"],
                )

        # RetrievalQA or RetrievalQAWithSourcesChain uses the LLM to interpret both the query and the retrieved documents, potentially leading to more accurate answers by synthesizing information.
        self.qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.retrieval_llm,
            retriever=self.embeddings_vector_llm.as_retriever(),
            return_source_documents=True, # True to return searched documents
        )

        self.session_id = "VectordbEmbeddingsAgent"  # for History & Traceability purposes
        self.message_history = ChatMessageHistory() if save_chat_history else None
        

    def invoke_similarity_search_with_score(
        self,
        question: str,
    ):
        """
        Finds text chunks similar to the query.
        The score should be near 0 for better results.
        """
        if not question:
            raise ValueError("Question must be provided.")

        return self.embeddings_vector_llm.similarity_search_with_score(question)
    
    def invoke(
        self,
        question: str,
    ):
        """
        Execute the LangChain agent and return the response.
        """
        if not question:
            raise ValueError("Question must be provided.")

        if self.message_history:
            self.message_history.add_user_message(question)

        response = self.qa_chain.invoke(question)

        if self.message_history:
            self.message_history.add_ai_message(response["output"])

        return response
    
    def get_all_vectors_and_info(self):
        """
        Returns all vectors and their informations from the Vector DB.
        """
        return self.embeddings_vector_llm.get()
    
    def get_chat_history(self) -> list:
        """
        Returns the chat history as a list of messages.
        """
        return self.message_history.messages if self.message_history else []

    def collection_exists(self) -> bool:
        """
        Checks if the collection exists AND contains data in the vector database.
        Returns True only if both conditions are met.
        """
        try:
            if self.client_service == VectordbClientServiceEnum.FAISS:
                return (
                    hasattr(self.embeddings_vector_llm, 'index') and 
                    self.embeddings_vector_llm.index is not None and 
                    self.embeddings_vector_llm.index.ntotal > 0  # Check for data presence
                )
            elif self.client_service == VectordbClientServiceEnum.CHROMA:
                return (
                    hasattr(self.embeddings_vector_llm, '_collection') and 
                    self.embeddings_vector_llm._collection is not None and 
                    self.embeddings_vector_llm._collection.count() > 0  # Check for data presence
                )
            else:
                logging.warning(f"Unsupported client service: {self.client_service}")
                return False
        except Exception as e:
            logging.warning(f"Collection existence check failed: {str(e)}")
            return False
