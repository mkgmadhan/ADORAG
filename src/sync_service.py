"""Sync service for orchestrating work item synchronization."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from .ado_service import ADOConnector
from .embedding_service import EmbeddingService
from .search_service import SearchIndexManager

logger = logging.getLogger(__name__)


class SyncManager:
    """Manages synchronization of work items from ADO to Azure AI Search."""

    def __init__(
        self,
        ado_connector: ADOConnector,
        embedding_service: EmbeddingService,
        search_manager: SearchIndexManager,
        project_name: str,
    ):
        """
        Initialize Sync Manager.

        Args:
            ado_connector: Azure DevOps connector instance
            embedding_service: Embedding service instance
            search_manager: Search index manager instance
            project_name: Name of the ADO project
        """
        self.ado_connector = ado_connector
        self.embedding_service = embedding_service
        self.search_manager = search_manager
        self.project_name = project_name

    def sync(
        self,
        force_full_sync: bool = False,
        batch_size: int = 50,
        progress_callback: Optional[callable] = None,
    ) -> Tuple[int, int]:
        """
        Synchronize work items from ADO to Azure AI Search.

        Args:
            force_full_sync: If True, perform full sync regardless of last sync time
            batch_size: Number of items to process per batch
            progress_callback: Optional callback function(step, current, total, message) for progress updates

        Returns:
            Tuple of (total_items_synced, total_items_in_index)
        """
        logger.info("Starting sync operation...")

        if progress_callback:
            progress_callback("init", 0, 100, "Initializing sync...")

        # Ensure index exists
        if not self.search_manager.index_exists():
            logger.info("Index does not exist, creating...")
            if progress_callback:
                progress_callback("index", 5, 100, "Creating search index...")
            self.search_manager.create_index()

        # Get last sync time
        sync_metadata = self.search_manager.get_sync_metadata()
        last_sync_time = None

        if not force_full_sync and sync_metadata:
            last_sync_time_str = sync_metadata.get("last_sync_time")
            if last_sync_time_str:
                last_sync_time = datetime.fromisoformat(last_sync_time_str.replace("Z", "+00:00"))
                logger.info(f"Last sync time: {last_sync_time}")

        # Fetch work items from ADO
        logger.info("Fetching work items from Azure DevOps...")
        if progress_callback:
            progress_callback("fetch", 10, 100, "Fetching work items from Azure DevOps...")
        
        work_items = self.ado_connector.fetch_work_items(
            project_name=self.project_name,
            last_sync_time=last_sync_time,
        )

        if not work_items:
            logger.info("No work items to sync")
            total_count = self.search_manager.get_work_item_count()
            if progress_callback:
                progress_callback("complete", 100, 100, "No new items to sync")
            return 0, total_count

        logger.info(f"Fetched {len(work_items)} work items")
        if progress_callback:
            progress_callback("fetched", 20, 100, f"Fetched {len(work_items)} work items")

        # Generate embeddings in batches
        logger.info("Generating embeddings...")
        synced_count = 0
        total_items = len(work_items)

        for i in range(0, len(work_items), batch_size):
            batch = work_items[i:i + batch_size]

            # Extract content for embedding
            batch_contents = [item["content"] for item in batch]

            # Generate embeddings
            if progress_callback:
                progress_pct = 20 + int((synced_count / total_items) * 60)
                progress_callback("embedding", progress_pct, 100, 
                                f"Generating embeddings: {synced_count}/{total_items}")
            
            embeddings = self.embedding_service.generate_embeddings_batch(
                texts=batch_contents,
                batch_size=16,  # API batch size
            )

            # Add embeddings to work items
            for item, embedding in zip(batch, embeddings):
                item["content_vector"] = embedding

            # Upsert to search index
            if progress_callback:
                progress_pct = 20 + int((synced_count / total_items) * 70)
                progress_callback("indexing", progress_pct, 100, 
                                f"Indexing: {synced_count + len(batch)}/{total_items}")
            
            self.search_manager.upsert_documents(batch)

            synced_count += len(batch)
            logger.info(f"Synced {synced_count}/{len(work_items)} work items")

        # Clean up deleted items (only during full sync)
        if force_full_sync:
            logger.info("Checking for deleted work items...")
            if progress_callback:
                progress_callback("cleanup", 95, 100, "Cleaning up deleted work items...")
            
            # Get all work item IDs currently in Azure DevOps
            ado_work_item_ids = self.ado_connector.get_all_work_item_ids(self.project_name)
            
            # Get all work item IDs from search index
            index_work_item_ids = self.search_manager.get_all_work_item_ids()
            
            # Find IDs that are in index but not in ADO (deleted items)
            deleted_ids = index_work_item_ids - ado_work_item_ids
            
            if deleted_ids:
                logger.info(f"Found {len(deleted_ids)} deleted work items to remove from index")
                self.search_manager.delete_documents(list(deleted_ids), self.project_name)
                logger.info(f"Removed {len(deleted_ids)} deleted work items from index")
            else:
                logger.info("No deleted work items found")

        # Update sync metadata
        current_time = datetime.utcnow()
        total_count = self.search_manager.get_work_item_count()

        self.search_manager.update_sync_metadata(
            last_sync_time=current_time,
            work_item_count=total_count,
        )

        logger.info(
            f"Sync completed: {synced_count} items synced, {total_count} total items in index"
        )

        return synced_count, total_count

    def get_sync_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current sync status.

        Returns:
            Dictionary with sync metadata or None
        """
        return self.search_manager.get_sync_metadata()

    def test_connections(self) -> Dict[str, bool]:
        """
        Test all service connections.

        Returns:
            Dictionary with connection test results
        """
        results = {}

        # Test ADO connection
        try:
            results["ado"] = self.ado_connector.test_connection(self.project_name)
        except Exception as e:
            logger.error(f"ADO connection test failed: {e}")
            results["ado"] = False

        # Test search index
        try:
            results["search"] = self.search_manager.index_exists()
        except Exception as e:
            logger.error(f"Search connection test failed: {e}")
            results["search"] = False

        # Test embedding service
        try:
            test_embedding = self.embedding_service.generate_embedding("test")
            results["embedding"] = len(test_embedding) > 0
        except Exception as e:
            logger.error(f"Embedding service test failed: {e}")
            results["embedding"] = False

        return results
