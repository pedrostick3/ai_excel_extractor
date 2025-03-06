import logging
from modules.ai.services.openai_ai_service import OpenAiAiService
from modules.ai.core.agents.email_gen_agent.prompts import email_gen_agent_prompts

class EmailGenAgent:
    """
    Class to interact with the AI Email Gen Agent.
    """
    model = None

    def __init__(self,
        ai_service: OpenAiAiService,
        model: str,
    ):
        """
        Initialize the AI Agent.
        """
        self.ai_service = ai_service
        self.model = model

    def ask_ai(
        self,
        user_prompt: str,
        system_prompt: str = None,
        example_prompts: list[dict[str, str]] = None,
        tools: list[dict] = None,
        tool_choice: str = None,
        ai_analytics_file_name: str = None,
        log_messages: bool = True,
    ) -> str:
        """
        Ask the AI for a response based on the given email content.

        Args:
            user_prompt (str): The user prompt to be used.
            system_prompt (str): The system prompt to be used.
            example_prompts (list[dict[str, str]]): The example prompts to be used.
            tools (list[dict]): The tools to be used.
            tool_choice (str): Force the function calling by setting the tool choice to "required". [Source](https://community.openai.com/t/new-api-feature-forcing-function-calling-via-tool-choice-required/731488) 
            ai_analytics_file_name (str): The AI analytics file name to be used.
            log_messages (bool): Flag to indicate if the request messages should be logged.

        Returns:
            str: The AI's response.
        """
        try:
            ai_response = self.ai_service.ask_ai(
                model=self.model,
                system_prompt=system_prompt,
                example_prompts=example_prompts,
                first_user_prompt=user_prompt,
                tools=tools,
                tool_choice=tool_choice,
                use_assistant_instead_of_system=False,  # True caso o modelo seja "o1-preview" ou "o1-mini"
                response_format=None,
                ai_analytics_file_name=ai_analytics_file_name,
                ai_analytics_agent_name="EmailGenAgent",
                log_request_messages=log_messages,
                log_response_message=log_messages,
            )

            return ai_response
        except Exception as e:
            logging.error(f"Erro ao comunicar com o AI EmailGenAgent: {e}")
            raise
    
    def generate_email_response(
        self,
        email_content: str,
        processed_files: list[dict],
    ) -> str:
        """
        Generate the email response based on the given email content.

        Args:
            email_content (str): The email content.
            processed_files (list[dict]): The processed files.

        Returns:
            str: The AI's email response.
        """
        logging.info(f"AI EmailGenAgent - email_content = {email_content}")
        agent_response = self.ask_ai(
            system_prompt=email_gen_agent_prompts.EMAIL_GEN_SYSTEM_PROMPT,
            user_prompt=f"With this processed files:\n```{processed_files}```\nGenerate an email content response for the following email:\n{email_content}",
            example_prompts=email_gen_agent_prompts.EMAIL_GEN_EXAMPLE_PROMPTS,
        )
        logging.info(f"AI EmailGenAgent - agent_response = {agent_response}")
        return agent_response
