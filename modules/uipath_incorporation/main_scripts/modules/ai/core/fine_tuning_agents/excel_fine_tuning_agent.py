import logging
import os
import json
import shutil
from datetime import datetime
from modules.ai.services.openai_ai_service import OpenAiAiService
from modules.excel.services.excel_service import ExcelService
from modules.ai.core.enums.file_category import FileCategory
import modules.excel.constants.excel_constants as excel_constants
from modules.ai.core.fine_tuning_agents.prompts import excel_categorizer_and_header_finder_agent_prompts
from modules.ai.core.fine_tuning_agents.prompts import excel_pre_header_modifier_agent_prompts
from modules.ai.core.fine_tuning_agents.prompts import excel_content_modifier_with_function_calling_agent_prompts
from modules.ai.core.function_calling.enums.functions_to_call import FunctionsToCall

class ExcelFinetuningAgent:
    """
    Class to interact with the AI Fine-Tuning Agent.
    """
    fine_tuning_model = None

    def __init__(self,
        ai_service: OpenAiAiService,
        base_model: str,
        fine_tuning_model: str,
    ):
        """
        Initialize the AI Agent.
        """
        self.ai_service = ai_service
        self.base_model = base_model
        self.fine_tuning_model = fine_tuning_model

    def ask_ai(
        self,
        user_prompt: str,
        system_prompt: str = None,
        tools: list[dict] = None,
        tool_choice: str = None,
        ai_analytics_file_name: str = None,
        ai_analytics_agent_name: str = None,
        log_messages: bool = True,
    ) -> str:
        """
        Ask the AI for a response based on the given excel_data.

        Args:
            user_prompt (str): The user prompt to be used.
            tools (list[dict]): The tools to be used.
            tool_choice (str): Force the function calling by setting the tool choice to "required". [Source](https://community.openai.com/t/new-api-feature-forcing-function-calling-via-tool-choice-required/731488) 
            ai_analytics_file_name (str): The AI analytics file name to be used.
            ai_analytics_agent_name (str): The AI analytics agent name to be used.
            log_messages (bool): Flag to indicate if the request messages should be logged.

        Returns:
            str: The AI's response.
        """
        try:
            ai_response = self.ai_service.ask_ai(
                model=self.fine_tuning_model,
                base_model=self.base_model,
                first_user_prompt=user_prompt,
                system_prompt=system_prompt,
                tools=tools,
                tool_choice=tool_choice,
                use_assistant_instead_of_system=False,  # True caso o modelo seja "o1-preview" ou "o1-mini"
                response_format=None,
                ai_analytics_file_name=ai_analytics_file_name,
                ai_analytics_agent_name=ai_analytics_agent_name,
                log_request_messages=log_messages,
                log_response_message=log_messages,
            )

            return ai_response
        except Exception as e:
            logging.error(f"Erro ao comunicar com o AI ExcelGenericFinetuningAgent: {e}")
            raise
    
    def _handle_category_from_ai_category_agent_response_string(
        self,
        ai_agent_response: str,
        file_name: str,
        excel_file_path: str,
        invalid_output_path: str,
        function_id_to_log: str,
    ) -> str:
        """
        Handle the category from the AI category agent response string.

        Args:
            ai_agent_response (str): The AI category agent response.
            file_name (str): The file name.
            excel_file_path (str): The Excel file path.
            invalid_output_path (str): The invalid output path.
            function_id_to_log (str): The function ID to log.

        Returns:
            str: The new file path.
        """
        try:
            ai_agent_response_dict = json.loads(ai_agent_response)
        except json.JSONDecodeError or ValueError as e:
            logging.error(f"Warning - {function_id_to_log}: Erro ao converter a resposta do AI para JSON: {e}\nai_agent_response = {ai_agent_response}")
            raise

        try:
            category_by_ai = ai_agent_response_dict['category']
        except KeyError as e:
            logging.error(f"Warning - {function_id_to_log}: Erro ao obter a chave 'category' do JSON: {e}\nai_agent_response = {ai_agent_response_dict}")
            raise

        category = FileCategory.get_category_by_name(category_by_ai)
        logging.info(f"{function_id_to_log}: returned '{category_by_ai}' so the file '{file_name}' is the '{category}' category.")
        
        if category == FileCategory.INVALIDO:
            logging.info(f"{function_id_to_log}: O ficheiro '{file_name}' foi categorizado como 'INVALIDO'.")
            invalid_output_path = f"{invalid_output_path}/{category.value} - {file_name}"
            try:
                shutil.copy2(excel_file_path, invalid_output_path)
            except shutil.Error as e:
                logging.error(f"{function_id_to_log}: Erro ao guardar o ficheiro '{invalid_output_path}'.")
                raise
            return invalid_output_path

        return f'{invalid_output_path}/{category.value} - {datetime.now().strftime("%d_%m_%Y")} - {file_name}'

    def get_file_category_and_header(
        self,
        excel_file_path: str,
        invalid_output_path: str,
        ai_analytics_file_name: str = None,
    ) -> dict:
        """
        Get the file's category and header.

        Args:
            excel_file_path (str): The Excel file path.
            invalid_output_path (str): The invalid output path.
            ai_analytics_file_name (str): The AI analytics file name.

        Returns:
            dict: The file's category and header.
        """
        excel_data_first_5_rows = ExcelService.get_excel_csv_to_csv_str(excel_file_path, only_get_first_rows=5)
        file_name = os.path.basename(excel_file_path)
        excel_categorizer_and_header_finder_agent_response = self.ask_ai(
            system_prompt=excel_categorizer_and_header_finder_agent_prompts.CATEGORIZER_AND_HEADER_FINDER_SYSTEM_PROMPT,
            user_prompt=f"""Categorize and find the header of the following file:
Filename = '{file_name}'
```csv
{excel_data_first_5_rows}
```""",
            ai_analytics_file_name=ai_analytics_file_name,
            ai_analytics_agent_name="ExcelGenericFinetuningAgent (ExcelCategorizerAndHeaderFinderAgent)",
        )

        output_file_path = self._handle_category_from_ai_category_agent_response_string(
            ai_agent_response=excel_categorizer_and_header_finder_agent_response,
            file_name=file_name,
            excel_file_path=excel_file_path,
            invalid_output_path=invalid_output_path,
            function_id_to_log="AI ExcelGenericFinetuningAgent - get_file_category_and_header()",
        )

        try:
            excel_categorizer_and_header_finder_agent_response_dict = json.loads(excel_categorizer_and_header_finder_agent_response)
            excel_categorizer_and_header_finder_agent_response_dict["output_file_path"] = output_file_path
        except json.JSONDecodeError or ValueError as e:
            logging.error(f"Warning - AI ExcelGenericFinetuningAgent - get_file_category_and_header(): Erro ao converter a resposta do AI para JSON: {e}\nexcel_categorizer_and_header_finder_agent_response = {excel_categorizer_and_header_finder_agent_response}")
            raise
            
        return excel_categorizer_and_header_finder_agent_response_dict if excel_categorizer_and_header_finder_agent_response_dict else {}
    
    def modify_pre_header(
        self,
        category: FileCategory,
        input_excel_file_path: str,
        header_row_number: int,
        output_excel_file_path: str,
        ai_analytics_file_name: str = None,
    ) -> bool:
        """
        Modify the pre-header of the Excel file.

        Args:
            category (FileCategory): The category of the file.
            input_excel_file_path (str): The path to the input Excel file.
            header_row_number (int): The number of the header row.
            output_excel_file_path (str): The path to the output Excel file.
            ai_analytics_file_name (str): The AI analytics file name to be used.

        Returns:
            bool: The success of the operation.
        """
        excel_data_first_rows_until_header = ExcelService.get_excel_csv_to_csv_str(input_excel_file_path, only_get_first_rows=header_row_number)
        logging.info(f"AI ExcelGenericFinetuningAgent - {category} - excel_data_first_rows_until_header = {excel_data_first_rows_until_header}")
        excel_pre_header_modifier_agent_response = self.ask_ai(
            system_prompt=excel_pre_header_modifier_agent_prompts.PRE_HEADER_MODIFIER_SYSTEM_PROMPT,
            user_prompt=f"Modify the pre-header of the following file that belongs to the '{category.value}' category:\n{excel_data_first_rows_until_header}",
            ai_analytics_file_name=ai_analytics_file_name,
            ai_analytics_agent_name="ExcelGenericFinetuningAgent (ExcelPreHeaderModifierAgent)",
        )

        try:
            success = ExcelService.replace_excel_csv_data_in_file(
                excel_input_file_path=input_excel_file_path,
                excel_output_file_path=output_excel_file_path,
                excel_data=excel_pre_header_modifier_agent_response,
                initial_index_for_replacement=0,
                final_index_for_replacement=header_row_number,
            )

            if not success:
                logging.error(f"Warning - AI ExcelGenericFinetuningAgent - Não foi possível guardar o ficheiro '{output_excel_file_path}'.")

            return success
        except Exception as e:
            logging.error(f"Erro ao processar o retorno do AI ExcelGenericFinetuningAgent: {e}")
            raise
    
    def modify_content_returning_function_calling(
        self,
        category: FileCategory,
        input_excel_file_path: str,
        output_excel_file_path: str,
        excel_header_row_index: int,
        ai_analytics_file_name: str = None,
    ) -> None:
        """
        Make AI return the function to call that modifies the content of the Excel file.

        Args:
            category (FileCategory): The category of the file.
            excel_input_file_path (str): The path to the Excel file to be processed.
            excel_output_file_path (str): The path to the Excel file to be saved.
            excel_header_row_index (int): The row index of the header in the Excel file.
            ai_analytics_file_name (str, optional): The AI analytics file name to be used. Defaults to None.

        Returns:
            None
        """
        try:
            excel_data = ExcelService.get_excel_csv_to_csv_str(input_excel_file_path)
        except Exception as e:
            logging.error(f"AI ExcelGenericFinetuningAgent: Error reading Excel file: {e}")
            raise

        excel_lines = excel_data.split(excel_constants.EXCEL_LINE_BREAK)
        excel_lines_count = len(excel_lines) - 1
        logging.info(f"AI ExcelGenericFinetuningAgent - {category} - The file '{input_excel_file_path}' has {excel_lines_count} lines.")
        
        try:
            ai_response = self.ask_ai(
                system_prompt=excel_content_modifier_with_function_calling_agent_prompts.CONTENT_MODIFIER_SYSTEM_PROMPT,
                user_prompt=f"""Return the function to call that modifies the content of the following file that belongs to the '{category.value}' category:
input_excel_file_path = '{input_excel_file_path}'
output_excel_file_path = '{output_excel_file_path}'
excel_header_row_index = {excel_header_row_index}""",
                ai_analytics_file_name=ai_analytics_file_name,
                ai_analytics_agent_name="ExcelGenericFinetuningAgent (ExcelContentModifierWithFunctionCallingAgent)",
                tool_choice="required",
                tools=[
                    *FunctionsToCall.MODIFY_EXCEL_CONTENT_FOR_EXECUTION_CATEGORY.value["tools"],
                    *FunctionsToCall.MODIFY_EXCEL_CONTENT_FOR_TEST_EXECUTION_CATEGORY.value["tools"],
                ],
            )
        except Exception as e:
            logging.error(f"AI ExcelGenericFinetuningAgent: Error communicating with AI: {e}")
            raise

        try:
            response_json = json.loads(ai_response)
        except json.JSONDecodeError:
            logging.error(f"AI ExcelGenericFinetuningAgent: Error parsing AI response JSON: {ai_response}")
            raise
        
        if "function" not in response_json:
            logging.error(f"AI ExcelGenericFinetuningAgent: The AI response JSON does not contain the 'function' key. ai_response = {ai_response}")
            raise

        try:
            FunctionsToCall.get_enum_by_function_name(response_json["function"]["name"]).run_function_from_ai_response(
                str_dict_func_args=response_json["function"]["arguments"],
            )
        except json.JSONDecodeError:
            logging.error(f"AI ExcelGenericFinetuningAgent: Error executing function. response_json: {response_json}")
            raise