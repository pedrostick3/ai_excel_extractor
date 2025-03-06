import logging
from typing import Callable

class LoggerService:
    """
    Service class to handle Logs.
    """

    @staticmethod
    def init(file_to_log: str = "project_logs.log"):
        """
        Initialize the logging system.
        """
        # Config logs
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(file_to_log, encoding="utf-8"),
                    logging.StreamHandler(),
                ],
            )
            logging.info(">---< Logging System Initialized >---<")

    @staticmethod        
    def log_and_return(value, key_label:str, callback:Callable = None, callback_input = None):
        """
        Logs the given value and returns it.

        Args:
            value (any): The value to log and return.
            key_label (str): The label for the value.
            callback (Callable[[dict], None], optional): A callback function to be executed after logging. Defaults to None.
            callback_input (dict, optional): Input dictionary for the callback function. Defaults to None.

        Example:
            chain_get_header = (
                RunnablePassthrough.assign(question=lambda _: "What's the header row of the document?")
                | RunnableLambda(lambda x: log_and_return(x, "Header question"))
                | document_agent.qa_chain
                | RunnableLambda(lambda x: log_and_return({"header_row": x["answer"]}, "Header result"))
            )
        """
        logging.info(f"{key_label}: {value}")
        if callback:
            callback(callback_input)
        return value