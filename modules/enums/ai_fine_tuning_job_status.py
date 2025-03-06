from enum import Enum


class AiFineTuningJobStatus(Enum):
    """
    Enum for the AI Fine-Tuning Job Status.

    References:
    - https://platform.openai.com/docs/api-reference/fine-tuning/object#fine-tuning/object-status
    """

    VALIDATING_FILES = "validating_files"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @staticmethod
    def is_validating_files(status: str) -> bool:
        return status == AiFineTuningJobStatus.VALIDATING_FILES.value
    
    @staticmethod
    def is_queued(status: str) -> bool:
        return status == AiFineTuningJobStatus.QUEUED.value
    
    @staticmethod
    def is_running(status: str) -> bool:
        return status == AiFineTuningJobStatus.RUNNING.value
    
    @staticmethod
    def is_succeed(status: str) -> bool:
        return status == AiFineTuningJobStatus.SUCCEEDED.value
    
    @staticmethod
    def is_failed(status: str) -> bool:
        return status == AiFineTuningJobStatus.FAILED.value
    
    @staticmethod
    def is_cancelled(status: str) -> bool:
        return status == AiFineTuningJobStatus.CANCELLED.value
    
    @staticmethod
    def has_finished(status: str) -> bool:
        return AiFineTuningJobStatus.is_succeed(status) or AiFineTuningJobStatus.is_failed(status) or AiFineTuningJobStatus.is_cancelled(status)
