import time
import logging
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from modules.ai.core.agents.vectordb_embeddings_agent.utils.vectordb_embeddings_loader_utils import VectordbEmbeddingsLoaderUtils
from modules.logger.services.logger_service import LoggerService
from modules.poc_rag_email_gen_agent.utils.poc_rag_utils import PoCRagUtils
import modules.poc_rag_email_gen_agent.poc_rag_email_gen_agent_prompts as prompts
from modules.ai.core.agents.vectordb_embeddings_agent.vectordb_embeddings_agent import VectordbEmbeddingsAgent
from modules.ai.core.agents.vectordb_embeddings_agent.enums.vectordb_client_service_enum import VectordbClientServiceEnum
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import HumanMessage
from langchain_core.documents import Document


class PoCRagEmailGenAgent:
    """
    Class to interact with the AI Email Gen Agent.
    """
    @staticmethod
    def run(
        email_as_eml_paths: list[str],
        openai_api_key: str,
        ai_model: str = "gpt-4o-mini-2024-07-18",
        ai_embedding_model: str = "text-embedding-3-small",
        temporary_collection_name: str = "temporary_collection",
        extra_docs_to_vectorize: list[Document] = [],
        override_questions: str = None,
        encoding: str ='utf-8-sig',
        use_logging_system: bool = False,
    ) -> dict:
        """
        Run the AI process for PoC3.

        Args:
            email_as_eml_paths (list[str]): List of email paths.
            openai_api_key (str): OpenAI API key.
            ai_model (str): AI model to use. Defaults to "gpt-4o-mini-2024-07-18".
            ai_embedding_model (str): AI embedding model to use. Defaults to "text-embedding-3-small".
            temporary_collection_name (str): Name of temporary collection. Defaults to "temporary_collection".
            extra_docs_to_vectorize (list[Document]): Additional documents to vectorize.
            override_questions (str): Questions that will override the last email questions. Defaults None.
            encoding (str): Encoding of the input files. Defaults to "utf-8-sig".
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

        # Process emails
        start_time = time.time()
        logging.info(f"#### Start processing the received emails: {email_as_eml_paths} ####")

        # Sort emails with the most recent dates first
        email_as_eml_paths.sort(key=PoCRagUtils.get_email_date, reverse=True)

        # Load the most recent email body
        if email_as_eml_paths:
            most_recent_email_body = PoCRagUtils.get_email_body(email_as_eml_paths[0])
            logging.info(f"Body of the most recent email: {most_recent_email_body}")

        # Load email docs
        email_docs: list[Document] = []
        for email_path in email_as_eml_paths:
            email_docs.extend(VectordbEmbeddingsLoaderUtils.load_documents_from_eml(email_path))

        # Vectorize emails & Init VectordbAgent
        vectordb_agent = VectordbEmbeddingsAgent(
            client_service=vectordb_provider,
            embedding_llm=embedding_llm,
            retrieval_llm=retrieval_llm,
            documents=[*email_docs, *extra_docs_to_vectorize],
            collection_name=temporary_collection_name,
            force_add_documents=True,
        )

        # Invoke Chains
        result = PoCRagEmailGenAgent._get_chain_result(
            vectordb_agent=vectordb_agent,
            most_recent_email_body=most_recent_email_body,
            override_questions=override_questions,
        )
        logging.info(f"#### Finished processing received email in {time.time() - start_time:.2f} seconds : {result["email_body"]} ####")

        vectordb_agent.embeddings_vector_llm.delete_collection() # Delete old vectors

        return result
    
    @staticmethod
    def _get_chain_result(
        vectordb_agent: VectordbEmbeddingsAgent,
        most_recent_email_body: str = None,
        override_questions: str = None,
    ) -> dict:
        # Define Parsers
        email_questions_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="email_questions", description="The simplified questions of email")])
        email_body_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="email_body", description="The email body to send")])

        # Define Chains
        chain_get_most_recent_email_body_from_vectordb = (
            RunnablePassthrough.assign(question=lambda _: "Get the most recent email body")
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "The most recent email [Question]"))
            | vectordb_agent.qa_chain
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "The most recent email [Result]"))
        )

        chain_extract_simple_question = (
            RunnablePassthrough.assign(prompt=lambda x: prompts.EXTRACT_QUESTION_FROM_EMAIL_PROMPT.format(
                email=x,
                format_instructions=email_questions_parser.get_format_instructions(),
            ))
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Get simplified questions [Question]"))
            | RunnableLambda(lambda x: [HumanMessage(content=x["prompt"])])
            | vectordb_agent.retrieval_llm
            | RunnableLambda(lambda x: LoggerService.log_and_return(email_questions_parser.parse(x.content), "Get simplified questions [Result]"))
        )

        chain_answer_questions_with_vectordb = (
            RunnablePassthrough.assign(question=lambda x: override_questions if override_questions else x["email_questions"])
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Answer questions with VectorDB [Question]"))
            | vectordb_agent.qa_chain
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Answer questions with VectorDB [Result]"))
        )

        chain_add_sources_to_answer = (
            RunnablePassthrough.assign(prompt=lambda x: prompts.ADD_SOURCES_TO_ANSWER_PROMPT.format(
                answered_email=x,
                format_instructions=email_body_parser.get_format_instructions(),
            ))
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Add source to email response [Question]"))
            | RunnableLambda(lambda x: [HumanMessage(content=x["prompt"])])
            | vectordb_agent.retrieval_llm
            | RunnableLambda(lambda x: LoggerService.log_and_return(email_body_parser.parse(x.content), "Add source to email response [Result]"))
        )
        
        chain_prettify_email = (
            RunnablePassthrough.assign(prompt=lambda x: prompts.EMAIL_GEN_AND_PRETTIFY_PROMPT.format(
                original_email=most_recent_email_body,
                answered_email=x,
                format_instructions=email_body_parser.get_format_instructions(),
            ))
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Prettify email answers & sources [Question]"))
            | RunnableLambda(lambda x: [HumanMessage(content=x["prompt"])])
            | vectordb_agent.retrieval_llm
            | RunnableLambda(lambda x: LoggerService.log_and_return(email_body_parser.parse(x.content), "Prettify email answers & sources [Result]"))
        )

        # Invoke Chains
        if most_recent_email_body:
            chain_get_all = (
                RunnablePassthrough.assign(email_questions=lambda _: most_recent_email_body)
                | chain_extract_simple_question
                | chain_answer_questions_with_vectordb
                | chain_add_sources_to_answer
                | chain_prettify_email
            )
        else:
            chain_get_all = (
                chain_get_most_recent_email_body_from_vectordb
                | chain_extract_simple_question
                | chain_answer_questions_with_vectordb
                | chain_add_sources_to_answer
                | chain_prettify_email
            )
        
        return chain_get_all.invoke({})