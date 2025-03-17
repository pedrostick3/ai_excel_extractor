import os
import logging
import constants.configs as configs
from dotenv import load_dotenv
from langsmith import utils

class LangSmithService:
    @staticmethod
    def init_service() -> bool:
        """
        Initialize the language service.
        """
        os.environ["LANGSMITH_API_KEY"] = configs.LANGSMITH_API_KEY
        os.environ["LANGSMITH_TRACING"] = str(configs.LANGSMITH_TRACING).lower()
        os.environ["LANGSMITH_ENDPOINT"] = configs.LANGSMITH_ENDPOINT
        os.environ["LANGSMITH_PROJECT"] = configs.LANGSMITH_PROJECT
        load_dotenv(override=True)

        is_properly_initialized = utils.tracing_is_enabled()
        logging.info(f"LangSmith tracing enabled? {is_properly_initialized}")
        return is_properly_initialized
