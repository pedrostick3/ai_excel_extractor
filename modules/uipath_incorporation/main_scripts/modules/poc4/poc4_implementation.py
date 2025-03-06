import os
import pandas as pd
import logging
from langchain_community.document_loaders import CSVLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import HumanMessage
from modules.ai.core.agents.vectordb_embeddings_agent.vectordb_embeddings_agent import VectordbEmbeddingsAgent
from modules.ai.core.agents.vectordb_embeddings_agent.enums.vectordb_client_service_enum import VectordbClientServiceEnum
from modules.excel.services.excel_service import ExcelService
from modules.logger.services.logger_service import LoggerService
import modules.poc4.poc4_prompts as prompts
from modules.analytics.services.ai_analytics import AiAnalytics


class PoC4Implementation:
    """
    This class is a LangChain implementation of the AI process for PoC4.
    """

    @staticmethod
    def run(
        input_files: list[str],
        parametrization_file_path: str,
        openai_api_key: str,
        ai_model: str = "gpt-4o-mini-2024-07-18",
        ai_embedding_model: str = "text-embedding-3-small",
        use_smarter_model: bool = False,
        update_parametrization_vector_db: bool = False,
        parametrization_collection_name = "parametrization",
        temporary_collection_name = "temp_collection",
        output_folder: str = "./assets/docs_output",
        output_file_name: str = "mestre dados_finais.xlsx",
        encoding: str ='utf-8-sig',
        add_csv_mapping_template_to_last_column: bool = True,
        use_logging_system: bool = True,
    ) -> dict:
        """
        Run the AI process for PoC3.

        Args:
            input_files (list[str]): List of input files to process.
            parametrization_file_path (str): Path to the parametrization file.
            openai_api_key (str): OpenAI API key.
            ai_model (str): AI model to use. Defaults to "gpt-4o-mini-2024-07-18".
            ai_embedding_model (str): AI embedding model to use. Defaults to "text-embedding-3-small".
            use_smarter_model (bool): Flag to indicate if to use a smarter model. Defaults to False.
            update_parametrization_vector_db (bool): Flag to indicate if to update the parametrization vector database. Defaults to False.
            parametrization_collection_name (str): Name of the parametrization collection. Defaults to "parametrization".
            temporary_collection_name (str): Name of the temporary collection. Defaults to "temp_collection".
            output_folder (str): Output folder path. Defaults to "./assets/docs_output".
            output_file_name (str): Output file name. Defaults to "mestre dados_finais.xlsx".
            encoding (str): Encoding of the input files. Defaults to "utf-8-sig".
            add_csv_mapping_template_to_last_column (bool): Flag to indicate if to add the CSV mapping template to the last column. Defaults to True.
            use_logging_system (bool): Flag to indicate if to use the logging system. Defaults to True.
        """
        # Config logs
        if use_logging_system:
            LoggerService.init()

        # Initialize vars to use with LangChain
        vectordb_provider = VectordbClientServiceEnum.CHROMA
        embedding_llm = OpenAIEmbeddings(
            api_key=openai_api_key,
            model=ai_embedding_model,
        )
        retrieval_llm = ChatOpenAI(
            api_key=openai_api_key,
            model_name=ai_model,
            temperature=0,
        )

        if update_parametrization_vector_db:
            parametrization_csv_path = ExcelService.convert_xlsx_to_csv(parametrization_file_path, encoding=encoding)
            parametrization_docs = CSVLoader(parametrization_csv_path, encoding=encoding).load_and_split() # [LangChain CSVLoader Documentation](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.csv_loader.CSVLoader.html)

            parametrization_agent = VectordbEmbeddingsAgent(
                client_service=vectordb_provider,
                embedding_llm=embedding_llm,
                retrieval_llm=retrieval_llm,
                documents=parametrization_docs,
                force_add_documents=True,
                collection_name=parametrization_collection_name,
            )
        else:
            parametrization_agent = VectordbEmbeddingsAgent(
                client_service=vectordb_provider,
                embedding_llm=embedding_llm,
                retrieval_llm=retrieval_llm,
                collection_name=parametrization_collection_name,
            )

        # Create the output_folder and output_file if not exists
        os.makedirs(output_folder, exist_ok=True)
        output_file = ExcelService.create_file(
            output_file_path= os.path.join(output_folder, output_file_name),
            insert_columns_if_file_not_exists=["Nome", "Quota", "NIF", "Numero de Sócio", "Taxa", "Mês da Contribuição"],
        )

        process_info: dict = {
            "files_able_to_extract_data": [],
            "files_unable_to_extract_data": [],
        }

        # Process the input files
        for file_path in input_files:
            logging.info(f"#### Start processing file: {file_path} ####")

            # Load and classify document
            csv_file_path = ExcelService.convert_xlsx_to_csv(file_path, encoding=encoding)
            docs = CSVLoader(csv_file_path, encoding=encoding).load_and_split()
            # TODO remover
            temporary_document_agent = VectordbEmbeddingsAgent(
                client_service=vectordb_provider,
                embedding_llm=embedding_llm,
                retrieval_llm=retrieval_llm,
                documents=docs,
                force_add_documents=True,
                collection_name=temporary_collection_name,
            )

            excel_sheet_name = ExcelService.get_sheet_name(file_path)

            # Invoke chain
            chain_result = PoC4Implementation.get_chain_result(
                parametrization_agent,
                temporary_document_agent,
                excel_sheet_name,
                parametrization_csv_file_path=ExcelService.convert_xlsx_to_csv(parametrization_file_path, encoding=encoding),
                csv_file_to_extract=csv_file_path,
                smarter_llm=ChatOpenAI(
                    api_key=openai_api_key,
                    model_name="o1-mini-2024-09-12", # "o3-mini-2025-01-31" model it is only available from Tier 3 (https://platform.openai.com/docs/guides/rate-limits#usage-tiers)
                    # temperature=0, # temperature it is not supported on "o1-mini-2024-09-12" model
                ) if use_smarter_model else None,
                add_csv_mapping_template_to_last_column=add_csv_mapping_template_to_last_column,
            )

            amount_of_data_rows_extracted = ExcelService.get_content_lines_of_csv_data(chain_result["result"])
            logging.info(f"'{file_path}' file chain result got {amount_of_data_rows_extracted} data rows:\n{chain_result}")

            if amount_of_data_rows_extracted > 0:
                # Process and save extracted data to the master file
                PoC4Implementation.save_extracted_data_to_master_file(
                    output_file,
                    chain_result["result"],
                    file_extracted=file_path,
                    add_csv_mapping_template_to_last_column=add_csv_mapping_template_to_last_column,
                )
                process_info["files_able_to_extract_data"].append(os.path.basename(file_path))
            else:
                process_info["files_unable_to_extract_data"].append(os.path.basename(file_path))
                logging.info(f"'{file_path}' file had no extracted data.")
            
            # Delete the temporary vector
            temporary_document_agent.embeddings_vector_llm.delete_collection()

            logging.info("######### END #########")

        #logging.info(AiAnalytics.__str__())
        #AiAnalytics.export_str_ai_analytics_data_to_excel()
        return process_info

    @staticmethod
    def save_extracted_data_to_master_file(
        master_file_path: str,
        csv_data: str,
        csv_data_column_sep: str = ';',
        file_extracted: str = None, 
        add_csv_mapping_template_to_last_column: bool = True,
    ):
        """
        Save the extracted CSV data to the master Excel file.

        Args:
            master_file_path (str): Path to the master Excel file.
            csv_data (str): CSV-formatted string containing the extracted data.
            csv_data_column_sep (str): Separator used in the CSV data.
            file_extracted (str): Path to the file containing the extracted data.
            add_csv_mapping_template_to_last_column (bool): Whether to add the CSV mapping template to the last column.
        """
        try:
            master_df = pd.read_excel(master_file_path)
        except FileNotFoundError:
            master_df = pd.DataFrame(columns=["Nome", "Quota", "NIF", "Numero de Sócio", "Taxa", "Mês da Contribuição"])

        rows = csv_data.strip().split('\r\n')
        header = rows[0].split(csv_data_column_sep)  # Base Header: Nome,Quota,NIF,Número de Sócio,Taxa,Mês da Contribuição
        data_rows = rows[1:]  # Data rows

        expected_columns = ["Nome", "Quota", "NIF", "Numero de Sócio", "Taxa", "Mês da Contribuição"]
        if add_csv_mapping_template_to_last_column and "CSV_MAPPING_TEMPLATE" in header:
            if file_extracted:
                expected_columns.append("FILE_NAME")
            expected_columns.append("CSV_MAPPING_TEMPLATE")

        new_data = []
        filename_already_inserted = False
        for row in data_rows:
            if not row:
                continue  # Skip empty rows
            
            values = row.split(csv_data_column_sep)
            while len(values) < len(header):
                values.append("")
            
            row_dict = {}
            for col in expected_columns:
                if col == "FILE_NAME" and not filename_already_inserted:
                    row_dict[col] = os.path.basename(file_extracted) if file_extracted else ""
                    filename_already_inserted = True
                else:
                    try:
                        idx = header.index(col)
                        row_dict[col] = values[idx].strip() if idx < len(values) else ""
                    except ValueError:
                        row_dict[col] = ""

            new_data.append(row_dict)

        new_df = pd.DataFrame(new_data, columns=expected_columns)
        updated_df = pd.concat([master_df, new_df], ignore_index=True)

        # Save in master
        updated_df.to_excel(master_file_path, index=False)
        logging.info(f"Data saved in master file: {master_file_path}")
    
    @staticmethod
    def get_chain_result(
        parametrization_agent: VectordbEmbeddingsAgent,
        temporary_document_agent: VectordbEmbeddingsAgent,
        excel_sheet_name: str,
        parametrization_csv_file_path: str,
        return_all_questions_and_answers: bool = False,
        extract_data_via_ai: bool = False,
        csv_file_to_extract: str = None,
        add_csv_mapping_template_to_last_column = True,
        smarter_llm: ChatOpenAI = None,
    ) -> dict:
        # Define Parsers
        header_output_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="table_header_row", description="The CSV header row where the table starts")])
        template_output_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="template_row", description="The CSV row that matches the template parametrization mapping")])
        output_map_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="output_map", description="The output map to extract data from CSV")])
        extraction_output_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="extracted_rows", description="The CSV rows that were extracted with the help of the template mapping")])

        questions_and_answers: list[dict[str, str]] = []
        temp_vars: dict[str, str] = {}
        parametrization_header_from_vector_search = "Template;Nome;Quota;Pivot;Sheet;NIF;Nsocio;SeparadorMilhar;SeparadorDecimal;Moeda;Remover linhas com;RemoverLinhaFinal;IgnorarLinhasSemValorDesconto;MesReferencia;Taxa: "
        parametrization_header = "Template;Nome;Quota;Pivot;Sheet;NIF;Nsocio;SeparadorMilhar;SeparadorDecimal;Moeda;Remover linhas com;RemoverLinhaFinal;IgnorarLinhasSemValorDesconto;MesReferencia;Taxa\r\n"

        first_rows_of_the_file_to_extract_data = ExcelService.get_excel_csv_to_csv_str(csv_file_to_extract, only_get_first_rows=5, csv_sep=';')

        def save_qa(x: dict):
            questions_and_answers.append({"question": x["question"], "answer": x["answer"]})
        
        def update_temp_vars(x: dict[str, str]):
            temp_vars.update(x)

        # Define Chains
        chain_get_header = (
            RunnablePassthrough.assign(
                prompt=lambda _: prompts.HEADER_PROMPT.format(
                    csv_data=first_rows_of_the_file_to_extract_data,
                    sheet_name=excel_sheet_name,
                    format_instructions=header_output_parser.get_format_instructions(),
                )
            )
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Header question"))
            | RunnableLambda(lambda x: [HumanMessage(content=x["prompt"])])
            | (smarter_llm if smarter_llm else temporary_document_agent.retrieval_llm)
            | RunnableLambda(lambda x: LoggerService.log_and_return(header_output_parser.parse(x.content), "Header result"))
        )

        chain_get_template = (
            # Keep the original table_header_row automatically with RunnablePassthrough.assign
            RunnablePassthrough.assign(similarity_search_results=lambda x: parametrization_agent.embeddings_vector_llm.similarity_search_with_score(x["table_header_row"]))
            | RunnablePassthrough.assign(top_3_similarity_search_results=lambda x: [doc.page_content for doc, score in x["similarity_search_results"]][:3])  # Extract only first 3 documents
            | RunnablePassthrough.assign(
                prompt=lambda x: prompts.TEMPLATE_CHOOSER_PROMPT.format(
                    table_header_row=x["table_header_row"],
                    templates_list=x["top_3_similarity_search_results"],
                    format_instructions=template_output_parser.get_format_instructions(),
                )
            )
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Parametrization template question", update_temp_vars, x))
            | RunnableLambda(lambda x: [HumanMessage(content=x["prompt"])])
            | (smarter_llm if smarter_llm else temporary_document_agent.retrieval_llm)
            | RunnableLambda(lambda x: LoggerService.log_and_return(template_output_parser.parse(x.content), "Parametrization template result"))
            | RunnableLambda(lambda x: {**x, 'template_row': x['template_row'].replace(parametrization_header_from_vector_search, '')})
            | RunnablePassthrough.assign(template_row=lambda x: f"{parametrization_header}{ExcelService.get_the_most_similar_row_of_csv_file(parametrization_csv_file_path, x['template_row'])}")
        )

        chain_get_output_map = (
            RunnablePassthrough.assign(output_map=lambda x: ExcelService.map_parametrization_to_output(x['template_row']))
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Output Map result", update_temp_vars, x))
        )

        chain_get_all = chain_get_header | chain_get_template | chain_get_output_map
        result = chain_get_all.invoke({})
        logging.info(f"template_row & output_map = {result}")
        output_map = result["output_map"]

        def get_non_empty_values(map:dict) -> list:
            return [value for value in map.values() if not pd.isna(value) and value != "" and value != "None"]

        for key, value in output_map.items():
            if value != "":
                continue

            chain_try_complete_template = (
                RunnableLambda(lambda _: {'prompt': prompts.TRY_COMPLETE_TEMPLATE_PROMPT.format(
                        empty_output_map_key=key,
                        file_to_extract_data=ExcelService.delete_columns_from_csv_string(first_rows_of_the_file_to_extract_data, get_non_empty_values(result["output_map"])),
                        format_instructions=output_map_parser.get_format_instructions(),
                    )}
                )
                | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Try complete template question"))
                | RunnableLambda(lambda x: [HumanMessage(content=x["prompt"])])
                | (smarter_llm if smarter_llm else temporary_document_agent.retrieval_llm)
                | RunnableLambda(lambda x: LoggerService.log_and_return(output_map_parser.parse(x.content), "Try complete template result"))
            )
            try_value = chain_try_complete_template.invoke({})
            result["output_map"][key] = try_value["output_map"]
            logging.info(f"template_row & AI improved output_map = {result}")

        if extract_data_via_ai:
            chain_extract_data = (
                RunnablePassthrough.assign(question=lambda x: prompts.EXTRACTION_PROMPT.format(template_row=x["formatted_output_row"], format_instructions=extraction_output_parser.get_format_instructions()))
                | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Data extraction question"))
                | temporary_document_agent.qa_chain
                | RunnableLambda(lambda x: LoggerService.log_and_return(extraction_output_parser.parse(x["answer"]), "Data extraction result", save_qa, x))
            )
        else:
            header_row_index = ExcelService.get_excel_csv_row_number(
                excel_file_path=csv_file_to_extract,
                excel_row_content=ExcelService.remove_last_column(temp_vars['table_header_row']),
                csv_sep=";",
            ) - 1
            
            chain_extract_data = (
                RunnablePassthrough.assign(
                    extracted_rows=lambda _: PoC4Implementation.extract_standardized_data(
                        csv_path=csv_file_to_extract,
                        excel_header_row_index=header_row_index,
                        csv_mapping_template=result["output_map"],
                        add_csv_mapping_template_to_last_column=add_csv_mapping_template_to_last_column,
                    )
                )
            )
        
        
        extracted_rows_result = chain_extract_data.invoke({})

        toReturn = {"result": extracted_rows_result["extracted_rows"]}
        if return_all_questions_and_answers:
            toReturn["questions_and_answers"] = questions_and_answers

        return toReturn

    @staticmethod
    def extract_standardized_data(
        csv_path: str,
        csv_mapping_template: dict,
        excel_header_row_index: int = None,
        sep: str = ';',
        encoding: str = 'utf-8-sig',
        strip_and_case_insensitive: bool = True,
        add_csv_mapping_template_to_last_column: bool = True,
    ) -> str:
        """
        Extracts data from a CSV file and maps it to standardized columns using the provided mapping template.

        Args:
            csv_path (str): Path to the CSV file.
            csv_mapping_template (dict): Dictionary with standardized column names as keys and original column names as values.
            excel_header_row_index (int, optional): Index of the Excel header row. Defaults to None.
            sep (str, optional): Delimiter for CSV file. Defaults to ';'.
            encoding (str, optional): Encoding for CSV file. Defaults to 'utf-8-sig'.
            strip_and_case_insensitive (bool, optional): Whether to strip whitespace and use case-insensitive column matching. Defaults to True.
            add_csv_mapping_template_to_last_column (bool, optional): Whether to add the CSV mapping template as a new last column. Defaults to True.

        Returns:
            str: CSV string with standardized columns and extracted data.
        """
        if not csv_path:
            logging.error("extract_standardized_data() - csv_path is empty.")
            raise ValueError("extract_standardized_data() - csv_path is empty.") 

        try:
            original_df = pd.read_csv(csv_path, sep=sep, encoding=encoding, header=excel_header_row_index)
        except Exception as e:
            logging.error(f"Error reading CSV file: {e}")
            raise
        
        column_map = {}
        for col in original_df.columns:
            processed_name = col.strip().lower() if strip_and_case_insensitive else col
            column_map[processed_name] = col

        standardized_data = []

        for index, row in original_df.iterrows():
            standardized_row = {}
            for standardized_col, original_col in csv_mapping_template.items():
                value = ""
                if original_col:
                    lookup_col = original_col.strip().lower() if strip_and_case_insensitive else original_col
                    
                    if lookup_col in column_map:
                        actual_col = column_map[lookup_col]
                        raw_value = row[actual_col]
                        
                        if pd.notna(raw_value):
                            if isinstance(raw_value, float) and raw_value.is_integer():
                                value = int(raw_value)
                            else:
                                value = raw_value
                                
                            if isinstance(value, str):
                                value = value.strip()
                    else:
                        logging.warning(f"Original column '{original_col}' not found in CSV columns")
                        
                standardized_row[standardized_col] = value

            non_empty_count = sum(1 for v in standardized_row.values() if v not in ["", None])
            if non_empty_count > 3:
                standardized_data.append(standardized_row)

        if add_csv_mapping_template_to_last_column and standardized_data:
            # Create a new column and add the mapping template to the first row
            for i, row in enumerate(standardized_data):
                if i == 0:  # Only add to the first row
                    row["CSV_MAPPING_TEMPLATE"] = str(csv_mapping_template)
                else:
                    row["CSV_MAPPING_TEMPLATE"] = ""  # Leave empty for other rows

        standardized_df = pd.DataFrame(standardized_data)

        return standardized_df.to_csv(index=False, sep=sep, encoding=encoding, lineterminator='\r\n')
