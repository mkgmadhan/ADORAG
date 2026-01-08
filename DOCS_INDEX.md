# ADO RAG Documentation Index

Welcome to the ADO RAG documentation! This guide will help you find the right documentation for your needs.

## 📚 Documentation Overview

### Getting Started
Start here if you're new to ADO RAG:

1. **[README.md](README.md)** - Main project overview
   - Features and capabilities
   - Quick start guide
   - Architecture overview
   - Cost information

2. **[QUICKSTART.md](QUICKSTART.md)** - Fast setup guide
   - 5-minute setup for experienced users
   - Essential configuration only
   - Quick validation steps

3. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Detailed setup guide
   - Step-by-step instructions
   - Prerequisite details
   - Troubleshooting common issues
   - First-time user walkthrough

### Technical Documentation

4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture
   - System design and components
   - Data flow diagrams
   - Technology stack details
   - Design decisions and rationale

5. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview
   - Feature list and capabilities
   - Development history
   - Technical specifications

### Deployment & Operations

6. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guides
   - Docker deployment
   - Azure Container Apps
   - Azure App Service
   - Environment configuration
   - Production best practices

### Contributing

7. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
   - How to contribute
   - Code style guidelines
   - Pull request process
   - Development setup

8. **[LICENSE](LICENSE)** - MIT License
   - Usage rights and restrictions

## 🚀 Quick Navigation by Task

### I want to...

**Install and run ADO RAG locally**
→ Start with [README.md](README.md#quick-start) or [QUICKSTART.md](QUICKSTART.md)

**Understand how ADO RAG works**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md)

**Deploy to production**
→ Follow [DEPLOYMENT.md](DEPLOYMENT.md)

**Configure Azure services**
→ See [GETTING_STARTED.md](GETTING_STARTED.md#azure-setup)

**Troubleshoot issues**
→ Check [README.md](README.md#troubleshooting) or [GETTING_STARTED.md](GETTING_STARTED.md#troubleshooting)

**Contribute code**
→ Read [CONTRIBUTING.md](CONTRIBUTING.md)

**Understand costs**
→ See [README.md](README.md#cost-optimization)

**Use the bug triage feature**
→ See [README.md](README.md#bug-triage)

## 📖 Documentation by Audience

### For End Users
- [README.md](README.md) - Overview and basic usage
- [README.md - Usage Section](README.md#usage) - How to use the chat interface

### For Administrators
- [GETTING_STARTED.md](GETTING_STARTED.md) - Complete setup guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment options
- [README.md - Configuration](README.md#configuration) - Configuration reference

### For Developers
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Technical specifications

### For Decision Makers
- [README.md](README.md) - Feature overview
- [README.md - Cost Optimization](README.md#cost-optimization) - Cost analysis
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture

## 📁 Source Code Structure

```
ADORag/
├── app.py                          # Main Streamlit application
├── src/
│   ├── ado_service.py             # Azure DevOps integration
│   ├── search_service.py          # Azure AI Search operations
│   ├── embedding_service.py       # Embedding generation
│   ├── rag_service.py             # RAG processing and chat
│   ├── sync_service.py            # Sync orchestration
│   └── utils.py                   # Utilities and configuration
├── requirements.txt                # Python dependencies
├── Dockerfile                     # Container definition
├── .env.example                   # Environment template
└── test_config.py                 # Configuration validation
```

## 🔗 External Resources

### Azure Documentation
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure AI Search](https://learn.microsoft.com/en-us/azure/search/)
- [Azure DevOps REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)

### Technology Documentation
- [Streamlit](https://docs.streamlit.io/)
- [Python Azure SDK](https://azure.github.io/azure-sdk-for-python/)

## 💡 Tips

### First Time Setup
1. Read [README.md](README.md) for overview
2. Follow [QUICKSTART.md](QUICKSTART.md) or [GETTING_STARTED.md](GETTING_STARTED.md)
3. Use `.env.example` as template for your `.env` file
4. Run `python test_config.py` to validate configuration
5. Start with `streamlit run app.py`

### Production Deployment
1. Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
2. Follow [DEPLOYMENT.md](DEPLOYMENT.md) for your platform
3. Configure monitoring and logging
4. Review [README.md - Cost Optimization](README.md#cost-optimization)

### Troubleshooting
1. Check error messages in Streamlit interface
2. Review [README.md - Troubleshooting](README.md#troubleshooting)
3. Validate configuration with `test_config.py`
4. Check Azure service health in Azure Portal
5. Review logs for detailed error information

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/mkgmadhan/ADORAG/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mkgmadhan/ADORAG/discussions)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

Last Updated: January 2026
