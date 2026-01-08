"""Azure DevOps connector for fetching work items."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from azure.devops.connection import Connection
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from msrest.authentication import BasicAuthentication

logger = logging.getLogger(__name__)


class ADOConnector:
    """Connector for Azure DevOps API to fetch work items."""

    def __init__(self, organization_url: str, personal_access_token: str):
        """
        Initialize ADO connector.

        Args:
            organization_url: Azure DevOps organization URL (e.g., https://dev.azure.com/myorg)
            personal_access_token: Personal Access Token with Work Items read permission
        """
        self.organization_url = organization_url
        self.pat = personal_access_token

        # Create connection
        credentials = BasicAuthentication("", personal_access_token)
        self.connection = Connection(base_url=organization_url, creds=credentials)
        self.wit_client: WorkItemTrackingClient = self.connection.clients.get_work_item_tracking_client()

    def fetch_work_items(
        self,
        project_name: str,
        last_sync_time: Optional[datetime] = None,
        batch_size: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        Fetch work items from Azure DevOps project.

        Args:
            project_name: Name of the ADO project
            last_sync_time: If provided, fetch only items changed after this time (delta sync)
            batch_size: Number of work items to fetch per batch

        Returns:
            List of work item dictionaries with extracted metadata
        """
        logger.info(f"Fetching work items from project: {project_name}")

        # Build WIQL query
        if last_sync_time:
            # Delta sync - fetch only changed items
            # Azure DevOps WIQL requires date-only format (no time component)
            changed_date_str = last_sync_time.strftime("%Y-%m-%d")
            wiql_query = f"""
                SELECT [System.Id]
                FROM WorkItems
                WHERE [System.TeamProject] = '{project_name}'
                AND [System.ChangedDate] >= '{changed_date_str}'
                ORDER BY [System.ChangedDate] DESC
            """
            logger.info(f"Delta sync from: {changed_date_str}")
        else:
            # Full sync - fetch all items
            wiql_query = f"""
                SELECT [System.Id]
                FROM WorkItems
                WHERE [System.TeamProject] = '{project_name}'
                ORDER BY [System.ChangedDate] DESC
            """
            logger.info("Full sync - fetching all work items")

        # Execute query
        wiql_query_obj = {"query": wiql_query}
        query_result = self.wit_client.query_by_wiql(wiql_query_obj)

        if not query_result.work_items:
            logger.info("No work items found")
            return []

        work_item_ids = [item.id for item in query_result.work_items]
        logger.info(f"Found {len(work_item_ids)} work items")

        # Fetch work items in batches
        work_items = []
        for i in range(0, len(work_item_ids), batch_size):
            batch_ids = work_item_ids[i:i + batch_size]
            batch_items = self.wit_client.get_work_items(
                ids=batch_ids,
                expand="All",  # Include all fields and relations
            )

            for item in batch_items:
                # Filter items if doing delta sync to only include items changed after last_sync_time
                if last_sync_time:
                    changed_date = item.fields.get("System.ChangedDate")
                    if changed_date:
                        # Parse if string
                        if isinstance(changed_date, str):
                            from dateutil import parser
                            changed_date = parser.parse(changed_date)
                        
                        # Ensure timezone-aware comparison
                        from datetime import timezone
                        if changed_date.tzinfo is None:
                            changed_date = changed_date.replace(tzinfo=timezone.utc)
                        if last_sync_time.tzinfo is None:
                            last_sync_time = last_sync_time.replace(tzinfo=timezone.utc)
                        
                        # Only include if changed after last sync time
                        if changed_date <= last_sync_time:
                            continue
                
                work_items.append(self._extract_work_item_data(item, project_name))

            logger.info(f"Processed batch {i // batch_size + 1}: {len(batch_items)} items")

        logger.info(f"Total work items fetched: {len(work_items)}")
        return work_items
    
    def get_all_work_item_ids(self, project_name: str) -> set:
        """
        Get all work item IDs from Azure DevOps project (without fetching full details).
        
        Args:
            project_name: Name of the ADO project
            
        Returns:
            Set of work item IDs as strings
        """
        logger.info(f"Fetching all work item IDs from project: {project_name}")
        
        wiql_query = f"""
            SELECT [System.Id]
            FROM WorkItems
            WHERE [System.TeamProject] = '{project_name}'
        """
        
        wiql_query_obj = {"query": wiql_query}
        query_result = self.wit_client.query_by_wiql(wiql_query_obj)
        
        if not query_result.work_items:
            logger.info("No work items found")
            return set()
        
        work_item_ids = set(str(item.id) for item in query_result.work_items)
        logger.info(f"Found {len(work_item_ids)} work item IDs in Azure DevOps")
        return work_item_ids

    def _extract_work_item_data(self, work_item: Any, project_name: str) -> Dict[str, Any]:
        """
        Extract and clean work item data.

        Args:
            work_item: Work item object from Azure DevOps API
            project_name: Name of the project

        Returns:
            Dictionary with extracted work item metadata
        """
        fields = work_item.fields

        # Extract basic fields
        work_item_id = str(work_item.id)
        title = fields.get("System.Title", "")
        description = self._clean_html(fields.get("System.Description", ""))
        work_item_type = fields.get("System.WorkItemType", "")
        state = fields.get("System.State", "")
        assigned_to = fields.get("System.AssignedTo", {}).get("displayName", "") if isinstance(
            fields.get("System.AssignedTo"), dict
        ) else str(fields.get("System.AssignedTo", ""))
        tags = fields.get("System.Tags", "")
        created_date = fields.get("System.CreatedDate")
        changed_date = fields.get("System.ChangedDate")
        
        # Extract additional fields
        acceptance_criteria = self._clean_html(fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", ""))
        repro_steps = self._clean_html(fields.get("Microsoft.VSTS.TCM.ReproSteps", ""))
        priority = fields.get("Microsoft.VSTS.Common.Priority", "")
        severity = fields.get("Microsoft.VSTS.Common.Severity", "")

        # Extract comments from history
        comments = self._extract_comments(work_item)

        # Build content for embedding (combine all searchable text)
        content_parts = [
            f"Title: {title}",
            f"Type: {work_item_type}",
            f"State: {state}",
        ]

        if description:
            content_parts.append(f"Description: {description}")
        
        if acceptance_criteria:
            content_parts.append(f"Acceptance Criteria: {acceptance_criteria}")
        
        if repro_steps:
            content_parts.append(f"Repro Steps: {repro_steps}")

        if tags:
            content_parts.append(f"Tags: {tags}")
        
        if priority:
            content_parts.append(f"Priority: {priority}")
        
        if severity:
            content_parts.append(f"Severity: {severity}")

        if assigned_to:
            content_parts.append(f"Assigned To: {assigned_to}")

        if comments:
            content_parts.append(f"Comments: {comments}")

        content = "\n\n".join(content_parts)

        # Build work item URL
        work_item_url = f"{self.organization_url}/{project_name}/_workitems/edit/{work_item_id}"

        # Convert dates to ISO format strings if they're datetime objects
        if created_date and hasattr(created_date, 'isoformat'):
            created_date = created_date.isoformat()
        if changed_date and hasattr(changed_date, 'isoformat'):
            changed_date = changed_date.isoformat()

        return {
            "id": f"{project_name}_{work_item_id}",
            "work_item_id": work_item_id,
            "title": title,
            "description": description,
            "work_item_type": work_item_type,
            "state": state,
            "assigned_to": assigned_to,
            "tags": tags,
            "project_name": project_name,
            "work_item_url": work_item_url,
            "created_date": created_date,
            "changed_date": changed_date,
            "content": content,
            "is_metadata": False,
        }

    def _extract_comments(self, work_item: Any) -> str:
        """
        Extract comments from work item.

        Args:
            work_item: Work item object

        Returns:
            Combined comments text
        """
        try:
            # Get comment history
            comments_list = []
            
            # Try to get comments from fields
            history = work_item.fields.get("System.History", "")
            if history:
                comments_list.append(self._clean_html(history))

            # Combine comments
            return " ".join(comments_list) if comments_list else ""

        except Exception as e:
            logger.warning(f"Error extracting comments: {e}")
            return ""

    def _clean_html(self, html_text: str) -> str:
        """
        Clean HTML tags from text.

        Args:
            html_text: HTML string

        Returns:
            Plain text with HTML tags removed
        """
        if not html_text:
            return ""

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_text, "lxml")
            text = soup.get_text(separator=" ", strip=True)
            return text
        except Exception as e:
            logger.warning(f"Error cleaning HTML: {e}")
            # Fallback: simple tag removal
            import re
            text = re.sub(r"<[^>]+>", " ", html_text)
            text = re.sub(r"\s+", " ", text).strip()
            return text

    def test_connection(self, project_name: str) -> bool:
        """
        Test connection to Azure DevOps.

        Args:
            project_name: Name of the project to test

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to get project
            core_client = self.connection.clients.get_core_client()
            project = core_client.get_project(project_name)
            logger.info(f"Successfully connected to project: {project.name}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
