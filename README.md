Crate .venv folder for virtual environment:

```bash
python -m venv .venv
```
OR
```bash
python3.9 -m venv .venv
```

Activate virtual environment:

```bash
source .venv/Scripts/activate
```
OR
```bash
.venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```
OR
```bash
python3.9 -m pip install -r requirements.txt
```
OR
```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

[Install LangFlow](https://docs.langflow.org/get-started-installation) with uv (first install uv: `pip install uv`):

```bash
uv pip install langflow
```
OR
```bash
.venv/Scripts/python.exe -m uv pip install langflow
```

Run LangFlow locally:

```bash	
uv run langflow run
```
OR
```bash
.venv/Scripts/python.exe -m uv run langflow run
```

Update LangFlow locally:

```bash	
uv pip install Langflow -U
```
OR
```bash
.venv/Scripts/python.exe -m uv pip install Langflow -U
```

Run the application on F5 (run button) or:

```bash
python main.py
```
OR
```bash
python3.9 main.py
```
OR
```bash
.venv/Scripts/python.exe main.py
```

Check available OpenAI models:
```python
import openai
openai.api_key = "OPENAI_API_KEY"

models=openai.models.list()
print(f"Available Models: {models}")
```

Create a fine-tuning model via API:
```python
from modules.ai.services.openai_ai_service import OpenAiAiService
from modules.ai.fine_tuning_agents.excel_generic_agent.excel_generic_fine_tuning_agent import ExcelGenericFinetuningAgent

ExcelGenericFinetuningAgent(
    ai_service=OpenAiAiService(),
    base_model=FINETUNING_BASE_MODEL,
    create_fine_tuning_model=True,
    force_rewrite_training_file=True,
)
```

Delete a fine-tuning model via API:
```python
from modules.ai.services.openai_ai_service import OpenAiAiService
from modules.ai.fine_tuning_agents.excel_generic_agent.excel_generic_fine_tuning_agent import ExcelGenericFinetuningAgent

ExcelGenericFinetuningAgent(
    ai_service=OpenAiAiService(),
    base_model=FINETUNING_BASE_MODEL,
    fine_tuning_model=FINETUNING_MODEL,
    delete_fine_tuning_model=True,
    delete_fine_tuning_model_safety_trigger=True,
)
```

Use a fine-tuning model via API:
```python
from modules.ai.services.openai_ai_service import OpenAiAiService
from modules.ai.fine_tuning_agents.excel_generic_agent.excel_generic_fine_tuning_agent import ExcelGenericFinetuningAgent

fine_tuning_agent = ExcelGenericFinetuningAgent(
    ai_service=OpenAiAiService(),
    base_model=FINETUNING_BASE_MODEL,
    fine_tuning_model=FINETUNING_MODEL,
)
```

If you encounter the following error when running the LangFlow application:
```bash
PermissionError: [Errno 13] Permission denied: 'C:\\Users\\pedrostick\\AppData\\Local\\langflow\\langflow\\Cache\\secret_key'
```

you can resolve it by running the following commands in your terminal:
```bash
rm C:/Users/pedrostick/AppData/Local/langflow/langflow/Cache/secret_key
uv run langflow run
```

don't forget to set your Global Variables again since this method cleans them up.

### Tested Models:
- **o1-mini**
- **text-embedding-3-small (for embeddings)**
- **gpt-4o-mini (most used since it's the best option for this PoC comparing cost & quality)**

### Agent Prompts:
- **PoC4**: modules/poc4/poc4_prompts.py

### AI Agents, Services & Utils:
- **PandasDataframeAgent**: modules/ai/agents/pandas_dataframe_agent/pandas_dataframe_agent.py
- **VectordbEmbeddingsAgent**: modules/ai/agents/vectordb_embeddings_agent/vectordb_embeddings_agent.py
- **OpenAiAiService**: modules/ai/services/openai_ai_service.py
- **TokenUtils**: modules/ai/utils/token_utils.py

### Excel Services:
- **ExcelService**: modules/excel/services/excel_service.py

### Logger Services:
- **LoggerService**: modules/logger/services/logger_service.py

### Python Project Modules:
- **ai**: Module responsible for handling everything related to AI;
- **excel**: Module responsible for processing excel files;
- **logger**: Module responsible for logging;
- **uipath_incorporation**: Independent module developed to test the [incorporation](https://youtu.be/Zar8wrhT0Dk?si=cCyvklLRAEGq7eOU) of the python project into UiPath Activities;

### Python version used:
- **Python 3.9.13** - you can check it by running `python --version` in your terminal