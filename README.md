# ADO RAG - AI-Powered Azure DevOps Work Item Search

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-red)
![Azure](https://img.shields.io/badge/Azure-OpenAI-orange)
![License](https://img.shields.io/badge/License-MIT-green)

An intelligent chat application that enables natural language search and Q&A over Azure DevOps work items using RAG (Retrieval-Augmented Generation) powered by Azure OpenAI and Azure AI Search.

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Deployment](#-deployment) • [Documentation](#-documentation)

</div>

---

## 🚀 Features

### Core Capabilities
- 💬 **Conversational AI Interface**: Natural language chat powered by Azure OpenAI GPT-4o-mini
- 🔍 **Hybrid Search**: Vector + keyword search with semantic ranking for accurate results
- 🎯 **Smart Filtering**: Query by work item type, state, priority, severity, and more
- 📊 **Rich Work Item Support**: Handles User Stories, Bugs, Tasks, Features, Epics
- 🔗 **Direct Integration**: Real-time sync with Azure DevOps REST API

### Advanced Features
- ⚡ **Delta Sync**: Intelligent incremental sync fetches only modified work items
- 🐛 **Bug Triage**: AI-powered duplicate detection and requirement matching
- 📈 **Progress Tracking**: Real-time sync progress with detailed stage indicators
- 🎨 **Rich Fields**: Acceptance Criteria, Repro Steps, Priority, Severity, Tags
- 🗑️ **Deletion Detection**: Automatically removes deleted work items from index
- 💰 **Cost-Optimized**: Uses efficient models (text-embedding-3-small, GPT-4o-mini)

### User Experience
- 📱 **Responsive UI**: Clean Streamlit interface with emoji reactions
- 🔢 **Accurate Counts**: Real-time work item statistics and filtering
- 🔄 **Smart Caching**: Efficient data retrieval with connection pooling
- 📝 **Source Attribution**: Clickable links to original work items in Azure DevOps

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI                             │
│                    (Chat Interface + Sidebar)                   │
└───────┬─────────────────────────────────────────────┬───────────┘
        │                                             │
        ├─────────── Query Flow ─────────────────────┤
        │                                             │
        ▼                                             ▼
┌───────────────────┐                        ┌───────────────────┐
│   RAG Service     │                        │   Sync Service    │
│  - Query parsing  │                        │  - Full sync      │
│  - Context build  │                        │  - Delta sync     │
│  - LLM streaming  │                        │  - Deletions      │
│  - Bug triage     │                        │  - Progress       │
└─────────┬─────────┘                        └─────────┬─────────┘
          │                                            │
          ├──────────────┬─────────────────────────────┤
          │              │                             │
          ▼              ▼                             ▼
┌──────────────┐  ┌──────────────┐         ┌──────────────────┐
│   Embedding  │  │    Azure     │         │   Azure DevOps   │
│   Service    │  │  AI Search   │         │       API        │
│              │  │              │         │                  │
│  - Generate  │  │  - Hybrid    │         │  - WIQL queries  │
│    vectors   │  │    search    │         │  - Work items    │
│  - Batch     │  │  - Vector    │         │  - Metadata      │
│    process   │  │    store     │         │  - Updates       │
└──────┬───────┘  └──────────────┘         └──────────────────┘
       │
       ▼
┌──────────────────┐
│  Azure OpenAI    │
│  - Embeddings    │
│  - Chat (GPT)    │
└──────────────────┘
```

### Key Components

- **RAG Service**: Query processing, context building, LLM streaming, bug triage
- **Sync Service**: Full/delta sync orchestration, deletion detection, progress tracking
- **Search Service**: Azure AI Search operations, hybrid search, document management
- **Embedding Service**: Vector generation, batch processing, caching
- **ADO Service**: Azure DevOps API integration, WIQL queries, work item retrieval

## ⚡ Quick Start

### Prerequisites

- **Python**: 3.10 or higher
- **Azure Subscription** with:
  - Azure OpenAI Service (text-embedding-3-small and GPT-4o-mini deployments)
  - Azure AI Search (Standard tier with semantic search enabled)
- **Azure DevOps**: Organization and project with Personal Access Token (PAT)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mkgmadhan/ADORAG.git
   cd ADORAG
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Azure DevOps Configuration
   ADO_ORGANIZATION=your-org-name
   ADO_PROJECT_NAME=your-project-name
   ADO_PAT=your-personal-access-token
   
   # Azure OpenAI Configuration
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your-openai-key
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
   AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
   AZURE_OPENAI_API_VERSION=2024-08-01-preview
   
   # Azure AI Search Configuration
   AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
   AZURE_SEARCH_KEY=your-search-admin-key
   AZURE_SEARCH_INDEX_NAME=adorag-workitems
   ```

5. **Test configuration (optional)**
   ```bash
   python test_config.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **First-time setup**
   - The app will automatically perform a full sync on first launch
   - Wait for sync to complete (progress shown in sidebar)
   - Start asking questions about your work items!

## 📖 Usage

### Chat Interface

**Sample queries:**
- "Show me all high priority bugs"
- "What user stories are in progress?"
- "Summarize bug #2432"
- "Count all features by state"
- "Show P1 bugs in Resolved state"
- "triage 2432" (Find similar bugs and related requirements)

### Bug Triage

The bug triage feature helps identify potential duplicates and related requirements:

```
User: triage 2432
```

**Returns:**
1. **Similar Bugs**: Semantically similar bugs that might be duplicates
2. **Related Requirements**: User stories that might be affected by the bug
3. **Triage Recommendations**: AI-generated analysis and suggestions

### Syncing Data

- **Full Sync**: Click "Sync" button when first setting up or after major changes
- **Delta Sync**: Regular syncs only fetch work items modified since last sync
- **Progress**: 8-stage progress indicator shows sync status in real-time
- **Deletion Detection**: Automatically identifies and removes deleted work items

### Filtering

**Natural language filters:**
- By type: "show bugs", "list user stories"
- By state: "active bugs", "resolved items"
- By priority: "P1 bugs", "high priority features"
- By severity: "critical bugs", "sev 1 items"
- Combinations: "show active P1 bugs in resolved state"

## 📁 Project Structure

```
ADORag/
├── app.py                          # Streamlit UI entry point
├── src/
│   ├── __init__.py
│   ├── ado_service.py             # Azure DevOps API integration (358 lines)
│   ├── search_service.py          # Azure AI Search operations (499 lines)
│   ├── embedding_service.py       # Embedding generation & batching (127 lines)
│   ├── rag_service.py             # RAG query processing (726 lines)
│   ├── sync_service.py            # Sync orchestration (213 lines)
│   └── utils.py                   # Configuration & utilities (96 lines)
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create from template)
├── .gitignore                     # Git ignore rules
├── .dockerignore                  # Docker ignore rules
├── Dockerfile                     # Container image definition
├── setup.ps1                      # Windows setup script
├── setup.sh                       # Linux/Mac setup script
├── test_config.py                 # Configuration validation
├── cleanup_deleted_items.py       # Standalone deletion cleanup utility
└── README.md                      # This file
```

## 🔧 Configuration

### Azure DevOps PAT Permissions

Your Personal Access Token needs:
- ✅ **Work Items**: Read
- ✅ **Project and Team**: Read

### Azure OpenAI Models

Deploy these models in your Azure OpenAI resource:
- **text-embedding-3-small**: 1536 dimensions, ~$0.02 per 1M tokens
- **gpt-4o-mini**: Chat completions, ~$0.15 per 1M input tokens

### Azure AI Search Index

The application automatically creates the search index on first sync:
- **Vector Configuration**: HNSW algorithm, 1536 dimensions
- **Fields**: work_item_id, title, description, content, type, state, priority, severity, tags, etc.
- **Search Features**: Hybrid (vector + keyword), semantic ranking, filtering

### Sync Behavior

- **First Launch**: Full sync of all work items
- **Subsequent Syncs**: Delta sync (only modified items)
- **Same-Day Filtering**: Python-level filtering for items modified today
- **Deletion Detection**: Compares ADO and index to identify removed items
- **Progress Tracking**: 8 stages - Initialize, Fetch, Process, Delete, Embed, Upload, Index, Finalize

## 🐳 Deployment

### Docker

1. **Build image**
   ```bash
   docker build -t adorag:latest .
   ```

2. **Run container**
   ```bash
   docker run -p 8501:8501 --env-file .env adorag:latest
   ```

### Azure Container Apps

1. **Create Azure Container Registry**
   ```bash
   az acr create --resource-group <rg> --name <acr-name> --sku Standard
   ```

2. **Build and push image**
   ```bash
   az acr login --name <acr-name>
   docker build -t adorag:latest .
   docker tag adorag:latest <acr-name>.azurecr.io/adorag:latest
   docker push <acr-name>.azurecr.io/adorag:latest
   ```

3. **Create Container Apps environment**
   ```bash
   az containerapp env create \
     --name adorag-env \
     --resource-group <rg> \
     --location eastus
   ```

4. **Deploy application**
   ```bash
   az containerapp create \
     --name adorag \
     --resource-group <rg> \
     --environment adorag-env \
     --image <acr-name>.azurecr.io/adorag:latest \
     --target-port 8501 \
     --ingress external \
     --registry-server <acr-name>.azurecr.io \
     --env-vars \
       ADO_ORGANIZATION=<org> \
       ADO_PROJECT_NAME=<project> \
       ADO_PAT=secretref:ado-pat \
       AZURE_OPENAI_ENDPOINT=<endpoint> \
       AZURE_OPENAI_KEY=secretref:openai-key \
       AZURE_SEARCH_ENDPOINT=<endpoint> \
       AZURE_SEARCH_KEY=secretref:search-key \
       # ... other env vars
   ```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 💰 Cost Optimization

### Token Usage
- **Embeddings**: text-embedding-3-small (~$0.02 per 1M tokens)
- **Chat**: GPT-4o-mini (~$0.15 per 1M input, ~$0.60 per 1M output)
- **Typical Costs**: 1000 work items = ~$0.30 embeddings + chat usage

### Search Costs
- **Azure AI Search**: Standard S1 tier (~$250/month)
- **Storage**: Minimal cost for work item metadata

### Optimization Features
- **Delta Sync**: Only process changed items (reduces API calls and embeddings)
- **Batch Processing**: Efficient embedding generation (100 items/batch)
- **Caching**: Connection pooling and metadata caching
- **Efficient Models**: Smallest viable models for cost savings

**Estimated monthly cost for 5,000 work items**: ~$260-280 (mostly search tier)

## 🔍 Troubleshooting

### Sync Issues

**Problem**: Sync fails or shows incorrect counts
- ✅ Verify `ADO_PAT` has correct permissions (Work Items: Read)
- ✅ Check `ADO_ORGANIZATION` and `ADO_PROJECT_NAME` are correct
- ✅ Review Streamlit logs for API errors
- ✅ Run `python test_config.py` to validate configuration

### Search Issues

**Problem**: Search returns no results or poor matches
- ✅ Ensure Azure AI Search index exists (check Azure Portal)
- ✅ Verify `AZURE_SEARCH_KEY` has admin permissions
- ✅ Confirm semantic search is enabled (Premium tier required)
- ✅ Check work items are actually synced (`check_index_status.py`)

### OpenAI Issues

**Problem**: Embedding or chat errors
- ✅ Confirm model deployments exist in Azure OpenAI resource
- ✅ Verify `AZURE_OPENAI_KEY` is valid
- ✅ Check deployment names match environment variables
- ✅ Monitor rate limits and quotas in Azure Portal

### Bug Triage Issues

**Problem**: Triage returns unrelated bugs
- The system uses pure semantic similarity (vector-only search)
- Results depend on bug content quality and detail
- Ensure bugs have detailed descriptions and proper tags

### Common Errors

**Error**: `fatal: not a git repository`
- Run `git init` in project root

**Error**: `ModuleNotFoundError: No module named 'azure'`
- Activate virtual environment and run `pip install -r requirements.txt`

**Error**: `Index not found`
- Run a full sync to create the index

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Step-by-step getting started guide
- [GETTING_STARTED.md](GETTING_STARTED.md) - Detailed setup instructions
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture and design
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guides for various platforms
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview and features

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- Search by [Azure AI Search](https://azure.microsoft.com/en-us/products/ai-services/ai-search)
- Integrated with [Azure DevOps](https://azure.microsoft.com/en-us/products/devops)

## 📧 Support

For issues, questions, or feature requests:
- Open an issue in this repository
- Contact: [GitHub Issues](https://github.com/mkgmadhan/ADORAG/issues)

---

<div align="center">

**Made with ❤️ for Azure DevOps teams**

</div>
