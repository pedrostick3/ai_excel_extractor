from enum import Enum


class AiFileStatus(Enum):
    """
    Enum for the AI File Status.

    References:
    - https://platform.openai.com/docs/api-reference/files/object
    """

    UPLOADED = "uploaded"
    PROCESSED = "processed"
    ERROR = "error"

    @staticmethod
    def is_uploaded(status: str) -> bool:
        return status == AiFileStatus.UPLOADED.value
    
    @staticmethod
    def is_processed(status: str) -> bool:
        return status == AiFileStatus.PROCESSED.value
    
    @staticmethod
    def is_error(status: str) -> bool:
        return status == AiFileStatus.ERROR.value
    
    @staticmethod
    def has_finished(status: str) -> bool:
        return AiFileStatus.is_processed(status) or AiFileStatus.is_error(status)
