from enum import Enum

class VectordbClientServiceEnum(Enum):
    """
    Enum for the different Vectordb client services.
    """

    UNKNOWN = {"description": "Unknown"}
    FAISS = {
        "description": "LangChain FAISS vector database service",
        "persist_directory": "./vector_databases_storage/faiss_index_parametrization"
    }
    CHROMA = {
        "description": "LangChain Chroma vector database service",
        "tutorial_url": "https://youtu.be/3yPBVii7Ct0",
        "persist_directory": "./vector_databases_storage/chroma_langchain_db",
        "collection_name": "langchain",
    }
