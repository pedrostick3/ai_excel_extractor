import pandas as pd
import logging
import constants.configs as configs
from modules.ai.langchain_agent.langchain_agent import LangChainAgent
from modules.ai.langgraph_agent.langgraph_agent_with_weather_tool import LangGraphAgentWithWeatherTool
from modules.ai.langgraph_agent.langgraph_multi_agents import LangGraphMultiAgents
from modules.ai.langsmith.services.langsmith_service import LangSmithService
from modules.enums.ai_implementation import AiImplementation
from langchain_community.document_loaders import CSVLoader, WebBaseLoader, DirectoryLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from modules.ai.agents.pandas_dataframe_agent.pandas_dataframe_agent import PandasDataframeAgent
from modules.ai.agents.vectordb_embeddings_agent.vectordb_embeddings_agent import VectordbEmbeddingsAgent
from modules.ai.agents.vectordb_embeddings_agent.enums.vectordb_client_service_enum import VectordbClientServiceEnum
from langchain_docling import DoclingLoader
from modules.excel.services.excel_service import ExcelService
from modules.logger.services.logger_service import LoggerService
from modules.poc4.poc4_implementation import PoC4Implementation
from modules.poc_rag_email_gen_agent.poc_rag_email_gen_agent import PoCRagEmailGenAgent

AI_IMPLEMENTATION = AiImplementation.TEST_LANGGRAPH_MULTI_AGENT


def main():
    print("Main START")

    # Config logs
    LoggerService.init()

    # PoC3 Files to process
    input_files = [
        ###### Main Files:
        # "Execution_data Template.xlsx",
        # "ParameterizationFile_testes_13112024.xlsx",
        # "Test_Execution_data Template.xlsx",
        ###### Test Files (Invalid category):
        # "ParameterizationFile_testes_13112024.csv",
        # "Inspire IT - GenAI LLM RPA PoC.docx",
        ###### Test Files (Data To Extract):
        "./assets/docs_input/data_to_extract/8.54€ SGF 092024.xlsx",
        "./assets/docs_input/data_to_extract/29.47€ Mapa Fundo Pensoes Sindicato Quadros_OUT2024.xlsx",
        "./assets/docs_input/data_to_extract/73.19€ MAPA FUNDO PENSÕES SAMS QUADROS - 09.2024.xlsx",
        "./assets/docs_input/data_to_extract/201.33€ 06 - FP - Junho 2024.xlsx",
        "./assets/docs_input/data_to_extract/334.39€ FP_SNQTB_102024.xlsx",
    ]

    if AI_IMPLEMENTATION == AiImplementation.TEST_PANDAS_DATAFRAME_TOOL_AGENT:
        logging.info("START - AiImplementation.TEST_PANDAS_DATAFRAME_TOOL_AGENT")
        df = pd.read_excel(f"{configs.INPUT_FOLDER}/ParameterizationFile_testes_13112024.xlsx")  # podem ser online files
        agent = PandasDataframeAgent(
            llm=ChatOpenAI(
                api_key=configs.OPENAI_API_KEY,
                model=configs.OPENAI_FINE_TUNING_BASE_MODEL,
                temperature=0,
            ),
            dataframes=df,
        )

        response1 = agent.invoke(question="Which Templates corresponds the Quota: quota sams sócio.")
        logging.info(f"AiImplementation.TEST_PANDAS_DATAFRAME_TOOL_AGENT - invoke response1 = {response1}")

        response2 = agent.invoke_returning_response_model(question="Which Templates corresponds the Quota: quota sams sócio.")
        logging.info(f"AiImplementation.TEST_PANDAS_DATAFRAME_TOOL_AGENT - invoke_returning_response_model response2 = {response2}")
    elif AI_IMPLEMENTATION == AiImplementation.TEST_VECTORDB_EMBEDDINGS_AGENT:
        logging.info("START - AiImplementation.TEST_VECTORDB_EMBEDDINGS_AGENT")

        csv_path = ExcelService.convert_xlsx_to_csv(f"{configs.INPUT_FOLDER}/ParameterizationFile_testes_13112024.xlsx")

        # CSVLoader.load() faz logo o split por row, não existindo a necessidade de se ter de criar chunks com o RecursiveCharacterTextSplitter.
        # [LangChain CSVLoader Documentation](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.csv_loader.CSVLoader.html)
        docs = CSVLoader(
            csv_path,
            #csv_args={"delimiter": ";", "fieldnames": ["Template","Nome","Quota","Pivot","Sheet","NIF","Nsocio","SeparadorMilhar","SeparadorDecimal","Moeda","Remover linhas com","RemoverLinhaFinal","IgnorarLinhasSemValorDesconto","Taxa","MesReferencia"]},
        ).load()

        vectordb_provider = VectordbClientServiceEnum.CHROMA

        agent = VectordbEmbeddingsAgent(
            client_service=vectordb_provider,
            embedding_llm=OpenAIEmbeddings(
                api_key=configs.OPENAI_API_KEY,
                model=configs.OPENAI_EMBEDDING_MODEL,
            ),
            retrieval_llm=ChatOpenAI(
                api_key=configs.OPENAI_API_KEY,
                model_name=configs.OPENAI_FINE_TUNING_BASE_MODEL,
                temperature=0,
            ),
            documents=docs,
        )

        response1 = agent.invoke_similarity_search_with_score(question="Which Templates corresponds the Quota: quota sams sócio.")
        logging.info(f"AiImplementation.TEST_PANDAS_DATAFRAME_TOOL_AGENT - invoke_similarity_search_with_score response1 = {response1}")
        
        response2 = agent.invoke(question="Which Templates corresponds the Quota: quota sams sócio.")
        logging.info(f"AiImplementation.TEST_PANDAS_DATAFRAME_TOOL_AGENT - invoke response2 = {response2}")
        
        if vectordb_provider == VectordbClientServiceEnum.FAISS:
            response3 = agent.invoke_saving_and_reloading_local_FAISS_index(question="Which Templates corresponds the Quota: quota sams sócio.")
            logging.info(f"AiImplementation.TEST_PANDAS_DATAFRAME_TOOL_AGENT - invoke_saving_and_reloading_local_FAISS_index response3 = {response3}")
    elif AI_IMPLEMENTATION == AiImplementation.TEST_RAG:
        logging.info("START - AiImplementation.TEST_RAG")

        vectordb_provider = VectordbClientServiceEnum.PINECONE
        csv_docs = DirectoryLoader(configs.INPUT_FOLDER, glob="**/*.csv", loader_cls=CSVLoader, show_progress=True).load_and_split()
        docx_docs = DoclingLoader([f"{configs.INPUT_FOLDER}/Inspire IT - GenAI LLM RPA PoC.docx"]).load_and_split()
        web_docs = WebBaseLoader(["https://inspireit.pt/pt/"]).load_and_split()

        agent = VectordbEmbeddingsAgent(
            client_service=vectordb_provider,
            embedding_llm=OpenAIEmbeddings(
                api_key=configs.OPENAI_API_KEY,
                model=configs.OPENAI_EMBEDDING_MODEL,
            ),
            retrieval_llm=ChatOpenAI(
                api_key=configs.OPENAI_API_KEY,
                model_name=configs.OPENAI_FINE_TUNING_BASE_MODEL,
                temperature=0,
            ),
            documents=[*csv_docs, *docx_docs, *web_docs],
        )

        response1 = agent.invoke(question="Who is InspireIT? (get it's contacts)")
        logging.info(f"AiImplementation.TEST_RAG - invoke response1 = {response1}")
        
        response2 = agent.invoke(question="O que é o PoC 4?")
        logging.info(f"AiImplementation.TEST_RAG - invoke response2 = {response2}")
        
        response3 = agent.invoke(question="Qual o nome e a quota do template 'Template SAMS_2'?") # Nome = Colaborador | Quota = Desconto Total
        logging.info(f"AiImplementation.TEST_RAG - invoke response3 = {response3}")
        
        response4 = agent.invoke(question="Quem é a InspireIT e qual o nome e a quota do template 'Template SAMS_2'?") # Nome = Colaborador | Quota = Desconto Total
        logging.info(f"AiImplementation.TEST_RAG - invoke response4 = {response4}")
    elif AI_IMPLEMENTATION == AiImplementation.POC_4:
        logging.info("START - AiImplementation.POC_4")
        results = PoC4Implementation.run(input_files=input_files)
        print(f"Results: {results}")
    elif AI_IMPLEMENTATION == AiImplementation.TEST_LANGSMITH:
        logging.info("START - AiImplementation.TEST_LANGSMITH")
        LangSmithService.init_service()

        # Test with PoC4
        results = PoC4Implementation.run(input_files=input_files)
        print(f"Results: {results}")
    elif AI_IMPLEMENTATION == AiImplementation.POC_RAG:
        logging.info("START - AiImplementation.POC_RAG")
        
        #from langchain_community.document_loaders import WebBaseLoader
        #inspire_web_docs = WebBaseLoader(["https://inspireit.pt/pt/"], encoding='utf-8-sig').load_and_split()
        # Question = "Who is InspireIT? (get it's contacts)"

        result = PoCRagEmailGenAgent.run(
            email_as_eml_paths=[
                "./assets/docs_input/emails/poc3_email_ask_for_modification.eml",
                "./assets/docs_input/emails/poc3_email_response_with_processed_files.eml",
                "./assets/docs_input/emails/poc4_email_ask_to_extract_data.eml",
                "./assets/docs_input/emails/poc4_email_response_with_extracted_data.eml",
                "./assets/docs_input/emails/poc_rag_email_with_questions.eml",
                #"./assets/docs_input/emails/uipath_extracted_emls/Extract Data20250314_152830.eml",
                #"./assets/docs_input/emails/uipath_extracted_emls/RE Extract Data20250314_152827.eml",
                #"./assets/docs_input/emails/uipath_extracted_emls/RE Extract Data20250314_155113.eml",
            ],
            #extra_docs_to_vectorize=[*inspire_web_docs],
            openai_api_key=configs.OPENAI_API_KEY,
            ai_embedding_model=configs.OPENAI_EMBEDDING_MODEL,
            ai_model = configs.OPENAI_FINE_TUNING_BASE_MODEL,
            #override_questions="What's Germano Dias NIF?",
        )
        logging.info(f"Result: {result}")
    elif AI_IMPLEMENTATION == AiImplementation.TEST_LANGCHAIN_AGENT:
        logging.info("START - AiImplementation.TEST_LANGCHAIN_AGENT")
        LangChainAgent.run_agent_type_zero_shot_react_description()
    elif AI_IMPLEMENTATION == AiImplementation.TEST_LANGGRAPH_AGENT:
        logging.info("START - AiImplementation.TEST_LANGGRAPH_AGENT")
        LangGraphAgentWithWeatherTool.run()
    elif AI_IMPLEMENTATION == AiImplementation.TEST_LANGGRAPH_MULTI_AGENT:
        logging.info("START - AiImplementation.TEST_LANGGRAPH_MULTI_AGENT")
        LangGraphMultiAgents.run()

    print("Main END")


if __name__ == "__main__":
    main()
