class AnalyticsUtils:
    @staticmethod
    def format_time_from_seconds(time_in_seconds: float) -> str:
        hours = int(time_in_seconds // 3600)
        minutes = int((time_in_seconds % 3600) // 60)
        seconds = time_in_seconds % 60

        if hours > 0:
            formatted_time = f"{hours:02d}h{minutes:02d}m{seconds:05.3f}s"
        elif minutes > 0:
            formatted_time = f"{minutes:02d}m{seconds:05.3f}s"
        else:
            formatted_time = f"{seconds:05.3f}s"

        return formatted_time
