from enum import Enum
import logging
import json
from modules.ai.core.function_calling.functions.modify_excel_content_functions import ModifyExcelContentFunctions

class FunctionsToCall(Enum):
    """
    Enum for the different functions to call.

    Refs:
    - https://platform.openai.com/docs/guides/function-calling
    - https://json-schema.org/learn/getting-started-step-by-step#introduction-to-json-schema
    """

    UNKNOWN = {"description": "Unknown"}

    MODIFY_EXCEL_CONTENT_FOR_EXECUTION_CATEGORY = {
        "function": ModifyExcelContentFunctions.modify_excel_content_for_execution_category,
        "description": "Function to modify the content of an Excel file based on the Execution Category.",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "modify_excel_content_for_execution_category",
                    "description": "Modify the content of an Excel file based on the Execution Category.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input_excel_file_path": {
                                "type": "string",
                                "description": "The input Excel file path.",
                            },
                            "output_excel_file_path": {
                                "type": "string",
                                "description": "The output Excel file path.",
                            },
                            "excel_header_row_index": {
                                "type": "number",
                                "description": "The Excel header row index.",
                            },
                        },
                        "required": ["input_excel_file_path", "output_excel_file_path", "excel_header_row_index"],
                    },
                }
            }
        ],
    }

    MODIFY_EXCEL_CONTENT_FOR_TEST_EXECUTION_CATEGORY = {
        "function": ModifyExcelContentFunctions.modify_excel_content_for_test_execution_category,
        "description": "Function to modify the content of an Excel file based on the Test Execution Category.",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "modify_excel_content_for_test_execution_category",
                    "description": "Modify the content of an Excel file based on the Test Execution Category.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input_excel_file_path": {
                                "type": "string",
                                "description": "The input Excel file path.",
                            },
                            "output_excel_file_path": {
                                "type": "string",
                                "description": "The output Excel file path.",
                            },
                            "excel_header_row_index": {
                                "type": "number",
                                "description": "The Excel header row index.",
                            },
                        },
                        "required": ["input_excel_file_path", "output_excel_file_path", "excel_header_row_index"],
                    },
                }
            }
        ],
    }

    @staticmethod
    def get_enum_by_function_name(function_name: str) -> "FunctionsToCall":
        """
        Get the enum by the function name.

        Args:
            function_name (str): The function name.

        Returns:
            FunctionsToCall: The enum.
        """
        if not function_name:
            logging.warning("FunctionsToCall - get_enum_by_function_name(): No function name provided.")
            return FunctionsToCall.UNKNOWN
        
        enum_item = next(
            (
                enum
                for enum in FunctionsToCall
                for tool in enum.value.get("tools", [])
                if tool.get("function", {}).get("name") == function_name
            ),
            FunctionsToCall.UNKNOWN,
        )

        if enum_item == FunctionsToCall.UNKNOWN:
            logging.warning(f"FunctionsToCall - get_enum_by_function_name(): Function name not found: {function_name}")

        return enum_item

    def run_function_from_ai_response(
        self,
        str_dict_func_args: str = None,
        dict_func_args: dict = None,
    ) -> None:
        """
        Run the function from the AI response.

        Args:
            str_dict_func_args (str): The string representation of the dictionary with the function arguments.
            dict_func_args (dict): The dictionary with the function arguments.

        Example:
            func_enum = FunctionsToCall.get_enum_by_function_name("modify_excel_content_for_execution_category").run_function_from_ai_response(
                str_dict_func_args="{\"input_excel_file_path\":\"./assets/docs_input/Execution_data Template.xlsx\",\"output_excel_file_path\":\"./assets/docs_output/Execution_data Template.xlsx\",\"excel_header_row_index\":1}",
            )
        """
        if self == FunctionsToCall.UNKNOWN:
            logging.warning("FunctionsToCall - run_function_from_ai_response(): Unknown function to call.")
            return None
        
        if not str_dict_func_args and not dict_func_args:
            logging.warning("FunctionsToCall - run_function_from_ai_response(): No function arguments provided from str_dict_func_args and dict_func_args.")
            return None
        
        if str_dict_func_args:
            try:
                dict_func_args = json.loads(str_dict_func_args)
            except json.JSONDecodeError:
                logging.error(f"FunctionsToCall - run_function_from_ai_response(): Error decoding the str_dict_func_args: {str_dict_func_args}")
                raise

        if not dict_func_args:
            logging.warning("FunctionsToCall - run_function_from_ai_response(): No function arguments provided from dict_func_args.")
            return None
        
        function_to_call = self.value.get("function")
        if not function_to_call:
            logging.warning("FunctionsToCall - run_function_from_ai_response(): No function to call.")
            return None
        
        try:
            function_to_call(**dict_func_args)
        except TypeError as e:
            logging.error(f"FunctionsToCall - run_function_from_ai_response(): Error calling the function: {e}")
            raise
