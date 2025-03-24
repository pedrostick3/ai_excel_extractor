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
    POC_RAG = {"description": "PoC_RAG implementation"}
    TEST_LANGSMITH = {
        "description": "LangSmith tool test",
        "official_docs": "https://docs.smith.langchain.com/",
        "official_platform": "https://eu.smith.langchain.com/",
    }
    TEST_LANGCHAIN_AGENT = {
        "description": "LangChain Agent test (deprecated approach)",
        "official_docs": "https://python.langchain.com/api_reference/langchain/agents/langchain.agents.mrkl.base.ZeroShotAgent.html",
        "migrate_langchain_agent_to_langgraph": "https://python.langchain.com/docs/how_to/migrate_agent/",
    }
    TEST_LANGGRAPH_AGENT = {
        "description": "LangGraph Agent test",
        "official_docs": "https://python.langchain.com/docs/tutorials/agents/",
    }
    TEST_LANGGRAPH_MULTI_AGENT = {
        "description": "LangGraph Multi-Agent Collaboration test",
        "official_docs": "https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/multi_agent/multi-agent-collaboration.ipynb",
        "tutorial_video": "https://youtu.be/hvAPnpSfSGo?si=SacZBMI7D4QqLrqM",
    }

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
