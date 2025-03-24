import time
import logging
from constants import configs
from modules.ai.langgraph_agent.tools.langgraph_tools import LangGraphTools
from modules.logger.services.logger_service import LoggerService
from modules.ai.langsmith.services.langsmith_service import LangSmithService
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import CompiledGraph
from functools import partial
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import Literal

class LangGraphMultiAgents:
    """
    Class to interact with AI Langchain Multi Agents.
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
            LangSmithService.init_service(langsmith_project=configs.LANGSMITH_PROJECT_TEST_LANGGRAPH_MULTI_AGENTS)

        # Initialize vars to use with LangGraph
        openai_llm = ChatOpenAI(
            api_key = openai_api_key,
            model_name = ai_model,
            temperature = 0,
        )
        research_agent = create_react_agent(
            model=openai_llm,
            tools=[LangGraphTools.tavily_tool],
            prompt=LangGraphTools.BASE_SYSTEM_MESSAGE.format(
                system_message="You can only do research. You are working with a chart generator colleague.",
            ),
            name="researcher_agent",
        )
        chart_agent = create_react_agent(
            model=openai_llm,
            tools=[LangGraphTools.python_repl_tool],
            prompt=LangGraphTools.BASE_SYSTEM_MESSAGE.format(
                system_message="You can only generate charts. You are working with a researcher colleague.",
            ),
            name="chart_generator_agent",
        )

        # Create Graph
        workflow = StateGraph(MessagesState)
        workflow.add_node("researcher", partial(LangGraphMultiAgents._prompt_node, agent=research_agent))
        workflow.add_node("chart_generator", partial(LangGraphMultiAgents._prompt_node, agent=chart_agent))

        workflow.add_edge(START, "researcher")
        workflow.add_conditional_edges(
            "researcher",
            LangGraphMultiAgents._router,
            {"continue": "chart_generator", "end": END},
        )
        workflow.add_conditional_edges(
            "chart_generator",
            LangGraphMultiAgents._router,
            {"continue": "researcher", "end": END},
        )

        graph = workflow.compile()
        
        # Save graph to PNG file (visual debug purposes)
        try:
            image_data = graph.get_graph().draw_mermaid_png()
            with open("./assets/docs_output/workflow-of-research-team.png", "wb") as f:
                f.write(image_data)
            logging.info("Graph saved to ./assets/docs_output/workflow-of-research-team.png")
        except Exception as e:
            logging.info(f"Could not save graph: {str(e)}")

        logging.info(f"#### Start processing ####")
        start_time = time.time()
        graph_output = graph.invoke(
            {
                "messages": [
                    HumanMessage(content="First, get the UK's GDP over the past 5 years, then make a line chart of it. Once you make the chart, finish."),
                ],
            },
            {
                "recursion_limit": 10, # Maximum number of steps to take in the graph
            },
        )
        result = graph_output["messages"][-1].content
        logging.info(f"#### Finished processing in {time.time() - start_time:.2f} seconds : {result} ####")
        return result

    @staticmethod
    def _prompt_node(
        state: MessagesState,
        agent: CompiledGraph,
    ) -> dict:
        result = agent.invoke(state)
        return {"messages": result["messages"]}
    
    @staticmethod
    def _router(
        state: MessagesState,
        use_max_loops: bool = False,
        max_loops: int = 4,
    ) -> Literal["continue", "end"]:
        last_message = state["messages"][-1]

        if "FINAL ANSWER" in last_message.content:
            return "end"
        if use_max_loops and len(state["messages"]) > max_loops:
            return "end"

        return "continue"
