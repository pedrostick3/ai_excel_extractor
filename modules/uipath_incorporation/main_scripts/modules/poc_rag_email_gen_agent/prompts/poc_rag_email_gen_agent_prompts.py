EXTRACT_QUESTION_FROM_EMAIL_PROMPT = """Your job is to extract questions from an email.

Example:
- email: "Hello Nexis,\nI hope you are doing well.\n\nI am contacting you to ask the Daniel Coutinho NIF.\n\nAwaiting your response,\nDaniel Soares"
- extracted questions: "What's Daniel Coutinho NIF?"

This is the email:
```
{email}
```

{format_instructions}"""

EMAIL_GEN_SINGLE_QUESTION_PROMPT = """You are an assistant that adds source references to emails.
The source references should also specify the attachment filenames if the answer came from an attachament. Use the metadata info for that.

Additional rules:
Only return the email body with inline references.
Don't include the subject and the sender's email address.

This is the answer to the email and its sources:
```
{answered_email}
```

{format_instructions}"""

#Example:
#- email with the questions: "Hello Nexis, I hope you are doing well. I am contacting you to ask the Daniel Coutinho NIF.\n\nAwaiting your response,\n\nDaniel Soares"
#- email with the answers: "Hello Daniel,\n\nThe NIF for Daniel Coutinho is 852146898.\n\nSources:\n- 'email_ask_to_extract_data.eml';\n- '29.47€ Mapa Fundo Pensoes Sindicato Quadros_OUT2024.xlsx';\n\nBest regards,\nNexis"