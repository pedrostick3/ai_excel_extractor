import os
from langchain_core.documents import Document
from langchain_community.chat_message_histories import ChatMessageHistory
from modules.ai.agents.pandas_dataframe_agent.schemas.pandas_dataframe_agent_response_schema import PandasDataframeAgentResponseSchema
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from modules.ai.agents.vectordb_embeddings_agent.enums.vectordb_client_service_enum import VectordbClientServiceEnum
from langchain_pinecone import PineconeVectorStore
from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata

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
        elif self.client_service == VectordbClientServiceEnum.PINECONE:
            if not os.getenv("PINECONE_API_KEY"):
                os.environ["PINECONE_API_KEY"] = VectordbClientServiceEnum.PINECONE.value["api_key"]
            if force_add_documents:
                self.embeddings_vector_llm = PineconeVectorStore.from_documents(
                    documents,
                    self.embedding_llm,
                    index_name=VectordbClientServiceEnum.PINECONE.value["index_name"],
                )
            else:
                self.embeddings_vector_llm = PineconeVectorStore.from_existing_index(
                    VectordbClientServiceEnum.PINECONE.value["index_name"],
                    self.embedding_llm,
                )
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

    def invoke_saving_and_reloading_local_FAISS_index(
        self,
        question: str,
    ) -> PandasDataframeAgentResponseSchema:
        """
        Execute the LangChain agent and return the PandasDataframeAgentResponse model response.
        """
        if not question:
            raise ValueError("Question must be provided.")
        if self.client_service != VectordbClientServiceEnum.FAISS:
            raise ValueError("Only FAISS Vector DB client is supported.")

        persist_directory = VectordbClientServiceEnum.FAISS.value["persist_directory"]
        self.embeddings_vector_llm.save_local(persist_directory)
        # saving and reloading the FAISS index locally might be useful for reusing the index without recomputing embeddings each time (but for a single query, it's redundant)
        parametrization_saved = self.embeddings_vector_llm.load_local(
            persist_directory,
            self.embedding_llm,
            allow_dangerous_deserialization=True,
        )

        return self.invoke(
            question=question,
            retriever=parametrization_saved.as_retriever(),
        )
    
    def get_chat_history(self) -> list:
        """
        Returns the chat history as a list of messages.
        """
        return self.message_history.messages if self.message_history else []
    
    #@staticmethod
    #def text_simple_example():
    #    """
    #    Simple example of embedings.
    #    """
    #    from langchain_openai import OpenAIEmbeddings
    #    import constants.configs as configs
    #
    #    # Embedings Tests
    #    embeddings_model = OpenAIEmbeddings(
    #        api_key=configs.OPENAI_API_KEY,
    #        model=configs.OPENAI_EMBEDDING_MODEL,
    #    )
    #    embeddings_model.embed_documents("Langchain", "OpenAI")
    #    embedded_query = embeddings_model.embed_query("What's the best AI framework?")
    #    print(f"embedded_query ({len(embedded_query)}) = {embedded_query})")
