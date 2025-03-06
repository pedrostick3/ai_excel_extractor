from typing import Optional, Any
from pydantic import BaseModel

class PandasDataframeAgentResponseSchema(BaseModel):
    row_index: Optional[int] = None
    row_data: Optional[dict] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    def __str__(self):
        return self.model_dump_json(indent=2)
