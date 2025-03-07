import os
import logging
import json
from modules.ai.services.openai_ai_service import OpenAiAiService
from modules.ai.core.fine_tuning_agents.excel_fine_tuning_agent import ExcelFinetuningAgent
from modules.ai.core.agents.email_gen_agent.email_gen_agent import EmailGenAgent
from modules.ai.core.enums.file_category import FileCategory
from modules.excel.services.excel_service import ExcelService
from modules.analytics.services.ai_analytics import AiAnalytics
from modules.poc4.poc4_implementation import PoC4Implementation
from modules.poc4.poc4_email_gen_agent.poc4_email_gen_agent import PoC4EmailGenAgent

OPENAI_FINE_TUNING_BASE_MODEL = "gpt-4o-mini-2024-07-18" # https://platform.openai.com/docs/models OR https://openai.com/api/pricing
OPENAI_FINE_TUNING_MODEL = "ft:gpt-4o-mini-2024-07-18:inspireit::Av1GNDPM" # Can be found in https://platform.openai.com/finetune/. It's the name of the model or you can check too in the 'Output model' propriety.
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

def runExcelAiAgentWith(
    openai_api_key: str,
    input_excel_file_path: str,
    output_folder_path: str = "./assets/docs_output",
    is_to_log: bool = False,
) -> dict:
    """
    Run the Excel AI Agent with the given parameters.

    Args:
        openai_api_key (str): The OpenAI API key.
        input_excel_file_path (str): The input Excel file path.
        output_folder_path (str): The output folder path.
        is_to_log (bool): Flag to indicate if it is to log.

    Returns:
        dict: The output Excel file path and category.

    Example:
        file_path_result = runExcelAiAgentWith(
            openai_api_key="YOUR_OPENAI_API_KEY",
            input_excel_file_path="./assets/docs_input/Execution_data Template.xlsx",
            output_folder_path="./assets/docs_output",
        )
        print(f"Output Excel file path: {file_path_result}") # Output Excel file path: ./assets/docs_output/Execução - 16_12_2024 - Execution_data Template.xlsx
    """

    # Configurar logs
    if is_to_log and not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("process.log", encoding='utf-8'), logging.StreamHandler()],
        )
    logging.info("# START - runExcelAiAgentWith()")

    # Configurar Fine-Tuning AI Service
    fine_tuning_agent = ExcelFinetuningAgent(
        ai_service=OpenAiAiService(api_key=openai_api_key),
        base_model=OPENAI_FINE_TUNING_BASE_MODEL,
        fine_tuning_model=OPENAI_FINE_TUNING_MODEL,
    )
    
    os.makedirs(output_folder_path, exist_ok=True) # Criar pasta de output se não existir

    # Processar ficheiro
    input_excel_file_name = os.path.basename(input_excel_file_path)
    logging.info(f"#### Start processing file: {input_excel_file_path} ####")

    # 1. 2. Categorizar Excel & perceber onde começa a tabela retornando a linha do cabeçalho
    logging.info("#1. 2. START - ExcelGenericFinetuningAgent")
    file_category_and_header = fine_tuning_agent.get_file_category_and_header(
        excel_file_path=input_excel_file_path,
        invalid_output_path=output_folder_path,
        ai_analytics_file_name=input_excel_file_name,
    )

    # Get category from the agent response
    try:
        category_by_ai = file_category_and_header['category']
    except KeyError as e:
        logging.error(f"Warning - Erro ao obter \"file_category_and_header['category']\": {e}\nfile_category_and_header = {file_category_and_header}")
        raise

    try:
        output_file_path = file_category_and_header['output_file_path']
    except KeyError as e:
        logging.error(f"Warning - Erro ao obter \"file_category_and_header['output_file_path']\": {e}\nfile_category_and_header = {file_category_and_header}")
        raise

    file_category = FileCategory.get_category_by_name(category_by_ai)
    logging.info(f"The file '{input_excel_file_name}' is '{file_category}' category.")
    if file_category == FileCategory.INVALIDO:
        logging.info(f"# END - runExcelAiAgentWith() - output_file_path: {output_file_path} ")
        logging.info(AiAnalytics.__str__())
        AiAnalytics.export_str_ai_analytics_data_to_excel()
        return {
            "output_file_path": output_file_path,
            "file_category": file_category.value,
        }

    # Get header from the agent response
    try:
        excel_header = file_category_and_header['header']['row_content']
    except KeyError as e:
        logging.error(f"Warning - Erro ao obter \"file_category_and_header['header']['row_content']\": {e}\nfile_category_and_header = {file_category_and_header}")
        raise
    logging.info("#1. 2. END - ExcelGenericFinetuningAgent")

    # 3. Modificar Excel antes do cabeçalho
    logging.info("#3. START - ExcelGenericFinetuningAgent")
    fine_tuning_agent.modify_pre_header(
        category=file_category,
        input_excel_file_path=input_excel_file_path,
        header_row_number=ExcelService.get_excel_csv_row_number(input_excel_file_path, excel_header),
        output_excel_file_path=output_file_path,
        ai_analytics_file_name=input_excel_file_name,
    )
    logging.info("#3. END - ExcelGenericFinetuningAgent")

    header_row_number = ExcelService.get_excel_csv_row_number(output_file_path, excel_header)

    # 4. Modificar Excel depois do cabeçalho
    logging.info("#4. START - ExcelGenericFinetuningAgent - modify_content_returning_function_calling()")
    fine_tuning_agent.modify_content_returning_function_calling(
        category=file_category,
        input_excel_file_path=output_file_path,
        output_excel_file_path=output_file_path,
        excel_header_row_index=header_row_number - 1, # -1 para obter o index
        ai_analytics_file_name=input_excel_file_name,
    )
    logging.info("#4. END - ExcelGenericFinetuningAgent - modify_content_returning_function_calling()")
    
    logging.info(f"# END - runExcelAiAgentWith() - output_file_path: {output_file_path}")
    logging.info(AiAnalytics.__str__())
    AiAnalytics.export_str_ai_analytics_data_to_excel()

    return {
        "output_file_path": output_file_path,
        "file_category": file_category.value,
    }

def runEmailGenAgentWith(
    openai_api_key: str,
    email_content: str,
    processed_files: list[dict],
    is_to_log: bool = False,
) -> str:
    """
    Run the Email Gen Agent with the given parameters.

    Args:
        openai_api_key (str): The OpenAI API key.
        email_content (str): The email content.
        processed_files (list[dict]): The processed files information.
        is_to_log (bool): Flag to indicate if it is to log.

    Returns:
        str: The email response.
    """
    # Configurar logs
    if is_to_log and not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("process.log", encoding='utf-8'), logging.StreamHandler()],
        )
    logging.info("# START - runEmailGenAgentWith()")

    # Configurar Agent Service
    agent_service = EmailGenAgent(
        ai_service=OpenAiAiService(api_key=openai_api_key),
        model=OPENAI_FINE_TUNING_BASE_MODEL,
    )

    # Obter resposta do AI
    email_response = agent_service.generate_email_response(
        email_content=email_content,
        processed_files=processed_files,
    )
    logging.info(f"# END - runEmailGenAgentWith() - Email response: {email_response}")
    
    logging.info(AiAnalytics.__str__())
    AiAnalytics.export_str_ai_analytics_data_to_excel()

    return email_response

def testRunExcelAiAgentOnly(
    openai_api_key: str,
    execution_data_file_path: str = "./assets/docs_input/Execution_data Template.xlsx",
    test_execution_data_file_path: str = "./assets/docs_input/Test_Execution_data Template.xlsx",
    parameterization_file_path: str = "./assets/docs_input/ParameterizationFile_testes_13112024.xlsx",
    output_folder_path: str = "./assets/docs_output",
) -> str:
    execution_data_file_result = runExcelAiAgentWith(
        openai_api_key=openai_api_key,
        input_excel_file_path=execution_data_file_path,
        output_folder_path=output_folder_path,
    )
    test_execution_data_file_result = runExcelAiAgentWith(
        openai_api_key=openai_api_key,
        input_excel_file_path=test_execution_data_file_path,
        output_folder_path=output_folder_path,
    )
    parameterization_file_result = runExcelAiAgentWith(
        openai_api_key=openai_api_key,
        input_excel_file_path=parameterization_file_path,
        output_folder_path=output_folder_path,
    )
    return json.dumps([execution_data_file_result, test_execution_data_file_result, parameterization_file_result])

def testRunEmailGenAgentOnly(
    openai_api_key: str,
    email_content: str = "Hello Nexis, I hope you are doing well. I am contacting you to process the attached file. Awaiting your response, Daniel Soares",
    processed_files: list[dict] = [{
            "output_file_path": "./assets/docs_input/Test_Execution_data Template.xlsx",
            "file_category": "Teste Execução",
    }],
) -> str:
    email_response = runEmailGenAgentWith(
        openai_api_key=openai_api_key,
        email_content=email_content,
        processed_files=processed_files,
    )
    return email_response

def testRunBothAgents(
    openai_api_key: str,
    email_content: str = "Hello Nexis, I hope you are doing well. I am contacting you to process the attached files. Awaiting your response, Daniel Soares",
    files_paths: list[str] = [
        "./assets/docs_input/Execution_data Template.xlsx",
        "./assets/docs_input/Test_Execution_data Template.xlsx",
        "./assets/docs_input/ParameterizationFile_testes_13112024.xlsx",
    ],
    output_folder_path: str = "./assets/docs_output",
) -> str:
    to_return = {"processed_files": []}
    for file_path in files_paths:
        file_result = runExcelAiAgentWith(
            openai_api_key=openai_api_key,
            input_excel_file_path=file_path,
            output_folder_path=output_folder_path,
        )
        to_return["processed_files"].append(file_result)

    to_return["email_content"] = runEmailGenAgentWith(
        openai_api_key=openai_api_key,
        email_content=email_content,
        processed_files=to_return["processed_files"],
    )

    return json.dumps(to_return)

def testRunBothAgentsWithSingleFile(
    openai_api_key: str,
    email_content: str = "Hello Nexis, I hope you are doing well. I am contacting you to process the attached file. Awaiting your response, Daniel Soares",
    file_path: str = "./assets/docs_input/Test_Execution_data Template.xlsx",
    output_folder_path: str = "./assets/docs_output",
) -> str:
    to_return = {}
    file_result = runExcelAiAgentWith(
        openai_api_key=openai_api_key,
        input_excel_file_path=file_path,
        output_folder_path=output_folder_path,
    )
    to_return["processed_file"] = file_result

    to_return["email_content"] = runEmailGenAgentWith(
        openai_api_key=openai_api_key,
        email_content=email_content,
        processed_files=[to_return["processed_file"]],
    )

    return json.dumps(to_return)

def runExcelExtractionAgentWith(
    openai_api_key: str,
    files_paths: list[str] = [
        "./assets/docs_input/data_to_extract/8.54€ SGF 092024.xlsx",
        "./assets/docs_input/data_to_extract/29.47€ Mapa Fundo Pensoes Sindicato Quadros_OUT2024.xlsx",
        "./assets/docs_input/data_to_extract/73.19€ MAPA FUNDO PENSÕES SAMS QUADROS - 09.2024.xlsx",
        "./assets/docs_input/data_to_extract/201.33€ 06 - FP - Junho 2024.xlsx",
        "./assets/docs_input/data_to_extract/334.39€ FP_SNQTB_102024.xlsx",
    ],
    parametrization_file_path: str = "./assets/docs_input/ParameterizationFileCarpenter.xlsx",
    output_folder_path: str = "./assets/docs_output",
    output_file_name: str = "mestre dados_finais.xlsx",
) -> dict:
    return PoC4Implementation.run(
        input_files=files_paths,
        parametrization_file_path=parametrization_file_path,
        output_folder=output_folder_path,
        output_file_name=output_file_name,
        openai_api_key=openai_api_key,
        ai_embedding_model=OPENAI_EMBEDDING_MODEL,
        ai_model=OPENAI_FINE_TUNING_BASE_MODEL,
        #update_parametrization_vector_db=True,
    )

def testPoC4EmailGenAgent(
    openai_api_key: str,
    email_content: str = "Hello Nexis, I hope you are doing well. I am contacting you to extract data from the attached files. Awaiting your response, Daniel Soares",
    extracted_files_info: str = "{'files_able_to_extract_data': ['8.54€ SGF 092024.xlsx', '29.47€ Mapa Fundo Pensoes Sindicato Quadros_OUT2024.xlsx'], 'files_unable_to_extract_data': ['334.39€ FP_SNQTB_102024.xlsx']}",
) -> dict:
    return PoC4EmailGenAgent.run(
        email_content=email_content,
        extracted_files_info=extracted_files_info,
        openai_api_key=openai_api_key,
        ai_model=OPENAI_FINE_TUNING_BASE_MODEL,
        #use_logging_system=True,
    )

def runExcelExtractionAgentWithPoC4EmailGenAgent(
    openai_api_key: str,
    email_content: str = "Hello Nexis, I hope you are doing well. I am contacting you to extract data from the attached files. Awaiting your response, Daniel Soares",
    files_paths: list[str] = [
        "./assets/docs_input/data_to_extract/8.54€ SGF 092024.xlsx",
        "./assets/docs_input/data_to_extract/29.47€ Mapa Fundo Pensoes Sindicato Quadros_OUT2024.xlsx",
        "./assets/docs_input/data_to_extract/73.19€ MAPA FUNDO PENSÕES SAMS QUADROS - 09.2024.xlsx",
        "./assets/docs_input/data_to_extract/201.33€ 06 - FP - Junho 2024.xlsx",
        "./assets/docs_input/data_to_extract/334.39€ FP_SNQTB_102024.xlsx",
    ],
    parametrization_file_path: str = "./assets/docs_input/ParameterizationFileCarpenter.xlsx",
    output_folder_path: str = "./assets/docs_output",
    output_file_name: str = "mestre dados_finais.xlsx",
) -> dict:
    to_return = {}

    to_return["extracted_files_info"] = PoC4Implementation.run(
        input_files=files_paths,
        parametrization_file_path=parametrization_file_path,
        output_folder=output_folder_path,
        output_file_name=output_file_name,
        openai_api_key=openai_api_key,
        ai_embedding_model=OPENAI_EMBEDDING_MODEL,
        ai_model=OPENAI_FINE_TUNING_BASE_MODEL,
        #use_logging_system=True,
        #update_parametrization_vector_db=True,
    )

    to_return["email_content"] = PoC4EmailGenAgent.run(
        email_content=email_content,
        extracted_files_info=to_return["extracted_files_info"],
        openai_api_key=openai_api_key,
        ai_model=OPENAI_FINE_TUNING_BASE_MODEL,
        #use_logging_system=True,
    )

    to_return["extracted_files_info"]["output_file_path_with_the_extracted_data"] = f"{output_folder_path}/{output_file_name}"

    return json.dumps(to_return)

if __name__ == "__main__":
    results = runExcelExtractionAgentWithPoC4EmailGenAgent("YOUR_OPENAI_API_KEY")
    print(f"Results: {results}")