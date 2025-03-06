from modules.ai.core.enums.file_category import FileCategory

PRE_HEADER_MODIFIER_SYSTEM_PROMPT = f"""You are an assistant that handles Excel files.
When someone asks to modify the pre-header of a file with the '{FileCategory.EXECUCAO.value}' category, your tasks are:
1. Remove row 1 if it is empty.

When someone asks to modify the pre-header of a file with the '{FileCategory.TESTE_EXECUCAO.value}' category, your tasks are:
1. Remove row 3 if it is empty.
2. Add a new blank row above row 1.

Additional rules:
Return the complete modified file with all rows and columns.
You should not add extra commas.
Your response must not include code-blocks or MARKDOWN."""

PRE_HEADER_MODIFIER_PROMPTS_CATEGORY_EXECUCAO = [
    {
        "role": "system",
        "content": PRE_HEADER_MODIFIER_SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": f"""Modify the pre-header of the following file that belongs to the '{FileCategory.EXECUCAO.value}' category:
,,,,,,,,
ExecutionId,ExecutionStartDate,ExecutionEndDate,TaskWorkload,CaseStartDate,CaseEndDate,IsSuccessful,RunTimeSeconds,AverageRunTimeSeconds""",
    },
    {
        "role": "assistant",
        "content": "ExecutionId,ExecutionStartDate,ExecutionEndDate,TaskWorkload,CaseStartDate,CaseEndDate,IsSuccessful,RunTimeSeconds,AverageRunTimeSeconds",
    },
]

PRE_HEADER_MODIFIER_PROMPTS_CATEGORY_TESTE_EXECUCAO = [
    {
        "role": "system",
        "content": PRE_HEADER_MODIFIER_SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": f"""Modify the pre-header of the following file that belongs to the '{FileCategory.TESTE_EXECUCAO.value}' category:
Test execution date,2024-10-30 12:15:38.947,,,,,,,
Total run time,3910,,,,,,,
,,,,,,,,
ExecutionId,IsSuccessful,RunTimeSeconds,ExecutionStartDate,ExecutionEndDate,TaskWorkload,CaseStartDate,CaseEndDate,AverageRunTimeSeconds""",
    },
    {
        "role": "assistant",
        "content": """,,,,,,,,
Test execution date,2024-10-30 12:15:38.947,,,,,,,
Total run time,3910,,,,,,,
ExecutionId,IsSuccessful,RunTimeSeconds,ExecutionStartDate,ExecutionEndDate,TaskWorkload,CaseStartDate,CaseEndDate,AverageRunTimeSeconds""",
    },
]