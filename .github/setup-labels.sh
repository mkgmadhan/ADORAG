#!/bin/bash
#
# Script to create GitHub labels for the issue triage workflow
# 
# Usage: ./setup-labels.sh [owner/repo]
#
# Requires GitHub CLI (gh) to be installed and authenticated
# Install: https://cli.github.com/

set -e

# Get repository from argument or detect from git remote
if [ -z "$1" ]; then
    REPO=$(git remote get-url origin | sed -E 's/.*[:/]([^/]+\/[^/]+)(\.git)?$/\1/')
    echo "Using repository: $REPO"
else
    REPO=$1
fi

echo "Creating labels for repository: $REPO"
echo ""

# Function to create or update a label
create_label() {
    local name=$1
    local color=$2
    local description=$3
    
    echo "Creating label: $name"
    gh label create "$name" --color "$color" --description "$description" --repo "$REPO" 2>/dev/null || \
    gh label edit "$name" --color "$color" --description "$description" --repo "$REPO" 2>/dev/null || \
    echo "  → Label already exists or couldn't be created: $name"
}

echo "Creating type labels..."
create_label "bug" "d73a4a" "Something isn't working"
create_label "enhancement" "a2eeef" "New feature or request"
create_label "documentation" "0075ca" "Improvements or additions to documentation"
create_label "question" "d876e3" "Further information is requested"

echo ""
echo "Creating priority labels..."
create_label "priority: high" "b60205" "High priority issue"
create_label "priority: medium" "fbca04" "Medium priority issue"

echo ""
echo "Creating area labels..."
create_label "area: azure-devops" "006b75" "Azure DevOps integration"
create_label "area: sync" "006b75" "Synchronization functionality"
create_label "area: search" "006b75" "Search functionality"
create_label "area: ai" "006b75" "AI and RAG functionality"
create_label "area: ui" "006b75" "User interface"
create_label "area: deployment" "006b75" "Deployment and infrastructure"
create_label "area: configuration" "006b75" "Configuration and setup"

echo ""
echo "Creating status labels..."
create_label "triage" "ededed" "Automatically triaged"
create_label "needs-info" "fef2c0" "More information needed"

echo ""
echo "✓ Label setup complete!"
echo ""
echo "You can view all labels at: https://github.com/$REPO/labels"
