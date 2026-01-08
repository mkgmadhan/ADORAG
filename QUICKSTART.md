# Quick Start Guide

## Local Development Setup

### 1. Prerequisites
- Python 3.10 or higher
- Git
- Azure subscription with:
  - Azure OpenAI Service
  - Azure AI Search
  - Azure DevOps account

### 2. Clone and Setup

```bash
# Navigate to project directory
cd c:\Dev\ADORag

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your credentials
notepad .env
```

**Required Configuration:**

```env
# Azure DevOps
ADO_ORGANIZATION=https://dev.azure.com/your-organization
ADO_PROJECT_NAME=YourProjectName
ADO_PAT=your-personal-access-token

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-admin-key
AZURE_SEARCH_INDEX_NAME=ado-workitems
```

### 4. Azure DevOps Personal Access Token (PAT)

1. Go to Azure DevOps → User Settings → Personal Access Tokens
2. Click "New Token"
3. Set scopes:
   - **Work Items**: Read
   - **Project and Team**: Read (optional)
4. Copy the token and add to `.env` file

### 5. Azure OpenAI Setup

1. Create Azure OpenAI resource in Azure portal
2. Deploy models:
   - **text-embedding-3-small** (for embeddings)
   - **gpt-4o-mini** (for chat)
3. Copy endpoint and key to `.env` file

### 6. Azure AI Search Setup

1. Create Azure AI Search service (Standard tier recommended)
2. Enable semantic search in Azure portal:
   - Go to your Search service
   - Navigate to "Semantic ranker"
   - Enable semantic search
3. Copy endpoint and admin key to `.env` file

### 7. Run the Application

```bash
# Ensure virtual environment is activated
streamlit run app.py
```

The application will:
1. Automatically create the search index if it doesn't exist
2. Perform an initial full sync of all work items
3. Open in your default browser at http://localhost:8501

### 8. Using the Application

#### First Launch
- Wait for initial sync to complete (progress shown in UI)
- This may take a few minutes depending on work item count

#### Asking Questions
- Type questions in the chat input
- Examples:
  - "What bugs are assigned to John?"
  - "Show me high priority features"
  - "Tell me about authentication issues"
  - "What's the status of sprint items?"

#### Syncing Updates
- **Delta Sync**: Click "🔄 Delta Sync" to fetch only changed items
- **Full Sync**: Click "🔃 Full Sync" to re-index all items

#### Viewing Work Items
- Click on work item links in responses to open in Azure DevOps
- Links format: #123 or Work Item #123

---

## Testing the Setup

### Test 1: Verify Configuration
```bash
python -c "from src.utils import load_config, validate_config; config = load_config(); validate_config(config); print('✓ Configuration valid')"
```

### Test 2: Test ADO Connection
```python
from src.ado_service import ADOConnector
from src.utils import load_config

config = load_config()
connector = ADOConnector(config['ado_organization'], config['ado_pat'])
result = connector.test_connection(config['ado_project_name'])
print(f'ADO Connection: {"✓ Success" if result else "✗ Failed"}')
```

### Test 3: Test OpenAI Connection
```python
from src.embedding_service import EmbeddingService
from src.utils import load_config

config = load_config()
service = EmbeddingService(
    config['openai_endpoint'],
    config['openai_api_key'],
    config['openai_api_version'],
    config['openai_embedding_deployment']
)
embedding = service.generate_embedding("test")
print(f'OpenAI Connection: ✓ Success (embedding dimension: {len(embedding)})')
```

---

## Troubleshooting

### Issue: "Module not found" errors
**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
pip install -r requirements.txt
```

### Issue: "Missing required environment variables"
**Solution**: Check `.env` file exists and contains all required variables
```bash
type .env  # Windows
cat .env   # Linux/Mac
```

### Issue: "ADO connection failed"
**Solution**: 
1. Verify PAT is valid and not expired
2. Check PAT has "Work Items: Read" permission
3. Verify organization URL format: `https://dev.azure.com/your-org`

### Issue: "Search index creation failed"
**Solution**:
1. Verify Azure Search key is admin key (not query key)
2. Check semantic search is enabled
3. Ensure Standard tier or higher

### Issue: "OpenAI deployment not found"
**Solution**:
1. Verify model deployments exist in Azure OpenAI Studio
2. Check deployment names match `.env` configuration
3. Ensure models are fully deployed (not creating)

### Issue: "Sync takes too long"
**Solution**:
1. First sync of large projects (1000+ items) can take 5-10 minutes
2. Check network connectivity
3. Monitor logs for progress
4. Consider syncing during off-hours

---

## Next Steps

1. **Customize**: Modify prompts in `src/rag_service.py` for specific use cases
2. **Deploy**: Follow [DEPLOYMENT.md](DEPLOYMENT.md) for Azure deployment
3. **Monitor**: Set up Azure Monitor for production deployments
4. **Scale**: Configure auto-scaling based on usage patterns

---

## Development Tips

### Running with Debug Logging
```bash
# Set log level in .env
LOG_LEVEL=DEBUG

# Run application
streamlit run app.py
```

### Clearing Index and Re-syncing
```python
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential

# Delete index
endpoint = "your-search-endpoint"
key = "your-search-key"
index_name = "ado-workitems"

client = SearchIndexClient(endpoint, AzureKeyCredential(key))
client.delete_index(index_name)
print("Index deleted. Restart app to recreate and sync.")
```

### Viewing Raw Work Item Data
```python
from src.ado_service import ADOConnector
from src.utils import load_config
import json

config = load_config()
connector = ADOConnector(config['ado_organization'], config['ado_pat'])
items = connector.fetch_work_items(config['ado_project_name'])
print(json.dumps(items[0], indent=2))  # View first item
```

---

## Support and Feedback

For issues, questions, or feedback:
- Open an issue in the repository
- Review logs in the application
- Check Azure service health status
