# Issue Triage Workflow

This document describes the automated issue triage workflow for the ADORAG repository.

## Overview

The issue triage workflow automatically labels and categorizes new issues based on their content, helping maintainers quickly understand and prioritize incoming issues.

## How It Works

When a new issue is opened or edited, the workflow:

1. **Analyzes the issue content** - Examines both the title and body
2. **Assigns relevant labels** - Automatically adds appropriate labels
3. **Provides feedback** - Comments on the issue with triage information
4. **Checks for missing information** - For bug reports, validates that key details are present

## Labels

The workflow uses the following labels:

### Type Labels
- `bug` - Something isn't working correctly
- `enhancement` - New feature or improvement request
- `documentation` - Documentation improvements or issues
- `question` - Question about usage or functionality

### Priority Labels
- `priority: high` - Critical, urgent, or security-related issues
- `priority: medium` - Important issues that should be addressed soon

### Area Labels
- `area: azure-devops` - Related to Azure DevOps integration
- `area: sync` - Related to synchronization functionality
- `area: search` - Related to Azure AI Search or vector search
- `area: ai` - Related to OpenAI, GPT, embeddings, or RAG
- `area: ui` - Related to user interface or Streamlit
- `area: deployment` - Related to Docker, containers, or deployment
- `area: configuration` - Related to configuration or setup

### Status Labels
- `triage` - Issue has been automatically triaged (added to all new issues)
- `needs-info` - Additional information needed from reporter

## Label Setup

To ensure the workflow functions properly, create the following labels in your GitHub repository:

```bash
# Type labels
gh label create "bug" --color "d73a4a" --description "Something isn't working"
gh label create "enhancement" --color "a2eeef" --description "New feature or request"
gh label create "documentation" --color "0075ca" --description "Improvements or additions to documentation"
gh label create "question" --color "d876e3" --description "Further information is requested"

# Priority labels
gh label create "priority: high" --color "b60205" --description "High priority issue"
gh label create "priority: medium" --color "fbca04" --description "Medium priority issue"

# Area labels
gh label create "area: azure-devops" --color "006b75" --description "Azure DevOps integration"
gh label create "area: sync" --color "006b75" --description "Synchronization functionality"
gh label create "area: search" --color "006b75" --description "Search functionality"
gh label create "area: ai" --color "006b75" --description "AI and RAG functionality"
gh label create "area: ui" --color "006b75" --description "User interface"
gh label create "area: deployment" --color "006b75" --description "Deployment and infrastructure"
gh label create "area: configuration" --color "006b75" --description "Configuration and setup"

# Status labels
gh label create "triage" --color "ededed" --description "Automatically triaged"
gh label create "needs-info" --color "fef2c0" --description "More information needed"
```

## Trigger Keywords

The workflow looks for specific keywords to determine labels:

### Bug Detection
- "bug", "error", "fail", "crash", "broken", "not working"

### Enhancement Detection
- "feature", "enhancement", "add support", "would like"

### Documentation Detection
- "documentation", "docs", "readme", "guide"

### Question Detection
- "question", "how to", "how do i", "help"

### Priority Detection
- **High**: "critical", "urgent", "asap", "security", "data loss"
- **Medium**: "important", "blocker"

### Area Detection
- **Azure DevOps**: "azure devops", "ado", "work item"
- **Sync**: "sync", "synchronization", "delta sync"
- **Search**: "search", "azure ai search", "vector", "index"
- **AI**: "openai", "gpt", "llm", "rag", "embedding"
- **UI**: "ui", "interface", "streamlit", "display"
- **Deployment**: "deploy", "docker", "container", "azure container apps"
- **Configuration**: "config", "environment", ".env", "setup"

## Bug Report Validation

For issues labeled as bugs, the workflow checks for:

1. **Steps to reproduce** - Instructions to trigger the bug
2. **Expected behavior** - What should happen
3. **Actual behavior** - What actually happens
4. **Environment details** - Version and system information

If any of these are missing, the workflow:
- Adds a comment requesting the missing information
- Adds the `needs-info` label

## Customization

To modify the workflow behavior:

1. Edit `.github/workflows/issue-triage.yml`
2. Adjust the keyword detection logic in the script
3. Add or remove labels as needed
4. Update this documentation accordingly

## Maintainer Actions

After automatic triage, maintainers should:

1. **Review the labels** - Adjust if the automation was incorrect
2. **Remove the `triage` label** - After manual review
3. **Add additional labels** - If needed (e.g., good first issue, help wanted)
4. **Respond to questions** - For issues with missing information
5. **Prioritize** - Adjust priority labels based on business needs

## Benefits

- **Faster response time** - Issues are categorized immediately
- **Better organization** - Easy filtering and searching
- **Consistent labeling** - Automated approach ensures consistency
- **Reduced maintainer burden** - Less manual labeling work
- **Improved contributor experience** - Clear feedback on issue status

## Troubleshooting

### Workflow not triggering
- Check that the workflow file is in `.github/workflows/`
- Verify the file has correct YAML syntax
- Ensure the repository has Actions enabled

### Labels not being applied
- Verify the labels exist in the repository
- Check the workflow run logs for errors
- Ensure the workflow has `issues: write` permission

### Incorrect labels
- Review the keyword detection logic
- Add or adjust keywords in the workflow file
- Consider adding repository-specific terms

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Contributing Guide](../CONTRIBUTING.md)
- [Issue Templates](.github/ISSUE_TEMPLATE/) (if available)

---

*Last updated: 2026-02-16*
