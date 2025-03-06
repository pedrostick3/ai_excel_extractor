HEADER_PROMPT = """Identify the table header row (it may not be the first row):
```csv
{csv_data}
```

Be precise as this will be used for template mapping. Some cautions:
1. Add '{sheet_name}' column at the end of the row.
2. Return only the CSV row without explanations.
3. The column name should be exactly the same as the column name, even if it has special characters like ':'.
Example:
- vector column name: "Nome:"
- column name should be: "Nome:"

{format_instructions}"""

TEMPLATE_CHOOSER_PROMPT = """Choose the best template for this header row: '{table_header_row}'.
You must pick one item from this templates list: '{templates_list}'.

{format_instructions}"""

TRY_COMPLETE_TEMPLATE_PROMPT = """Try to find the best column for {empty_output_map_key}:
```
{file_to_extract_data}
```

Additional information:
- Nome: Represents the full name of a person. This field should contain alphabetic characters (and may include spaces or special characters) representing the individual's name. Example: "João Silva", "Maria Fernandes".
- Quota: Denotes a monetary amount, such as a fee, share, or contribution. It should be formatted as a numeric value representing money, and may include decimal points or commas depending on locale. Example: "100.00", "250,50".
- NIF: This is a tax identification number typically used in some countries (e.g., Portugal) and must consist of exactly 9 digits. It should be treated as an integer, with any leading zeros preserved. Example: "123456789", "001234567".
- Número de Sócio: Refers to a membership or association number. This field should be an integer or a string that uniquely identifies a member within an organization or club. Example: "101", "205".
- Taxa: Indicates a rate that could either be expressed as a percentage or a decimal (double) number. The value might represent, for instance, a discount rate or interest rate. Examples: "15%" or "0.15".
- Mês da Contribuição: Specifies the month when a contribution is made. This value can either be given as the full name (or abbreviated name) of the month or as a numerical representation (1 for January, 2 for February, etc.).

Additional Rules:
1. If there is no column that makes sense, that column should be "".

{format_instructions}"""

EXTRACTION_PROMPT = """With the help of the parametrization template: "{template_row}".
Extract all data rows as CSV with these standardized columns: "Nome;Quota;NIF;Número de Sócio;Taxa;Mês da Contribuição".

Rules:
1. Map columns using the template mappings
2. Use empty fields (;;) for missing values
3. Maintain original data formatting
4. If unsure about a column, try to infer from header names

Example:
- parametrization template: "Template;Nome;Quota;Pivot;Sheet;NIF;Nsocio;SeparadorMilhar;SeparadorDecimal;Moeda;Remover linhas com;RemoverLinhaFinal;IgnorarLinhasSemValorDesconto;MesReferencia;Taxa\nFP;Nome;Valor do Desconto;A1;FP;NIF;;;.;;;;;Mês referência;Taxa de Desconto"
- output CSV: "Nome;Quota;NIF;Número de Sócio;Taxa;Mês da Contribuição\nEstela Cardoso;8.54;254698754;;0.5;202409"

{format_instructions}"""
