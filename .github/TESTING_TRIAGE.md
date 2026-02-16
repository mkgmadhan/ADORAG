# Testing the Issue Triage Workflow

This document explains how to test the automated issue triage workflow.

## Prerequisites

1. The workflow is in `.github/workflows/issue-triage.yml`
2. Labels must be created in the repository (run `.github/setup-labels.sh`)
3. GitHub Actions must be enabled for the repository

## Testing Approach

### 1. Set Up Labels

First, create all the required labels:

```bash
cd .github
./setup-labels.sh
```

Or manually create them using the GitHub UI or the commands in `.github/ISSUE_TRIAGE.md`.

### 2. Test Cases

Create test issues with different content to verify the workflow:

#### Test Case 1: Bug Report
**Title**: "Application crashes when syncing work items"
**Body**: "The app crashes with an error message when I try to sync. It's urgent and breaking our workflow."

**Expected Labels**: `bug`, `area: sync`, `priority: high`, `triage`

#### Test Case 2: Feature Request
**Title**: "Add support for custom fields"
**Body**: "Would like to add support for custom work item fields in Azure DevOps"

**Expected Labels**: `enhancement`, `area: azure-devops`, `triage`

#### Test Case 3: Documentation Issue
**Title**: "Improve setup documentation"
**Body**: "The README could use more details about environment configuration"

**Expected Labels**: `documentation`, `area: configuration`, `triage`

#### Test Case 4: Question
**Title**: "How to configure Azure OpenAI endpoint?"
**Body**: "I need help setting up my Azure OpenAI endpoint. How do I do this?"

**Expected Labels**: `question`, `area: ai`, `area: configuration`, `triage`

#### Test Case 5: Incomplete Bug Report
**Title**: "Search not working"
**Body**: "The search feature is broken."

**Expected Labels**: `bug`, `area: search`, `triage`, `needs-info`
**Expected Comment**: Request for missing information (steps, expected/actual behavior)

#### Test Case 6: UI Issue with High Priority
**Title**: "Critical UI bug: Buttons not responding"
**Body**: "Critical issue - the UI buttons in streamlit are not responding to clicks. This is blocking our demo."

**Expected Labels**: `bug`, `area: ui`, `priority: high`, `triage`

#### Test Case 7: Deployment Question
**Title**: "Docker container fails to start"
**Body**: "When I try to deploy using the Dockerfile, the container fails to start. Need help with azure container apps deployment."

**Expected Labels**: `bug`, `area: deployment`, `triage`

### 3. Verify Workflow Execution

After creating a test issue:

1. Go to the **Actions** tab in the GitHub repository
2. Look for the "Issue Triage" workflow run
3. Click on the workflow run to see details
4. Verify that:
   - The workflow completed successfully
   - No errors occurred
   - The correct steps were executed

### 4. Verify Issue Updates

For each test issue created:

1. Check that the expected labels were applied
2. Verify that the triage comment was posted
3. For incomplete bug reports, verify the "needs-info" comment was posted

### 5. Test Editing

Edit an existing issue by adding more keywords:

1. Open a test issue
2. Edit the body to add keywords (e.g., add "critical" to make it high priority)
3. Save the changes
4. Verify that the workflow runs again and updates labels appropriately

## Monitoring

### Workflow Logs

To debug issues, check the workflow logs:

1. Go to Actions → Issue Triage workflow
2. Click on a specific run
3. Expand the "Analyze and label issue" step
4. Check console.log outputs for debugging information

### Common Issues

**Workflow doesn't trigger:**
- Check that the workflow file is in `.github/workflows/`
- Verify GitHub Actions is enabled
- Check the syntax with `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/issue-triage.yml'))"`

**Labels not applied:**
- Verify labels exist in the repository
- Check workflow permissions (issues: write)
- Review workflow logs for errors

**Incorrect labels:**
- Review the keyword detection logic in the workflow file
- Add repository-specific terms if needed
- Adjust keyword lists in the workflow

## Cleanup

After testing, you can:

1. Close test issues
2. Remove test labels if desired
3. Keep the workflow enabled for production use

## Production Use

Once testing is complete:

1. Keep all labels
2. Enable the workflow for all new issues
3. Monitor the first few weeks to adjust keyword detection
4. Train team members on how to interpret auto-applied labels
5. Periodically review and adjust the workflow based on actual usage

---

For more information, see:
- [.github/ISSUE_TRIAGE.md](.github/ISSUE_TRIAGE.md) - Full workflow documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
