from modules.analytics.services.ai_analytics import AiAnalytics
from modules.ai.utils.token_utils import TokenUtils
import json
import openai
import logging
import time

class OpenAiAiService:
    """
    Service class to interact with OpenAI AI for generating responses based on prompts.
    """

    def __init__(self, api_key: str):
        """
        Initialize the OpenAI API.
        """
        openai.api_key = api_key
        self.client = openai

    def get_ai_client(self) -> openai:
        """
        Get the client to be used for the AI/ML API.

        Returns:
            object: The client to be used.
        """
        return self.client

    def ask_ai(
        self,
        model: str,
        first_user_prompt: str,
        system_prompt: str = None,
        example_prompts: list[dict[str, str]] = None,
        continuous_user_conversation_prompt: str = None,
        use_assistant_instead_of_system: bool = False,
        response_format: dict = {"type": "json_object"},
        temperature: float = 1,
        top_p: float = 1,
        tools: list[dict] = None,
        tool_choice: str = None,
        base_model: str = None,
        ai_analytics_file_name: str = None,
        ai_analytics_agent_name: str = None,
        log_request_messages: bool = True,
        log_response_message: bool = True,
    ) -> str:
        """
        Ask the AI for a response based on the given prompt.

        Args:
            model (str): The model to be used.
            first_user_prompt (str): The first user prompt to be used.
            system_prompt (str): The system prompt to be used.
            example_prompts (list[dict[str, str]]): The example prompts to be used.
            continuous_user_conversation_prompt (str): The continuous user conversation message to be used.
            use_assistant_instead_of_system (bool): Flag to indicate if the assistant should be used instead of the system. "o1-preview" and "o1-mini" models require this parameter to be True.
            response_format (dict): The response format to be used.
            temperature (float): The temperature to be used that determines the randomness of the response [deterministic = 0 < temp < 2 = creative].
            top_p (float): The nucleus sampling parameter to be used. It is the probability mass below which, the model will not consider the next token [0 < top_p <= 1].
            tools (list[dict]): The tools to be used.
            tool_choice (str): Force the function calling by setting the tool choice to "required". [Source](https://community.openai.com/t/new-api-feature-forcing-function-calling-via-tool-choice-required/731488) 
            base_model (str): The base model to be used in the Tokenizer.
            ai_analytics_file_name (str): The AI analytics file name to be used.
            ai_analytics_agent_name (str): The AI analytics agent name to be used.
            log_request_messages (bool): Flag to indicate if the request messages should be logged.
            log_response_message (bool): Flag to indicate if the response message should be logged.

        Returns:
            str: The AI's response.
        """
        try:
            if continuous_user_conversation_prompt:
                self.followup_conversation_messages.append(self._get_message_dict(role="user", content=continuous_user_conversation_prompt, tools=tools))
            else:
                ai_role = "assistant" if use_assistant_instead_of_system else "system"

                messages = []
                if system_prompt:
                    messages.append(self._get_message_dict(role=ai_role, content=system_prompt))
                if example_prompts and len(example_prompts) % 2 == 0:
                    messages.extend(example_prompts)
                messages.append(self._get_message_dict(role="user", content=first_user_prompt, tools=tools))

                self.followup_conversation_messages = messages
            
            
            self.followup_conversation_messages = self._handle_conversation_messages_length(
                base_model if base_model else model,
                self.followup_conversation_messages,
                not_to_replace_first_messages=1 + len(example_prompts) if example_prompts and len(example_prompts) % 2 == 0 else 1, # system_prompt + example_prompts
            )

            if log_request_messages:
                logging.info(f"request messages: {self.followup_conversation_messages}")

            logging.info(f"Wait for AI response...")
            start_time = time.time()
            response = self.get_ai_client().chat.completions.create(
                model=model,
                messages=self.followup_conversation_messages,
                response_format=response_format,
                temperature=temperature,
                top_p=top_p,
                tools=tools,
                tool_choice=tool_choice,
            )
            execution_time = time.time() - start_time
            logging.info(f"AI response received after {execution_time} seconds")
            AiAnalytics.add_file_agent_request(
                file_name=ai_analytics_file_name,
                agent_name=ai_analytics_agent_name,
                ai_model=model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                execution_time_in_seconds=execution_time,
            )

            message = response.choices[0].message
            messageContent = message.content
            messageFunctionCalls = message.tool_calls[0] if message.tool_calls else None

            if log_response_message:
                logging.info(f"response messages usage: {response.usage}")
                logging.info(f"response message: {message}")
                logging.info(f"response message model_dump_json: {message.model_dump_json()}")
                logging.info(f"response message content: {messageContent}")
                if tools and messageFunctionCalls:
                    logging.info(f"response message tool function calls: {messageFunctionCalls}")
                    logging.info(f"response message tool function calls model_dump_json: {messageFunctionCalls.model_dump_json()}")

            self.followup_conversation_messages.append(message)

            return messageFunctionCalls.model_dump_json() if tools and messageFunctionCalls else messageContent
        except Exception as e:
            logging.error(f"Erro ao comunicar com a AI: {e}")
            raise

    def _handle_conversation_messages_length(self, model: str, messages: list[dict], not_to_replace_first_messages: int = 0) -> list[dict]:
        """
        Handles the conversation messages length to ensure it is within the maximum token limit for the specified model.

        Args:
            model (str): The model name to validate against.
            messages (list[dict]): The conversation messages to be validated.

        Returns:
            list[dict]: The conversation messages with the correct length.
        """
        while not TokenUtils.is_context_window_valid(model, json.dumps(messages), log_id="messages") and len(messages) > 1:
            messages.pop(not_to_replace_first_messages)
        logging.info(f"Exists {len(messages)} messages in the conversation, with the following roles: {', '.join([message['role'] for message in messages])}.")
        return messages
    
    def _get_message_dict(self, role: str, content: str, tools: list[dict] = None) -> dict:
        """
        Creates a message dictionary.

        Args:
            role (str): The role of the message.
            content (str): The content of the message.
            tools (list[dict]): The tools associated with the message.

        Returns:
            dict: The message dictionary.
        """
        message = {"role": role, "content": content}
        if tools:
            message["tools"] = tools
        return message