from modules.ai.core.enums.file_category import FileCategory
from modules.ai.core.function_calling.enums.functions_to_call import FunctionsToCall

CONTENT_MODIFIER_SYSTEM_PROMPT = f"""You are an assistant responsible for choosing the right function to call (tools - function calling).
When someone asks to return the function to call that modifies the content of a file, if the category is:
- '{FileCategory.EXECUCAO.value}', return the 'modify_excel_content_for_execution_category' function.
- '{FileCategory.TESTE_EXECUCAO.value}', return the 'modify_excel_content_for_test_execution_category' function."""

CONTENT_MODIFIER_PROMPTS_CATEGORY_EXECUCAO = [
    {
        "role": "system",
        "content": CONTENT_MODIFIER_SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": f"""Return the function to call that modifies the content of the following file that belongs to the '{FileCategory.EXECUCAO.value}' category:
input_excel_file_path = './assets/docs_input/Execution_data Template.xlsx'
output_excel_file_path = './assets/docs_output/Execução - 16_12_2024 - Execution_data Template.xlsx'
excel_header_row_index = 1""",
        "tools": [
            *FunctionsToCall.MODIFY_EXCEL_CONTENT_FOR_EXECUTION_CATEGORY.value["tools"],
            *FunctionsToCall.MODIFY_EXCEL_CONTENT_FOR_TEST_EXECUTION_CATEGORY.value["tools"],
        ],
    },
    {
        "role": "assistant",
        "tool_calls": [
            {
                "function": {
                    "arguments": "{\"input_excel_file_path\":\"./assets/docs_input/Execution_data Template.xlsx\",\"output_excel_file_path\":\"./assets/docs_output/Execução - 16_12_2024 - Execution_data Template.xlsx\",\"excel_header_row_index\":1}",
                    "name": "modify_excel_content_for_execution_category",
                },
                "type": "function",
            },
        ],
    },
]

CONTENT_MODIFIER_PROMPTS_CATEGORY_TESTE_EXECUCAO = [
    {
        "role": "system",
        "content": CONTENT_MODIFIER_SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": f"""Return the function to call that modifies the content of the following file that belongs to the '{FileCategory.TESTE_EXECUCAO.value}' category:
input_excel_file_path = './assets/docs_input/Test_Execution_data Template.xlsx'
output_excel_file_path = './assets/docs_output/Teste Execução - 13_12_2024 - Test_Execution_data Template.xlsx'
excel_header_row_index = 3""",
        "tools": [
            *FunctionsToCall.MODIFY_EXCEL_CONTENT_FOR_EXECUTION_CATEGORY.value["tools"],
            *FunctionsToCall.MODIFY_EXCEL_CONTENT_FOR_TEST_EXECUTION_CATEGORY.value["tools"],
        ],
    },
    {
        "role": "assistant",
        "tool_calls": [
            {
                "function": {
                    "arguments": "{\"input_excel_file_path\":\"./assets/docs_input/Test_Execution_data Template.xlsx\",\"output_excel_file_path\":\"./assets/docs_output/Teste Execução - 13_12_2024 - Test_Execution_data Template.xlsx\",\"excel_header_row_index\":3}",
                    "name": "modify_excel_content_for_test_execution_category",
                },
                "type": "function",
            },
        ],
    },
]
