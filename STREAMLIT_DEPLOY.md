# Streamlit Cloud Deployment Guide

This guide walks you through deploying ADO RAG to Streamlit Cloud (free hosting).

## Prerequisites

✅ GitHub repository: https://github.com/mkgmadhan/ADORAG  
✅ Azure DevOps account with work items  
✅ Azure OpenAI and Azure AI Search services set up

## Step-by-Step Deployment

### 1. Go to Streamlit Cloud

Visit: **https://share.streamlit.io/**

### 2. Sign In

Click **"Sign in"** and authenticate with your GitHub account.

### 3. Deploy New App

Click **"New app"** button (or "Create app" if it's your first deployment).

### 4. Configure Repository

Fill in the deployment form:

- **Repository**: `mkgmadhan/ADORAG` 
  
  ⚠️ **Important**: Do NOT include `.git` at the end!

- **Branch**: `main`

- **Main file path**: `app.py`

### 5. Advanced Settings (Click "Advanced settings...")

#### App URL (Optional)
- You can customize the URL or leave it as default
- Example: `adorag-yourname.streamlit.app`

#### Python Version
- Select: **3.11** (or latest available)

#### Secrets
Click on "Secrets" and paste your configuration:

```toml
# Azure DevOps Configuration
ADO_ORGANIZATION = "your-org-name"
ADO_PROJECT_NAME = "your-project-name"
ADO_PAT = "your-personal-access-token"

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
AZURE_OPENAI_KEY = "your-openai-api-key"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
AZURE_OPENAI_CHAT_DEPLOYMENT = "gpt-4o-mini"
AZURE_OPENAI_API_VERSION = "2024-08-01-preview"

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT = "https://your-search-service.search.windows.net"
AZURE_SEARCH_KEY = "your-search-admin-key"
AZURE_SEARCH_INDEX_NAME = "adorag-workitems"

# Optional: Application Configuration
LOG_LEVEL = "INFO"
```

⚠️ **Copy from your `.env` file** and replace the values!

### 6. Deploy!

Click **"Deploy!"** button.

Streamlit Cloud will:
- Clone your GitHub repository
- Install dependencies from `requirements.txt`
- Start the application
- Provide you with a public URL

### 7. Wait for Deployment

Initial deployment takes 2-5 minutes. You'll see:
- 🟡 Installing dependencies...
- 🟡 Starting app...
- 🟢 App is live! ✨

### 8. Access Your App

Once deployed, you'll get a URL like:
```
https://adorag-yourname.streamlit.app
```

Click the link to open your app!

## Post-Deployment

### First Sync
- The app will automatically perform a full sync on first launch
- This may take a few minutes depending on your work item count
- Watch the sidebar for progress

### Auto-Updates
- Streamlit Cloud automatically redeploys when you push to GitHub
- Your secrets remain persistent across deployments

### Monitoring
- View app logs in the Streamlit Cloud dashboard
- Check "Manage app" → "Logs" for debugging

## Troubleshooting

### "This repository does not exist"
❌ You entered: `mkgmadhan/ADORAG.git`  
✅ Should be: `mkgmadhan/ADORAG` (no `.git`)

### "Module not found" errors
- Check that `requirements.txt` is in the repository root
- Streamlit Cloud automatically installs all dependencies

### "Missing environment variables"
- Verify all secrets are correctly entered in Advanced Settings
- Secret names must match exactly (case-sensitive)
- No quotes around secret values in TOML format

### App is slow or timing out
- Streamlit Cloud has resource limits (free tier)
- Large work item counts may cause timeouts
- Consider upgrading to Streamlit Cloud Pro for better performance

### Authentication failures
- Verify Azure DevOps PAT has correct permissions
- Check Azure OpenAI and Search keys are valid
- Ensure endpoints are correct (no trailing slashes where not needed)

## Making Changes

### Update Code
```bash
# Local changes
git add .
git commit -m "Update feature"
git push origin main

# Streamlit Cloud auto-deploys on push!
```

### Update Secrets
1. Go to https://share.streamlit.io/
2. Find your app
3. Click "︙" (three dots) → "Settings"
4. Update secrets
5. Click "Save"
6. App will restart automatically

## Cost & Limits

**Streamlit Cloud Free Tier:**
- ✅ Free forever
- ✅ Unlimited public apps
- ✅ 1 GB RAM per app
- ✅ 1 CPU core
- ⚠️ Apps sleep after inactivity (wake on access)

**Streamlit Cloud Pro** ($20/month):
- More resources (4 GB RAM)
- No sleeping
- Private apps
- Priority support

## Security Considerations

### Public vs Private
- **Free tier**: Apps are PUBLIC by default
- Anyone with the URL can access your app
- ⚠️ Do NOT expose sensitive Azure DevOps data publicly!

### Recommendations for Public Deployment
1. Use a demo/test Azure DevOps project
2. Ensure work items don't contain sensitive information
3. Consider authentication (requires custom code)

### For Private Deployment
- Upgrade to Streamlit Cloud Pro for private apps
- Or use Azure Container Apps (see [DEPLOYMENT.md](DEPLOYMENT.md))

## Alternative: Azure Container Apps

If you need:
- Private/secure access
- More resources
- Better performance
- Enterprise features

See [DEPLOYMENT.md](DEPLOYMENT.md) for Azure Container Apps deployment.

## Support

- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Community Forum**: https://discuss.streamlit.io/
- **GitHub Issues**: https://github.com/mkgmadhan/ADORAG/issues

---

**Ready to deploy? Start here**: https://share.streamlit.io/
