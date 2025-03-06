from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from modules.ai.agents.pandas_dataframe_agent.schemas.pandas_dataframe_agent_response_schema import PandasDataframeAgentResponseSchema

class PandasDataframeAgent:
    """
    This class is a LangChain implementation of Excel/CSV DataFrame agent.
    """

    def __init__(
        self,
        llm,
        dataframes,
        initial_messages: list = [
            SystemMessage(
                content="""You are an pandas dataframe agent that helps responding questions.
Format the response to JSON with the following structure:
{
    "row_index": <table_row_index>,
    "row_data": <all_row_data>,
    "result": <raw_result>,
}

Additional rules:
Only return the JSON.
No code-blocks or MARKDOWN are allowed in the response."""
            ),
        ],
        save_chat_history: bool = False,
        agent_type: AgentType = AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code: bool = True,
        verbose: bool = True,
    ):
        """
        Initialize the AI Agent.
        """
        self.llm = llm

        # The create_pandas_dataframe_agent is meant to let the LLM generate Python code to interact with the DataFrame.
        # This might be overkill if the task is straightforward, like a simple lookup. Also, allowing dangerous code could be a security concern if the CSV isn't trusted.
        self.agent_executor = create_pandas_dataframe_agent(
            self.llm,
            dataframes,
            agent_type=agent_type,
            allow_dangerous_code=allow_dangerous_code,
            verbose=verbose,
        )

        self.session_id = "PandasDataframeAgent-create_pandas_dataframe_agent"  # for History & Traceability purposes

        self.message_history = None
        if save_chat_history:
            self.message_history = ChatMessageHistory()
            if initial_messages:
                self.message_history.add_messages(initial_messages)

            self.agent_executor = RunnableWithMessageHistory(
                self.agent_executor,
                lambda session_id: self.message_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
        elif initial_messages:
            self.agent_executor = ChatPromptTemplate.from_messages(initial_messages) | self.agent_executor

    def invoke(
        self,
        question: str,
    ):
        """
        Execute the LangChain agent and return the response.
        """
        if not question:
            raise ValueError("Question must be provided.")

        if self.message_history:
            self.message_history.add_user_message(question)

        response = self.agent_executor.invoke(
            {"input": question},
            config={"configurable": {"session_id": self.session_id}},
        )

        if self.message_history:
            self.message_history.add_ai_message(response["output"])

        return response

    def invoke_returning_response_model(
        self,
        question: str,
    ) -> PandasDataframeAgentResponseSchema:
        """
        Execute the LangChain agent and return the PandasDataframeAgentResponse model response.
        """
        if not question:
            raise ValueError("Question must be provided.")

        response = self.invoke(question)
        raw_output = response["output"]

        try:
            output_parser = PydanticOutputParser(pydantic_object=PandasDataframeAgentResponseSchema)
            parsed_output = output_parser.parse(raw_output)
            return PandasDataframeAgentResponseSchema(
                row_index=parsed_output.row_index,
                row_data=parsed_output.row_data,
                result=parsed_output.result,
            )
        except Exception as e:
            return PandasDataframeAgentResponseSchema(error=f"Error decoding JSON response: {raw_output}")
