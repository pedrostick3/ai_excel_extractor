import time
import logging
from langchain_openai import ChatOpenAI
from constants import configs
from modules.logger.services.logger_service import LoggerService
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType

class LangChainAgent:
    """
    Class to interact with the AI Langchain Agent.
    """
    @staticmethod
    def run_agent_type_zero_shot_react_description(
        openai_api_key: str = configs.OPENAI_API_KEY,
        ai_model: str = configs.OPENAI_FINE_TUNING_BASE_MODEL,
        use_logging_system: bool = True,
    ) -> dict:
        """
        Run the AI to test the Agent.

        Args:
            openai_api_key (str): OpenAI API key.
            ai_model (str): AI model to use. Defaults to "gpt-4o-mini-2024-07-18".
            use_logging_system (bool): Flag to indicate if to use the logging system. Defaults to True.
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
        tools = load_tools(["llm-math"], llm=openai_llm)
        agent_executor = initialize_agent(
            tools=tools,
            llm=openai_llm,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

        start_time = time.time()
        logging.info(f"#### Start processing with AgentType.ZERO_SHOT_REACT_DESCRIPTION ####")
        result = agent_executor.run("I have 20 candies. If I share them equally with my friends, there are 2 left over. If one more person joins us, there are 6 candies left. How many friends am I with?")
        # Answer: 6 people altogether (so 5 friends!)
        logging.info(f"#### Finished processing in {time.time() - start_time:.2f} seconds : {result} ####")

        return result
