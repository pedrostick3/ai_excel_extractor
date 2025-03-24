import time
import logging
from constants import configs
from modules.logger.services.logger_service import LoggerService
from modules.ai.langsmith.services.langsmith_service import LangSmithService
from modules.ai.langgraph_agent.models.agent_state import AgentState
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from functools import partial
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import Literal

class LangGraphAgentWithWeatherTool:
    """
    Class to interact with the AI Langchain Agent.
    """
    @staticmethod
    def run(
        openai_api_key: str = configs.OPENAI_API_KEY,
        ai_model: str = configs.OPENAI_FINE_TUNING_BASE_MODEL,
        use_langsmith: bool = True,
        use_logging_system: bool = True,
    ) -> dict:
        """
        Run the AI te test the Agent.

        Args:
            openai_api_key (str): OpenAI API key.
            ai_model (str): AI model to use. Defaults to "gpt-4o-mini-2024-07-18".
            use_langsmith (bool): Flag to indicate if to use LangSmith. Defaults to True.
            use_logging_system (bool): Flag to indicate if to use the logging system. Defaults to True.
        """
        # Config logs
        if use_logging_system:
            LoggerService.init()
        
        # Initialize LangSmith if enabled
        if use_langsmith:
            LangSmithService.init_service(langsmith_project=configs.LANGSMITH_PROJECT_TEST_LANGGRAPH)

        # Initialize vars to use with LangChain
        openai_llm = ChatOpenAI(
            api_key = openai_api_key,
            model_name = ai_model,
            temperature = 0,
        )
        tools = [LangGraphAgentWithWeatherTool._get_weather]
        openai_llm_with_tools = openai_llm.bind_tools(tools)
        tool_node = ToolNode(tools)
        workflow = StateGraph(AgentState)
        workflow.add_node("tool_node", tool_node)
        workflow.add_node("prompt_node", partial(LangGraphAgentWithWeatherTool._prompt_node, llm=openai_llm_with_tools))
        workflow.add_conditional_edges("prompt_node", LangGraphAgentWithWeatherTool._conditional_edge)
        workflow.add_edge("tool_node", "prompt_node")
        workflow.set_entry_point("prompt_node")
        graph = workflow.compile()

        # Save graph to PNG file (visual debug purposes)
        try:
            image_data = graph.get_graph().draw_mermaid_png()
            with open("./assets/docs_output/workflow-of-weather-agent.png", "wb") as f:
                f.write(image_data)
            logging.info("Graph saved to ./assets/docs_output/workflow-of-weather-agent.png")
        except Exception as e:
            logging.info(f"Could not save graph: {str(e)}")


        start_time = time.time()
        logging.info(f"#### Start processing ####")
        new_state = graph.invoke({"messages": [HumanMessage(content="What's the weather in Brazil?")]})
        result = new_state["messages"][-1].content
        logging.info(f"#### Finished processing in {time.time() - start_time:.2f} seconds : {result} ####")

        return result
    
    @tool
    @staticmethod
    def _get_weather(location: str) -> str:
        """Call to get the current weather."""
        if location.lower() in ["brazil"]:
            return "It's sunny with 20°C."
        else:
            return "It's cold with 10°C."

    @staticmethod
    def _prompt_node(
        state: AgentState,
        llm: ChatOpenAI,
    ) -> dict:
        new_messages = llm.invoke(state["messages"])
        return {"messages": [new_messages]}
    
    
    @staticmethod
    def _conditional_edge(state: AgentState) -> Literal['tool_node', '__end__']:
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tool_node"
        else:
            return "__end__"

