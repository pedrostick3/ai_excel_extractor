# Paths
INPUT_FOLDER = "./assets/docs_input"
OUTPUT_FOLDER = "./assets/docs_output"
VECTOR_DB_STORAGE = "./vector_databases_storage"
TEST_EXECUTION_EXAMPLE_FILE = "./assets/example_test_execution_main.py"
MAX_EXCEL_LINES_PER_AI_REQUEST = 5

# Free AI APIs: https://github.com/zukixa/cool-ai-stuff

# GitHub Configs
# Quick Start Guide: https://github.com/marketplace/models/azure-openai/o1-mini
# Limitações: https://docs.github.com/pt/github-models/prototyping-with-ai-models#rate-limits
GITHUB_BASE_URL = "https://models.inference.ai.azure.com"
GITHUB_KEY = "<your_key>"
GITHUB_MODEL = "gpt-4o-mini" # https://github.com/marketplace/models

# FresedGPT Configs
# Discord invite to config: https://discord.gg/JecEC5my4T
# Discord channel to config: https://discord.com/channels/1232622371249192970/1234913876693221426
# Quick Start Guide: https://fresed-api.gitbook.io/fresed-api/getting-started
FRESEDGPT_BASE_URL = "https://fresedgpt.space/v1"
FRESEDGPT_KEY = "<your_key>"
FRESEDGPT_MODEL = "gpt-4o-mini" # https://fresedgpt.space/v1/models

# Zukijourney Configs
# Discord invite to config: https://discord.com/invite/Y4J6XXnmQ6
# Discord channel to config: https://discord.com/channels/1090022628946886726/1305777445852545024
# Quick Start Guide: https://docs.zukijourney.com/ai
ZUKIJOURNEY_BASE_URL = "https://api.zukijourney.com/v1"
ZUKIJOURNEY_KEY = "<your_key>"
ZUKIJOURNEY_MODEL = "gpt-4o-mini" # https://proxy.blackgaypornis.fun/v1/models

# OpenAI Configs
OPENAI_API_KEY = "<your_key>"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small" # https://platform.openai.com/docs/models OR https://openai.com/api/pricing
OPENAI_FINE_TUNING_BASE_MODEL = "gpt-4o-mini-2024-07-18" # https://platform.openai.com/docs/models OR https://openai.com/api/pricing
OPENAI_FINE_TUNING_MODEL_17_01_2025 = "ft:gpt-4o-mini-2024-07-18:inspireit::AqjmD7gd" # Can be found in https://platform.openai.com/finetune/. It's the name of the model or you can check too in the 'Output model' propriety.
OPENAI_FINE_TUNING_MODEL_28_01_2025 = "ft:gpt-4o-mini-2024-07-18:inspireit::AuiodsIl" # Can be found in https://platform.openai.com/finetune/. It's the name of the model or you can check too in the 'Output model' propriety.
OPENAI_FINE_TUNING_MODEL_29_01_2025_WITH_VALIDATION_FILE = "ft:gpt-4o-mini-2024-07-18:inspireit::Av1GNDPM" # Can be found in https://platform.openai.com/finetune/. It's the name of the model or you can check too in the 'Output model' propriety.

# Azure OpenAI Configs
# [Fine-tuning models Regions](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models?tabs=global-standard%2Cstandard-chat-completions#fine-tuning-models)
# [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
# [Chat Quick Start Guide](https://learn.microsoft.com/pt-pt/azure/ai-services/openai/chatgpt-quickstart?tabs=command-line%2Ckeyless%2Cjavascript-keyless%2Ctypescript-keyless%2Cpython-new&pivots=programming-language-python#create-a-new-python-application)
AZURE_ENDPOINT = "https://<your_azure_openai_resource_name>.openai.azure.com" # Can be found in: Azure AI Foundry > Home > Azure OpenAI Endpoint (https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/fine-tuning?tabs=azure-openai%2Cturbo%2Cpython-new&pivots=programming-language-python#create-a-customized-model)
AZURE_API_KEY_1 = "<your_key>" # Can be found in: Azure AI Foundry > Home > API key 1 (https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/fine-tuning?tabs=azure-openai%2Cturbo%2Cpython-new&pivots=programming-language-python#create-a-customized-model)
AZURE_MODEL = "gpt-4o-mini" # Can be found in: Azure AI Foundry > Deployments > specific_model. It's the 'Name' propriety (not the 'Model Name' propriety). (https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/fine-tuning?tabs=azure-openai%2Cturbo%2Cpython-new&pivots=programming-language-python#create-a-customized-model)
AZURE_FINE_TUNING_MODEL = "gpt-4o-mini-2024-07-18-ft-5e5ff9cb38304ef8aceb079861af4050" # Can be found in: Azure AI Foundry > Deployments > specific_model. It's the 'Name' propriety (not the 'Model Name' propriety). (https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/fine-tuning?tabs=azure-openai%2Cturbo%2Cpython-new&pivots=programming-language-python#create-a-customized-model)
AZURE_API_VERSION = "2024-08-01-preview" # Can be found in: Azure AI Foundry > Deployments > specific_model > Endpoint > Target URI (https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning)

# Pinecone Configs
# [Pinecone WebPlatform](https://app.pinecone.io/organizations/-OJIcF7u7ahEIfzfe4eY/projects/00e9c860-0b66-4991-9904-5168ea966c8b/indexes)
# [Langchain Pinecone official docs](https://python.langchain.com/docs/integrations/vectorstores/pinecone/)
PINECONE_API_KEY = "<your_key>"
PINECONE_INDEX_NAME = "test-index"

# LangSmith Configs
LANGSMITH_TRACING=True
LANGSMITH_ENDPOINT="https://eu.api.smith.langchain.com"
LANGSMITH_API_KEY="<your-api-key>"
LANGSMITH_PROJECT_TEST_LANGSMITH="test-langsmith"
LANGSMITH_PROJECT_TEST_LANGGRAPH="test-langgraph"
LANGSMITH_PROJECT_TEST_LANGGRAPH_MULTI_AGENTS="test-langgraph-multi-agents"

# Anthropic Configs (Claude AI)
ANTHROPIC_ADMIN_KEY = "<your_key>"
ANTHROPIC_API_KEY = "<your_key>"

# Tavily Configs (Researcher AI Tool)
TAVILY_API_KEY = "<your_key>"
