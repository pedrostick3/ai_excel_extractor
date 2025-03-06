class PoC4Constants:
    PARAMETRIZATION_HEADER_FROM_VECTOR_SEARCH:str = "Template;Nome;Quota;Pivot;Sheet;NIF;Nsocio;SeparadorMilhar;SeparadorDecimal;Moeda;Remover linhas com;RemoverLinhaFinal;IgnorarLinhasSemValorDesconto;MesReferencia;Taxa: "
    PARAMETRIZATION_HEADER_FROM_CSV:str = "Template;Nome;Quota;Pivot;Sheet;NIF;Nsocio;SeparadorMilhar;SeparadorDecimal;Moeda;Remover linhas com;RemoverLinhaFinal;IgnorarLinhasSemValorDesconto;MesReferencia;Taxa\r\n"
    OUTPUT_COLUMNS:list[str] = ["Nome", "Quota", "NIF", "Número de Sócio", "Taxa", "Mês da Contribuição"]
    OUTPUT_PARAMETRIZATION_MAP:str = "Nome;Quota;NIF;Número de Sócio;Taxa;Mês da Contribuição\r\nNome;Quota;NIF;Nsocio;Taxa;MesReferencia"
    