# Deployment Guide

## Azure Container Apps Deployment

### Prerequisites

1. Azure subscription
2. Azure CLI installed (`az` command)
3. Docker installed locally
4. Azure Container Registry (or Docker Hub)
5. Azure resources created:
   - Azure OpenAI Service with deployments
   - Azure AI Search service
   - Azure Container Apps environment (optional, will create if needed)

### Step 1: Prepare Azure Resources

#### Create Resource Group
```bash
az group create --name adorag-rg --location eastus
```

#### Create Azure Container Registry
```bash
az acr create --resource-group adorag-rg --name adoragacr --sku Basic
az acr login --name adoragacr
```

#### Create Container Apps Environment (if needed)
```bash
az containerapp env create \
  --name adorag-env \
  --resource-group adorag-rg \
  --location eastus
```

### Step 2: Build and Push Docker Image

#### Build Docker image locally
```bash
docker build -t adorag:latest .
```

#### Tag and push to ACR
```bash
docker tag adorag:latest adoragacr.azurecr.io/adorag:latest
docker push adoragacr.azurecr.io/adorag:latest
```

### Step 3: Deploy to Container Apps

#### Deploy with environment variables
```bash
az containerapp create \
  --name adorag-app \
  --resource-group adorag-rg \
  --environment adorag-env \
  --image adoragacr.azurecr.io/adorag:latest \
  --target-port 8501 \
  --ingress external \
  --registry-server adoragacr.azurecr.io \
  --query properties.configuration.ingress.fqdn \
  --env-vars \
    ADO_ORGANIZATION=https://dev.azure.com/your-org \
    ADO_PROJECT_NAME=YourProject \
    ADO_PAT=your-personal-access-token \
    AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/ \
    AZURE_OPENAI_KEY=your-openai-key \
    AZURE_OPENAI_API_VERSION=2024-02-15-preview \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small \
    AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini \
    AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net \
    AZURE_SEARCH_KEY=your-search-key \
    AZURE_SEARCH_INDEX_NAME=ado-workitems \
    LOG_LEVEL=INFO
```

### Step 4: Configure Managed Identity (Optional, Recommended)

#### Enable managed identity
```bash
az containerapp identity assign \
  --name adorag-app \
  --resource-group adorag-rg \
  --system-assigned
```

#### Grant permissions to Azure OpenAI and Search
```bash
# Get the identity principal ID
IDENTITY_ID=$(az containerapp identity show \
  --name adorag-app \
  --resource-group adorag-rg \
  --query principalId \
  --output tsv)

# Assign Cognitive Services OpenAI User role
az role assignment create \
  --role "Cognitive Services OpenAI User" \
  --assignee $IDENTITY_ID \
  --scope /subscriptions/{subscription-id}/resourceGroups/{openai-rg}/providers/Microsoft.CognitiveServices/accounts/{openai-name}

# Assign Search Index Data Contributor role
az role assignment create \
  --role "Search Index Data Contributor" \
  --assignee $IDENTITY_ID \
  --scope /subscriptions/{subscription-id}/resourceGroups/{search-rg}/providers/Microsoft.Search/searchServices/{search-name}
```

### Step 5: Scale Configuration

#### Configure scaling rules
```bash
az containerapp update \
  --name adorag-app \
  --resource-group adorag-rg \
  --min-replicas 1 \
  --max-replicas 3 \
  --scale-rule-name azure-http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50
```

### Step 6: Monitor and Logs

#### View logs
```bash
az containerapp logs show \
  --name adorag-app \
  --resource-group adorag-rg \
  --follow
```

#### View application insights
```bash
az monitor app-insights component show \
  --app adorag-app \
  --resource-group adorag-rg
```

### Step 7: Update Application

#### Build and push new version
```bash
docker build -t adorag:v2 .
docker tag adorag:v2 adoragacr.azurecr.io/adorag:v2
docker push adoragacr.azurecr.io/adorag:v2
```

#### Update container app
```bash
az containerapp update \
  --name adorag-app \
  --resource-group adorag-rg \
  --image adoragacr.azurecr.io/adorag:v2
```

---

## Alternative: Azure App Service Deployment

### Create App Service Plan
```bash
az appservice plan create \
  --name adorag-plan \
  --resource-group adorag-rg \
  --is-linux \
  --sku B1
```

### Create Web App
```bash
az webapp create \
  --name adorag-webapp \
  --resource-group adorag-rg \
  --plan adorag-plan \
  --deployment-container-image-name adoragacr.azurecr.io/adorag:latest
```

### Configure environment variables
```bash
az webapp config appsettings set \
  --name adorag-webapp \
  --resource-group adorag-rg \
  --settings \
    ADO_ORGANIZATION=https://dev.azure.com/your-org \
    ADO_PROJECT_NAME=YourProject \
    # ... (add all other environment variables)
```

---

## Switching Between ADO Projects

To point the application to a different Azure DevOps project:

1. Update environment variables in Container Apps:
```bash
az containerapp update \
  --name adorag-app \
  --resource-group adorag-rg \
  --set-env-vars \
    ADO_ORGANIZATION=https://dev.azure.com/new-org \
    ADO_PROJECT_NAME=NewProject \
    ADO_PAT=new-pat-token
```

2. Restart the container app to reload configuration
3. The application will automatically perform a full sync on first launch

---

## Cost Optimization Tips

1. **Scale to Zero**: Configure min replicas to 0 for development environments
2. **Use Spot Instances**: For non-production workloads
3. **Monitor Token Usage**: Track Azure OpenAI token consumption
4. **Optimize Sync Frequency**: Use delta sync and schedule appropriately
5. **Right-size Search Tier**: Start with Basic tier and scale up if needed

---

## Troubleshooting

### Connection Issues
- Verify all endpoint URLs are correct
- Check API keys are valid and not expired
- Ensure network connectivity between services

### Sync Failures
- Verify ADO PAT has correct permissions (Work Items: Read)
- Check if ADO organization and project names are correct
- Review logs for specific error messages

### Search Issues
- Ensure Azure AI Search index exists
- Verify semantic search is enabled in Azure portal
- Check API key has admin permissions

### OpenAI Errors
- Verify model deployments exist
- Check rate limits and quotas
- Ensure API version is compatible with models

---

## Security Best Practices

1. **Use Managed Identity** instead of API keys where possible
2. **Store secrets in Azure Key Vault** and reference in Container Apps
3. **Enable HTTPS only** for ingress
4. **Restrict network access** using VNet integration
5. **Rotate PATs regularly** (every 90 days recommended)
6. **Enable audit logging** for compliance
7. **Use RBAC** for fine-grained access control

---

## Monitoring and Alerts

### Set up alerts
```bash
# Alert on high error rate
az monitor metrics alert create \
  --name adorag-high-errors \
  --resource-group adorag-rg \
  --scopes /subscriptions/{sub-id}/resourceGroups/adorag-rg/providers/Microsoft.App/containerApps/adorag-app \
  --condition "avg Percentage CPU > 80" \
  --description "Alert when CPU usage is high"
```

### Application Insights integration
- Automatically enabled in Container Apps
- View metrics, logs, and traces in Azure portal
- Set up custom dashboards and workbooks
