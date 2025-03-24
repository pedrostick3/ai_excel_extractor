import os
import logging
import constants.configs as configs
from dotenv import load_dotenv
from langsmith import utils

class LangSmithService:
    @staticmethod
    def init_service(
        langsmith_api_key: str = configs.LANGSMITH_API_KEY,
        langsmith_tracing: bool = configs.LANGSMITH_TRACING,
        langsmith_endpoint: str = configs.LANGSMITH_ENDPOINT,
        langsmith_project: str = configs.LANGSMITH_PROJECT_TEST_LANGSMITH,
    ) -> bool:
        """
        Initialize the language service.
        """
        os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
        os.environ["LANGSMITH_TRACING"] = str(langsmith_tracing).lower()
        os.environ["LANGSMITH_ENDPOINT"] = langsmith_endpoint
        os.environ["LANGSMITH_PROJECT"] = langsmith_project
        load_dotenv(override=True)

        is_properly_initialized = utils.tracing_is_enabled()
        logging.info(f"LangSmith tracing enabled? {is_properly_initialized}")
        return is_properly_initialized
