import time
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from modules.logger.services.logger_service import LoggerService
import modules.poc4.poc4_email_gen_agent.prompts.poc4_email_gen_agent_prompts as prompts

class PoC4EmailGenAgent:
    """
    Class to interact with the AI Email Gen Agent.
    """
    @staticmethod
    def run(
        email_content: str,
        extracted_files_info: dict,
        openai_api_key: str,
        ai_model: str = "gpt-4o-mini-2024-07-18",
        use_logging_system: bool = False,
    ) -> dict:
        """
        Run the AI process for PoC3.

        Args:
            email_content (str): Email content to generate the AI response.
            extracted_files_info (dict): Information about the extracted files.
            openai_api_key (str): OpenAI API key.
            ai_model (str): AI model to use. Defaults to "gpt-4o-mini-2024-07-18".
            use_logging_system (bool): Flag to indicate if to use the logging system. Defaults to False.
        """
        # Config logs
        if use_logging_system:
            LoggerService.init()

        # Initialize vars to use with LangChain
        openai_llm = ChatOpenAI(
            api_key = openai_api_key,
            model_name = ai_model,
            temperature = 0,
        )

        # Process the received email
        start_time = time.time()
        logging.info(f"#### Start processing the received email: {email_content} ####")

        # Define & Invoke Chains
        email_body_parser = StructuredOutputParser.from_response_schemas([ResponseSchema(name="email_body", description="The email body to send")])
        chain_get_email = (
            ChatPromptTemplate.from_messages(
                messages = PoC4EmailGenAgent._format_prompt_messages_to_ChatPromptTemplate_messages([
                    {"role": "system", "content": prompts.EMAIL_GEN_SYSTEM_PROMPT.format(
                        format_instructions=email_body_parser.get_format_instructions(),
                    )},
                    *prompts.EMAIL_GEN_EXAMPLE_PROMPT,  # Unpack the examples
                    {"role": "user", "content": prompts.EMAIL_GEN_USER_PROMPT.format(
                        received_email=email_content,
                        extracted_files_info=extracted_files_info,
                    )},
                ])
            )
            | RunnableLambda(lambda x: LoggerService.log_and_return(x, "Email question"))
            | openai_llm
            | RunnableLambda(lambda x: LoggerService.log_and_return(email_body_parser.parse(x.content), "Email result"))
        )

        result = chain_get_email.invoke({})
        logging.info(f"#### Finished processing received email in {time.time() - start_time:.2f} seconds : {result["email_body"]} ####")

        return result

    @staticmethod
    def _format_prompt_messages_to_ChatPromptTemplate_messages(messages:list) -> list:
        """
        This function replaces '{' to '{{' and '}' to '}}' so messages can be used in ChatPromptTemplate.from_messages().
        """
        escaped_messages = []
        for message in messages:
            if "content" in message:
                escaped_message = {
                    "role": message["role"],
                    "content": message["content"].replace("{", "{{").replace("}", "}}")
                }
                escaped_messages.append(escaped_message)
            else:
                escaped_messages.append(message)
        return escaped_messages