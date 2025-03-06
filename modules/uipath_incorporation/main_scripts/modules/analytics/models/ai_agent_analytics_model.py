from modules.analytics.utils.analytics_utils import AnalyticsUtils

class AiAgentAnalyticsModel(object):
    name: str
    ai_model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    execution_time_in_seconds: float
    extra_info: str
    
    def __init__(
        self,
        name: str,
        ai_model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        execution_time_in_seconds: float,
        extra_info: str = None,
    ):
        """
        Initializes the AI Agent Analytics Model.
        """
        self.name = name
        self.ai_model = ai_model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.execution_time_in_seconds = execution_time_in_seconds
        self.extra_info = extra_info

    def __str__(self):
        to_return = f"{self.name} - ai_model={self.ai_model} CompletionUsage(prompt_tokens={self.prompt_tokens}, completion_tokens={self.completion_tokens}, total_tokens={self.total_tokens})"
        
        formatted_time = AnalyticsUtils.format_time_from_seconds(self.execution_time_in_seconds)
        to_return += f" - Demorou {formatted_time}."

        if self.extra_info:
            to_return += f" extra_info = {self.extra_info}"
            
        return to_return

    