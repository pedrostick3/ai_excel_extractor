from enum import Enum
import constants.configs as configs

class VectordbClientServiceEnum(Enum):
    """
    Enum for the different Vectordb client services.
    """

    UNKNOWN = {"description": "Unknown"}
    FAISS = {
        "description": "LangChain FAISS vector database service",
        "persist_directory": f"{configs.VECTOR_DB_STORAGE}/faiss_index_parametrization"
    }
    PINECONE = {
        "description": "Langchain Pinecone vector database service",
        "index_name": configs.PINECONE_INDEX_NAME,
        "api_key": configs.PINECONE_API_KEY,
    }
    CHROMA = {
        "description": "LangChain Chroma vector database service",
        "tutorial_url": "https://youtu.be/3yPBVii7Ct0",
        "persist_directory": f"{configs.VECTOR_DB_STORAGE}/chroma_langchain_db",
        "collection_name": "langchain",
    }
