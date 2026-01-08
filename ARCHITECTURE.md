# ADO RAG Architecture

## Overview

ADO RAG is a production-ready AI-powered search system that enables intelligent querying of Azure DevOps work items using Retrieval-Augmented Generation (RAG) architecture. The system is built with maintainability, scalability, and cost-efficiency as core design principles.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Streamlit Chat Application (app.py)              │  │
│  │  - Chat interface with message history                        │  │
│  │  - Project information display                                │  │
│  │  - Sync controls (Delta/Full)                                 │  │
│  │  - Auto-trigger initial sync                                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   Sync Service       │  │   RAG Service        │  │  Embedding Service   │
│  (sync_service.py)   │  │  (rag_service.py)    │  │ (embedding_service.py)│
│                      │  │                      │  │                      │
│ - Orchestrates sync  │  │ - Query processing   │  │ - Generate embeddings│
│ - Delta sync logic   │  │ - Context building   │  │ - Batch processing   │
│ - Metadata tracking  │  │ - Response streaming │  │ - Text truncation    │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
           │                        │                          │
           │                        │                          │
           ▼                        ▼                          │
┌──────────────────────┐  ┌──────────────────────┐           │
│   ADO Service        │  │  Search Service      │           │
│  (ado_service.py)    │  │ (search_service.py)  │◄──────────┘
│                      │  │                      │
│ - Fetch work items   │  │ - Index management   │
│ - Delta queries      │  │ - Vector search      │
│ - HTML cleaning      │  │ - Hybrid search      │
│ - Metadata extract   │  │ - Semantic ranking   │
└──────────────────────┘  └──────────────────────┘
           │                        │
           │                        │
           ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Azure Services Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  Azure DevOps   │  │  Azure OpenAI   │  │ Azure AI Search │    │
│  │                 │  │                 │  │                 │    │
│  │ - Work Items    │  │ - Embeddings    │  │ - Vector Store  │    │
│  │ - API           │  │ - Chat (GPT-4)  │  │ - Semantic      │    │
│  │ - PAT Auth      │  │ - Streaming     │  │ - Hybrid Search │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

#### Streamlit Application (`app.py`)
- **Purpose**: Provides web-based chat interface
- **Key Features**:
  - Real-time streaming responses
  - Session-based chat history
  - Auto-trigger initial sync on startup
  - Manual sync controls (Delta/Full)
  - Project status display
- **State Management**: Uses `st.session_state` for chat history and sync status
- **Caching**: `@st.cache_resource` for service initialization

### 2. Service Layer

#### Sync Service (`src/sync_service.py`)
- **Purpose**: Orchestrates synchronization workflow
- **Responsibilities**:
  - Coordinate between ADO and Search services
  - Manage delta vs. full sync logic
  - Track sync metadata (timestamp, count)
  - Batch processing for efficiency
- **Key Methods**:
  - `sync()`: Main sync operation
  - `get_sync_status()`: Retrieve sync metadata
  - `test_connections()`: Validate all service connections

#### RAG Service (`src/rag_service.py`)
- **Purpose**: Query processing and response generation
- **Responsibilities**:
  - Generate query embeddings
  - Retrieve relevant work items
  - Build context for LLM
  - Stream responses with citations
- **Key Features**:
  - Hybrid search (vector + keyword)
  - Semantic ranking
  - Work item reference extraction
  - Markdown formatting with links
- **Prompt Engineering**: System prompt optimized for accuracy and source attribution

#### Embedding Service (`src/embedding_service.py`)
- **Purpose**: Generate embeddings for text
- **Responsibilities**:
  - Single and batch embedding generation
  - Token counting and truncation
  - Error handling with fallback
- **Optimization**:
  - Batch API calls (16 texts per request)
  - Text truncation to 8191 tokens
  - Zero-vector fallback for errors

#### ADO Service (`src/ado_service.py`)
- **Purpose**: Interface with Azure DevOps API
- **Responsibilities**:
  - Authenticate with PAT
  - Fetch work items with WIQL queries
  - Extract and clean metadata
  - Handle HTML content
- **Key Features**:
  - Delta sync using `ChangedDate` filter
  - Pagination support
  - HTML stripping with BeautifulSoup
  - Comprehensive metadata extraction

#### Search Service (`src/search_service.py`)
- **Purpose**: Manage Azure AI Search operations
- **Responsibilities**:
  - Index creation and management
  - Document upsert operations
  - Vector and hybrid search
  - Metadata storage
- **Index Schema**:
  - Vector field (1536 dimensions)
  - Metadata fields (work item info)
  - Semantic search configuration
  - HNSW algorithm for vector search

### 3. Data Flow

#### Sync Flow
```
1. User triggers sync (or auto-trigger on startup)
2. Sync Service retrieves last sync timestamp
3. ADO Service fetches work items (delta query)
4. Embedding Service generates embeddings (batch)
5. Search Service upserts documents to index
6. Sync Service updates metadata
7. UI displays sync status
```

#### Query Flow
```
1. User enters question in chat
2. RAG Service generates query embedding
3. Search Service performs hybrid search
4. Top-K relevant work items retrieved
5. RAG Service builds context with work items
6. Azure OpenAI generates streaming response
7. UI displays response with work item links
```

## Design Decisions

### 1. Streamlit vs. React
**Decision**: Streamlit
**Rationale**:
- Rapid development and prototyping
- Built-in state management
- Python-native (consistency with backend)
- Easy deployment
- Trade-off: Less control over UI customization

### 2. Azure AI Search vs. Alternatives
**Decision**: Azure AI Search
**Rationale**:
- Integrated with Azure ecosystem
- Hybrid search (vector + keyword)
- Semantic ranking built-in
- Managed service (no infrastructure)
- Cost-effective for moderate scale
**Alternatives Considered**:
- PostgreSQL + pgvector (more cost-effective, self-managed)
- Pinecone (specialized, higher cost)
- Azure Cosmos DB (global scale, overkill for single project)

### 3. Delta Sync Strategy
**Decision**: ChangedDate-based delta sync with metadata tracking
**Rationale**:
- Efficient: Only process changed items
- Scalable: Handles growing work item counts
- Simple: No complex change tracking
- Reliable: Timestamp-based
**Trade-offs**: Doesn't detect deletions automatically

### 4. Embedding Model
**Decision**: text-embedding-3-small
**Rationale**:
- Cost-efficient (~$0.02 per 1M tokens)
- Good quality (1536 dimensions)
- Fast inference
- Microsoft-recommended

### 5. Chat Model
**Decision**: GPT-4o-mini
**Rationale**:
- Cost-efficient (~$0.15 per 1M input tokens)
- Fast responses
- Good quality for Q&A tasks
- Supports streaming
**When to use GPT-4**: Complex reasoning, multi-turn conversations

### 6. Project Isolation
**Decision**: Single project per deployment with backend configuration
**Rationale**:
- Simplified security (one PAT per deployment)
- Clear ownership and access control
- Easier troubleshooting
- Cost tracking per project
**Multi-project**: Use shared index with project_id filtering

## Scalability Considerations

### Current Scale (Up to 10,000 work items)
- Single Azure AI Search index
- Standard tier (~$250/month)
- Single Container App instance
- Batch size: 50 work items

### Medium Scale (10,000-100,000 work items)
- Increase batch sizes
- Enable horizontal scaling (2-5 replicas)
- Consider caching layer (Redis)
- Monitor token usage

### Large Scale (100,000+ work items)
- Partition index by project/team
- Implement incremental indexing
- Add rate limiting
- Consider dedicated OpenAI deployment

## Security Architecture

### Authentication & Authorization
- **ADO**: Personal Access Token (PAT) with Read scope
- **Azure OpenAI**: API Key or Managed Identity
- **Azure Search**: Admin Key or Managed Identity

### Best Practices
1. Store PATs in environment variables (not code)
2. Use Azure Key Vault for production
3. Enable Managed Identity where possible
4. Rotate PATs every 90 days
5. Implement RBAC for Azure resources
6. Use HTTPS only
7. Enable audit logging

### Network Security
- VNet integration for private access
- Private endpoints for Azure services
- NSG rules for traffic filtering
- Azure Front Door for WAF

## Cost Analysis

### Monthly Cost Estimate (10,000 work items)

| Service | Tier | Cost | Notes |
|---------|------|------|-------|
| Azure AI Search | Standard | $250 | Includes semantic search |
| Azure OpenAI (Embeddings) | text-embedding-3-small | $10 | ~500K tokens/sync |
| Azure OpenAI (Chat) | GPT-4o-mini | $20 | ~100 queries/day |
| Azure Container Apps | Consumption | $15 | 1 vCPU, 2GB RAM |
| **Total** | | **~$295/month** | |

### Cost Optimization
1. Use delta sync (reduce embedding costs)
2. Cache frequent queries
3. Implement query deduplication
4. Schedule syncs during off-hours
5. Use GPT-4o-mini instead of GPT-4
6. Monitor and set quota limits

## Maintenance & Operations

### Monitoring
- Application Insights for telemetry
- Custom metrics for sync operations
- Error rate alerts
- Token usage tracking
- Response time monitoring

### Backup & Recovery
- Azure AI Search: Built-in redundancy
- Configuration: Version-controlled in Git
- No application state to backup (session-only)

### Updates & Upgrades
- Zero-downtime deployments with Container Apps
- Blue-green deployment strategy
- Automated CI/CD pipeline
- Semantic versioning

## Future Enhancements

### Phase 2
- Multi-project support with project selector
- Advanced filtering (by assignee, date, state)
- Export conversation history
- Feedback mechanism for responses

### Phase 3
- Conversation history persistence (Cosmos DB)
- Azure AD B2C authentication
- Advanced analytics dashboard
- Webhook-based real-time sync

### Phase 4
- Multi-tenant support
- Custom embeddings fine-tuning
- Integration with Teams/Slack
- Advanced RAG with graph knowledge

## Testing Strategy

### Unit Tests
- Service layer logic
- Data transformation functions
- Utility functions

### Integration Tests
- Azure service connections
- End-to-end sync workflow
- Query and response generation

### Performance Tests
- Large-scale sync operations
- Concurrent query handling
- Token usage optimization

## Documentation

- **README.md**: Overview and features
- **QUICKSTART.md**: Local setup guide
- **DEPLOYMENT.md**: Azure deployment guide
- **ARCHITECTURE.md**: This document
- Code comments: Docstrings for all classes/functions

## Compliance & Governance

### Data Privacy
- Work item data stored in Azure (region-specific)
- No PII exposure in logs
- GDPR compliance (Azure services)

### Audit Trail
- All sync operations logged
- Query history in Application Insights
- Change tracking for configuration

## Support & Maintenance

### SLA Targets
- Uptime: 99.9% (Container Apps SLA)
- Query Response: < 5 seconds
- Sync Duration: < 10 minutes (10K items)

### Incident Response
1. Monitor alerts trigger
2. Check Application Insights logs
3. Verify Azure service health
4. Review recent deployments
5. Rollback if needed
6. Post-incident review
