import tiktoken
import logging
from typing import Dict

class TokenUtils:
    OPENAI_MODEL_TOKEN_LIMITS: Dict[str, int] = {
        "o1-preview": 128000,
        "o1-mini": 128000,
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-4o-mini-2024-07-18": 128000,
        "gpt-4": 8192,
        "gpt-4-turbo": 128000,
        "gpt-3.5-turbo": 4096,
    }

    @staticmethod
    def prompt_model_tokens_count(model: str, prompt: str, log_id: str = None) -> int:
        """
        Calculates the number of tokens in the prompt for the specified model.

        Args:
            model (str): The model name to calculate the token count for.
            prompt (str): The prompt string to calculate the token count for.

        Returns:
            int: The number of tokens in the prompt for the specified model.
        """
        if model not in TokenUtils.OPENAI_MODEL_TOKEN_LIMITS:
            raise ValueError(f"Model {model} not supported or unknown.")

        encoder = tiktoken.encoding_for_model(model)
        tokens = encoder.encode(prompt)
        token_count = len(tokens)

        log_identifier = log_id if log_id else "prompt"
        logging.info(f"Number of tokens in the {log_identifier}: {token_count}")

        return token_count
    
    @staticmethod
    def is_context_window_valid(model: str, conversation: str, log_id: str = None) -> bool:
        """
        Validates if the context window is within the maximum token limit for the specified model.

        Args:
            model (str): The model name to validate against.
            conversation (str): The conversation string to be validated.

        Returns:
            bool: True if the context window is valid, False otherwise.

        Raises:
            ValueError: If the model is not supported.
        """
        if model not in TokenUtils.OPENAI_MODEL_TOKEN_LIMITS:
            raise ValueError(f"Model {model} not supported or unknown.")

        token_limit = TokenUtils.OPENAI_MODEL_TOKEN_LIMITS[model]
        token_count = TokenUtils.prompt_model_tokens_count(model, conversation, log_id)

        return token_count <= token_limit

    @staticmethod
    def handle_prompt_for_max_model_tokens(model: str, prompt: str, truncate_if_exceeds: bool = True, log_id: str = None) -> str:
        """
        Validates if the prompt is within the maximum token limit for the specified model.
        If the prompt exceeds the limit and truncate_if_exceeds is True, the prompt is truncated to the model limit.
        If the prompt exceeds the limit and truncate_if_exceeds is False, an exception is raised.

        Args:
            model (str): The model name to validate against.
            prompt (str): The prompt string to be validated.
            truncate_if_exceeds (bool): Flag to indicate if the prompt should be truncated if it exceeds the limit.

        Returns:
            str: The original or truncated prompt based on the token limit.

        Raises:
            ValueError: If the model is not supported or if the prompt exceeds the token limit and truncate_if_exceeds is False.
        """
        if TokenUtils.is_context_window_valid(model, prompt, log_id):
            return prompt
        
        token_limit = TokenUtils.OPENAI_MODEL_TOKEN_LIMITS[model]
        if not truncate_if_exceeds:
            log_identifier = log_id if log_id else "prompt"
            raise ValueError(f"{log_identifier} exceeds the limit of {token_limit} tokens for the model {model}.")
        
        encoder = tiktoken.encoding_for_model(model)
        tokens = encoder.encode(prompt)
        truncated_tokens = tokens[:token_limit]
        logging.info(f"Number of tokens in the {log_identifier} truncated to: {len(truncated_tokens)}")
        return encoder.decode(truncated_tokens)