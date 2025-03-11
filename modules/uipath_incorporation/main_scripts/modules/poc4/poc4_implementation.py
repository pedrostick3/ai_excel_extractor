import os
import time
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
from modules.poc4.constants.poc4_constants import PoC4Constants
from modules.poc4.utils.poc4_utils import PoC4Utils
import modules.poc4.poc4_prompts as prompts


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
        output_folder: str = "./assets/docs_output",
        output_file_name: str = "mestre dados_finais.xlsx",
        encoding: str ='utf-8-sig',
        add_csv_mapping_template_to_last_column: bool = True,
        use_logging_system: bool = False,
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
            use_logging_system (bool): Flag to indicate if to use the logging system. Defaults to False.
        """
        # Config logs
        if use_logging_system:
            LoggerService.init()

        # Initialize vars to use with LangChain
        vectordb_provider = VectordbClientServiceEnum.CHROMA
        embedding_llm = OpenAIEmbeddings(
            api_key = openai_api_key,
            model = ai_embedding_model,
        )
        retrieval_llm = ChatOpenAI(
            api_key = openai_api_key,
            model_name = ai_model,
            temperature = 0,
        )

        parametrization_agent = VectordbEmbeddingsAgent(
            client_service = vectordb_provider,
            embedding_llm = embedding_llm,
            retrieval_llm = retrieval_llm,
            collection_name = parametrization_collection_name,
        )
        if update_parametrization_vector_db or not parametrization_agent.collection_exists():
            parametrization_csv_path = ExcelService.convert_xlsx_to_csv(parametrization_file_path, encoding=encoding)
            parametrization_docs = CSVLoader(parametrization_csv_path, encoding=encoding).load_and_split() # [LangChain CSVLoader Documentation](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.csv_loader.CSVLoader.html)
            parametrization_agent.embeddings_vector_llm.delete_collection() # Delete old vectors
            parametrization_agent = VectordbEmbeddingsAgent(
                client_service = vectordb_provider,
                embedding_llm = embedding_llm,
                retrieval_llm = retrieval_llm,
                documents = parametrization_docs,
                force_add_documents = True,
                collection_name = parametrization_collection_name,
            )

        # Create the output_folder and output_file if not exists
        os.makedirs(output_folder, exist_ok=True)
        output_file = ExcelService.create_file(
            output_file_path = os.path.join(output_folder, output_file_name),
            insert_columns_if_file_not_exists = PoC4Constants.OUTPUT_COLUMNS,
        )

        process_info: dict = {
            "files_able_to_extract_data": [],
            "files_unable_to_extract_data": [],
        }
        files_amount: int = len(input_files)
        files_cnt:int = 0

        # Process the input files
        for file_path in input_files:
            start_time = time.time()
            files_cnt += 1
            logging.info(f"#### Start processing file {files_cnt}/{files_amount}: {file_path} ####")

            excel_sheet_name = ExcelService.get_sheet_name(file_path)
            csv_file_path = ExcelService.convert_xlsx_to_csv(file_path, encoding=encoding)

            # Invoke chain
            chain_result = PoC4Implementation._get_chain_result(
                parametrization_agent,
                excel_sheet_name,
                parametrization_csv_file_path = ExcelService.convert_xlsx_to_csv(parametrization_file_path, encoding=encoding),
                csv_file_to_extract = csv_file_path,
                smarter_llm = ChatOpenAI(
                    api_key = openai_api_key,
                    model_name = "o1-mini-2024-09-12", # "o3-mini-2025-01-31" model it is only available from Tier 3 (https://platform.openai.com/docs/guides/rate-limits#usage-tiers)
                ) if use_smarter_model else None,
                add_csv_mapping_template_to_last_column = add_csv_mapping_template_to_last_column,
            )

            amount_of_data_rows_extracted = ExcelService.get_content_lines_of_csv_data(chain_result["result"])
            logging.info(f"'{file_path}' file chain result got {amount_of_data_rows_extracted} data rows:\n{chain_result}")

            if amount_of_data_rows_extracted > 0:
                # Process and save extracted data to the master file
                ExcelService.save_extracted_data_to_master_file(
                    output_file,
                    chain_result["result"],
                    file_extracted = file_path,
                    add_csv_mapping_template_to_last_column = add_csv_mapping_template_to_last_column,
                )
                process_info["files_able_to_extract_data"].append(os.path.basename(file_path))
            else:
                process_info["files_unable_to_extract_data"].append(os.path.basename(file_path))
                logging.info(f"'{file_path}' file had no extracted data.")

            logging.info(f"#### Finished processing file {files_cnt}/{files_amount} in {time.time() - start_time:.2f} seconds : {file_path} ####")

        return process_info

    @staticmethod
    def _get_chain_result(
        parametrization_agent: VectordbEmbeddingsAgent,
        excel_sheet_name: str,
        parametrization_csv_file_path: str,
        csv_file_to_extract: str = None,
        add_csv_mapping_template_to_last_column = True,
        smarter_llm: ChatOpenAI = None,
    ) -> dict:
        # Define Parsers
        header_output_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="table_header_row", description="The CSV header row where the table starts")])
        template_output_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="template_row", description="The CSV row that matches the template parametrization mapping")])
        output_map_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="output_map", description="The output map to extract data from CSV")])

        PoC4Utils.reset_temp_vars()
        first_rows_of_the_file_to_extract_data = ExcelService.get_excel_csv_to_csv_str(csv_file_to_extract, only_get_first_rows=5, csv_sep=';')

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
            | (smarter_llm if smarter_llm else parametrization_agent.retrieval_llm)
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
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Parametrization template question", PoC4Utils.update_temp_vars, x))
            | RunnableLambda(lambda x: [HumanMessage(content=x["prompt"])])
            | (smarter_llm if smarter_llm else parametrization_agent.retrieval_llm)
            | RunnableLambda(lambda x: LoggerService.log_and_return(template_output_parser.parse(x.content), "Parametrization template result"))
            | RunnableLambda(lambda x: {**x, 'template_row': x['template_row'].replace(PoC4Constants.PARAMETRIZATION_HEADER_FROM_VECTOR_SEARCH, '')})
            | RunnablePassthrough.assign(template_row=lambda x: f"{PoC4Constants.PARAMETRIZATION_HEADER_FROM_CSV}{ExcelService.get_the_most_similar_row_of_csv_file(parametrization_csv_file_path, x['template_row'])}")
        )

        chain_get_output_map = (
            RunnablePassthrough.assign(output_map = lambda x: ExcelService.map_parametrization_to_output(x['template_row']))
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Output Map result", PoC4Utils.update_temp_vars, x))
        )

        chain_get_all = chain_get_header | chain_get_template | chain_get_output_map
        result = chain_get_all.invoke({})
        logging.info(f"template_row & output_map = {result}")

        output_map = result["output_map"]
        for key, value in output_map.items():
            if value != "":
                continue

            chain_try_complete_template = (
                RunnableLambda(lambda _: {'prompt': prompts.TRY_COMPLETE_TEMPLATE_PROMPT.format(
                        empty_output_map_key=key,
                        file_to_extract_data=ExcelService.delete_columns_from_csv_string(first_rows_of_the_file_to_extract_data, PoC4Utils.get_non_empty_values(result["output_map"])),
                        format_instructions=output_map_parser.get_format_instructions(),
                    )}
                )
                | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Try complete template question"))
                | RunnableLambda(lambda x: [HumanMessage(content=x["prompt"])])
                | (smarter_llm if smarter_llm else parametrization_agent.retrieval_llm)
                | RunnableLambda(lambda x: LoggerService.log_and_return(output_map_parser.parse(x.content), "Try complete template result"))
            )
            try_value = chain_try_complete_template.invoke({})
            result["output_map"][key] = try_value["output_map"]
            logging.info(f"template_row & AI improved output_map = {result}")

        header_row_index = ExcelService.get_excel_csv_row_number(
            excel_file_path = csv_file_to_extract,
            excel_row_content = ExcelService.remove_last_column(PoC4Utils.temp_vars['table_header_row']),
            csv_sep = ';',
        ) - 1
        
        chain_extract_data = (
            RunnablePassthrough.assign(
                extracted_rows = lambda _: ExcelService.extract_standardized_data(
                    csv_path = csv_file_to_extract,
                    excel_header_row_index = header_row_index,
                    csv_mapping_template = result["output_map"],
                    add_csv_mapping_template_to_last_column = add_csv_mapping_template_to_last_column,
                )
            )
        )
        extracted_rows_result = chain_extract_data.invoke({})

        return {"result": extracted_rows_result["extracted_rows"]}
