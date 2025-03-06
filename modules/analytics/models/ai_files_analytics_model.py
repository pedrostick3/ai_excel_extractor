from modules.analytics.models.ai_agent_analytics_model import AiAgentAnalyticsModel
from modules.analytics.utils.analytics_utils import AnalyticsUtils

class AiFilesAnalyticsModel(object):
    agent_requests_per_file: dict[str, list[AiAgentAnalyticsModel]]

    def __init__(
        self,
        agent_requests_per_file: dict[str, list[AiAgentAnalyticsModel]] = {},
    ):
        """
        Initializes the AI Files Analytics Model.
        """
        self.agent_requests_per_file = agent_requests_per_file

    def __str__(self):
        to_return = ""
        for key, value in self.agent_requests_per_file.items():
            total_execution_time = 0
            for agent_request in value:
                total_execution_time += agent_request.execution_time_in_seconds
            formatted_time = AnalyticsUtils.format_time_from_seconds(total_execution_time)
            
            to_return += f"##### {key} - Demorou {formatted_time}.\n"
            for agent_request in value:
                to_return += f"\t{agent_request}\n"

        return to_return
    
    def add_agent_request(
        self,
        file_name: str,
        agent_request: AiAgentAnalyticsModel,
    ):
        """
        Adds an AI Agent Analytics Model to the list of agent requests.
        """
        if file_name not in self.agent_requests_per_file:
            self.agent_requests_per_file[file_name] = []
        self.agent_requests_per_file[file_name].append(agent_request)
        
    
