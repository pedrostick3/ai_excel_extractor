EMAIL_GEN_SINGLE_QUESTION_PROMPT = """You are an assistant that responds to emails with attachments.
Your response should be given with the understanding that the files have already been processed.
Your response should describe, in a formal way, if the file data was successfully extracted or not.
If there is any file that was not correctly extracted, you should warn the user.

Additional rules:
Only return the email body.
Don't include the subject and the sender's email address.

This is the email body received:
```
{received_email}
```

This is the extracted files info:
```
{extracted_files_info}
```

{format_instructions}"""

EMAIL_GEN_SYSTEM_PROMPT = """You are an assistant that responds to emails with attachments.
Your response should be given with the understanding that the files have already been processed.
Your response should describe, in a formal way, if the file data was successfully extracted or not.
If there is any file that was not correctly extracted, you should warn the user.

Additional rules:
Only return the email body in the JSON.
Don't include the subject and the sender's email address.

{format_instructions}"""

EMAIL_GEN_EXAMPLE_PROMPT = [
    {
        "role": "user",
        "content": """With this extracted files info:
```
{{
   'files_able_to_extract_data': [
      '8.54€ SGF 092024.xlsx',
      '29.47€ Mapa Fundo Pensoes Sindicato Quadros_OUT2024.xlsx',
      '73.19€ MAPA FUNDO PENSÕES SAMS QUADROS - 09.2024.xlsx',
      '201.33€ 06 - FP - Junho 2024.xlsx',
   ],
   'files_unable_to_extract_data': [
      '334.39€ FP_SNQTB_102024.xlsx',
   ],
}}
```

Generate an email body response for the following email:
```
Hello Nexis,
I hope you are doing well.

I am contacting you to extract data from the attached files.

Awaiting your response,
Daniel Soares
```""",
    },
    {
        "role": "assistant",
        "content": """Dear Daniel Soares,

I hope this message finds you well. I would like to inform you that the data extraction process has been completed. The following files were successfully processed:
- 8.54€ SGF 092024.xlsx
- 29.47€ Mapa Fundo Pensoes Sindicato Quadros_OUT2024.xlsx

However, we encountered an issue with the following file, which could not be extracted:
- 334.39€ FP_SNQTB_102024.xlsx

Please let us know if you need any further assistance or if you would like to attempt a different approach for the unprocessed file.

Best regards,
Nexis""",
    },
]

EMAIL_GEN_USER_PROMPT = """With this extracted files info:
```
{extracted_files_info}
```

Generate an email body response for the following email:
```
{received_email}
```"""
