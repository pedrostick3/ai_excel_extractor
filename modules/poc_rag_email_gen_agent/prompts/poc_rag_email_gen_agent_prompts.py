EXTRACT_QUESTION_FROM_EMAIL_PROMPT = """Your job is to extract questions from an email.

Example:
- email: "Hello Nexis,\nI hope you are doing well.\n\nI am contacting you to ask the Daniel Coutinho NIF.\n\nAwaiting your response,\nDaniel Soares"
- extracted questions: "What's Daniel Coutinho NIF?"

This is the email:
```
{email}
```

{format_instructions}"""

ADD_SOURCES_TO_ANSWER_PROMPT = """You are an assistant that adds source references to emails.
The source references should also specify the attachment filenames if the answer came from an attachament. Use the metadata info for that.

Additional rules:
Only return the email body with inline references.
Don't include the subject and the sender's email address.

This is the answer to the email and its sources:
```
{answered_email}
```

{format_instructions}"""

EMAIL_GEN_AND_PRETTIFY_PROMPT = """You are an assistant tasked with responding to the original email by enhancing the email body that already has the answers and sources.

**Instructions:**
- Only return the prettified email body.
- Include the sources of the answer with bullet points right after the answer.
- If any paths are present, only include the filenames, not the full paths.
- Do not include the subject line or the sender's email address.

**Original Email:**
```
{original_email}
```

**Email Body with the Answers and Sources:**
```
{answered_email}
```

Example:
- original email: "Hello Nexis, I hope you are doing well. I am contacting you to ask the Daniel Coutinho NIF.\n\nAwaiting your response,\n\nDaniel Soares"
- email with the answers and sources: "Daniel Coutinho's NIF is 852146898.  \n\nFor reference, this information was extracted from the document titled '73.19€ MAPA FUNDO PENSÕES SAMS QUADROS - 09.2024.xlsx' and the email response document."
- prettified email body: "Hello Daniel,\n\nThe NIF for Daniel Coutinho is 852146898.\n\nSources:\n- '73.19€ MAPA FUNDO PENSÕES SAMS QUADROS - 09.2024.xlsx';\n\nBest regards,\nNexis"

{format_instructions}"""
