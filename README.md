# LangChain, LangFlow and LangSmith PoCs

A collection of Proof-of-Concepts demonstrating integrations with LangChain, LangFlow, and LangSmith.

## 🚀 Quick Start

### Prerequisites
- Python 3.11.8 (`python --version` to verify the actual version and `py -0p` to [check your installed versions](https://stackoverflow.com/a/70233933/16451258))

### Virtual Environment Setup
```bash
# Create virtual environment
python -m venv .venv        # Windows/Linux
python3.9 -m venv .venv     # Specific Python version

# Activate environment
source .venv/Scripts/activate  # Bash (Windows/Linux)
.venv/Scripts/activate         # CMD/PowerShell
```

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
python3.9 -m pip install -r requirements.txt        # Specific Python version
.venv/Scripts/python.exe -m pip install -r requirements.txt  # Direct path

# Install LangFlow (requires uv)
pip install uv
uv pip install langflow
```

## ⚙️ LangFlow Management
```bash
# Run LangFlow
uv run langflow run
.venv/Scripts/python.exe -m uv run langflow run  # Direct path

# Update LangFlow
uv pip install Langflow -U
.venv/Scripts/python.exe -m uv pip install Langflow -U
```

## 🖥️ Running the Application
```bash
python main.py               # Standard
python3.9 main.py            # Specific Python version
.venv/Scripts/python.exe main.py  # Direct path
```

## 🤖 Fine-Tuning Models

### Create Fine-Tuning Model
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

### Delete Fine-Tuning Model
```python
ExcelGenericFinetuningAgent(
    ai_service=OpenAiAiService(),
    base_model=FINETUNING_BASE_MODEL,
    fine_tuning_model=FINETUNING_MODEL,
    delete_fine_tuning_model=True,
    delete_fine_tuning_model_safety_trigger=True,
)
```

### Use Fine-Tuning Model
```python
fine_tuning_agent = ExcelGenericFinetuningAgent(
    ai_service=OpenAiAiService(),
    base_model=FINETUNING_BASE_MODEL,
    fine_tuning_model=FINETUNING_MODEL,
)
```

## 🔍 Model Management
```python
# List available OpenAI models
import openai
openai.api_key = "OPENAI_API_KEY"
print(f"Available Models: {openai.models.list()}")
```

## 🛠️ Troubleshooting

### Permission Error Fix
```bash
rm C:/Users/pedrostick/AppData/Local/langflow/langflow/Cache/secret_key
uv run langflow run
```
**Note:** This will reset your LangFlow Global Variables.

## 📊 Models & Prompts

### Tested Models
- **`o1-mini`**
- **`text-embedding-3-small`** (Embeddings)
- **`gpt-4o-mini`** (Primary - best cost/quality balance)

### Agent Prompts
- **PoC4 Prompts**: `modules/poc4/poc4_prompts.py`
- **PoC_RAG Prompts**: `modules/poc_rag_email_gen_agent/poc_rag_email_gen_agent_prompts.py`

## 🗂️ Project Structure

### Core Modules
- **`ai`**: AI integrations and services
  - Agents: `PandasDataframeAgent`, `VectordbEmbeddingsAgent`
  - LangChain Agents: `LangChainAgent`
  - LangGraph Agents: `LangGraphAgentWithWeatherTool`, `LangGraphMultiAgents`
  - LangFlow: `PoC_RAG_LangFlow_project`, `PoC4_LangFlow_project` and its components
  - LangSmith: `LangSmithService`
- **`excel`**: Excel processing
  - Service: `ExcelService`
- **`logger`**: Logging infrastructure
  - Service: `LoggerService`

### Integration Module
- **`uipath_incorporation`**: UiPath integration project

## 🔗 Resources
- Dependencies: `requirements.txt`
- LangFlow documentation: [https://docs.langflow.org](https://docs.langflow.org)
- How to integrate python scripts in UiPath: [YouTube Video](https://youtu.be/Zar8wrhT0Dk?si=cCyvklLRAEGq7eOU)
