from enum import Enum


class AiType(Enum):
    """
    Enum for the different AI types.
    """

    UNKNOWN = {"description": "Unknown"}
    COMPLETION = {
        "description": "Completion",
        "RETURN_CODE_TO_EDIT_INSTEAD_OF_RETURN_EDITED_CONTENT": True,
        "USE_GENERIC_CONTENT_MODIFIER_AGENT_WHEN_RETURNING_CODE": False,
    }
    COMPLETION_FUNCTION_CALLING = {
        "description": "Completion with Function Calling tool"
    }
    FINE_TUNING = {
        "description": "Fine-tuning",
        "USE_CATEGORIZER_AND_HEADER_FINDER_IN_1_REQUEST": True,
        "USE_FUNCTION_CALLING_TO_MODIFY_CONTENT": True,
    }
    ASSISTANT_FILE_SEARCH = {"description": "Assistant with File Search tool"}
    ASSISTANT_CODE_INTERPRETER = {"description": "Assistant with Code Interpreter tool"}

    @staticmethod
    def get_type_by_description(type_description: str) -> "AiType":
        """
        Get the AI Type by its description.

        Args:
            type_description (str): The AI Type description.

        Returns:
            AiType: The AI Type.
        """
        for category in AiType:
            if category.value["description"] == type_description:
                return category

        return AiType.UNKNOWN
