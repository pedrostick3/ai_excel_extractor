from typing import Annotated, Sequence, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    This defines the object that is passed between each node in the graph.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
