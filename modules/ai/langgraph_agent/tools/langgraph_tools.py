from constants import configs
from typing import Annotated
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.tavily_search.tool import TavilySearchAPIWrapper

class LangGraphTools:
    BASE_SYSTEM_MESSAGE: str = """You are a helpful AI assistant, collaborating with other assistants.
Use the provided tools to progress towards answering the question.
If you are unable to fully answer, that's OK, another assistant with different tools will help where you left off. Execute what you can to make progress.
If you or any of the other assistants have the final answer or deliverable, prefix your response with FINAL ANSWER so the team knows to stop.

{system_message}"""

    tavily_tool = TavilySearchResults(
        api_wrapper = TavilySearchAPIWrapper(tavily_api_key=configs.TAVILY_API_KEY),
        max_results = 5,
    )

    @tool
    @staticmethod
    def python_repl_tool(code: Annotated[str, "The python code to execute to generate your chart and save it as './assets/docs_output/chart.png'."]) -> str:
        """
        Use this to execute pyhton code.
        If you want to see the output of a value, you should print it out with `print(...)`. This is visible to the user.
        """
        try:
            result = PythonREPL().run(code)
        except BaseException as e:
            return f"Failed to execute. Error: {repr(e)}"
        result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
        return f"{result_str}\n\nIf you have completed all tasks, respond with FINAL ANSWER."
