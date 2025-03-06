from enum import Enum


class AiImplementation(Enum):
    """
    Enum for the different AI implementations.
    """

    UNKNOWN = {"description": "Unknown"}
    TEST_PANDAS_DATAFRAME_TOOL_AGENT = {
        "description": "LangChain pandas dataframe tool agent test",
        "official_docs": "https://python.langchain.com/docs/integrations/tools/pandas/",
    }
    TEST_VECTORDB_EMBEDDINGS_AGENT = {
        "description": "LangChain Vector DB with Embeddings agent test",
        "official_docs": "https://python.langchain.com/docs/integrations/vectorstores/",
    }
    TEST_RAG = {
        "description": "LangChain RAG with Web and Vector DB",
        "official_docs": "https://python.langchain.com/docs/tutorials/rag/",
    }
    POC_4 = {"description": "PoC4 implementation"}

    @staticmethod
    def get_implementation_by_description(implementation_description: str) -> "AiImplementation":
        """
        Get the AI Implementation by its description.

        Args:
            implementation_description (str): The AI Implementation description.

        Returns:
            AiImplementation: The AI Implementation.
        """
        for implementation in AiImplementation:
            if implementation.value["description"] == implementation_description:
                return implementation

        return AiImplementation.UNKNOWN
