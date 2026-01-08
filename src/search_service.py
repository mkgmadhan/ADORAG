"""Azure AI Search service for indexing and retrieving work items."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

logger = logging.getLogger(__name__)


class SearchIndexManager:
    """Manages Azure AI Search index operations for work items."""

    METADATA_DOC_ID = "sync-metadata"

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        index_name: str,
        embedding_dimension: int = 1536,
    ):
        """
        Initialize Search Index Manager.

        Args:
            endpoint: Azure AI Search endpoint URL
            api_key: Azure AI Search admin key
            index_name: Name of the search index
            embedding_dimension: Dimension of embedding vectors (default: 1536 for text-embedding-3-small)
        """
        self.endpoint = endpoint
        self.index_name = index_name
        self.embedding_dimension = embedding_dimension

        credential = AzureKeyCredential(api_key)
        self.index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
        self.search_client = SearchClient(
            endpoint=endpoint, index_name=index_name, credential=credential
        )

    def create_index(self) -> None:
        """Create the search index with vector and semantic search configuration."""
        logger.info(f"Creating search index: {self.index_name}")

        fields = [
            SearchField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
                sortable=True,
            ),
            SearchField(
                name="work_item_id",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
            ),
            SearchField(
                name="title",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=True,
            ),
            SearchField(
                name="description",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchField(
                name="work_item_type",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),
            SearchField(
                name="state",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),
            SearchField(
                name="assigned_to",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),
            SearchField(
                name="tags",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchField(
                name="project_name",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SearchField(
                name="work_item_url",
                type=SearchFieldDataType.String,
                filterable=False,
            ),
            SearchField(
                name="created_date",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
            ),
            SearchField(
                name="changed_date",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
            ),
            SearchField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=self.embedding_dimension,
                vector_search_profile_name="vector-profile",
            ),
            # Metadata fields
            SearchField(
                name="is_metadata",
                type=SearchFieldDataType.Boolean,
                filterable=True,
            ),
            SearchField(
                name="last_sync_time",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
            ),
            SearchField(
                name="work_item_count",
                type=SearchFieldDataType.Int32,
                filterable=True,
            ),
        ]

        # Configure vector search
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="hnsw-algorithm",
                    parameters={
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine",
                    },
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="hnsw-algorithm",
                )
            ],
        )

        # Configure semantic search
        semantic_config = SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                content_fields=[
                    SemanticField(field_name="description"),
                    SemanticField(field_name="content"),
                ],
                keywords_fields=[
                    SemanticField(field_name="tags"),
                    SemanticField(field_name="work_item_type"),
                ],
            ),
        )

        semantic_search = SemanticSearch(configurations=[semantic_config])

        # Create the index
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search,
        )

        self.index_client.create_or_update_index(index)
        logger.info(f"Search index '{self.index_name}' created successfully")

    def index_exists(self) -> bool:
        """Check if the search index exists."""
        try:
            self.index_client.get_index(self.index_name)
            return True
        except Exception:
            return False

    def upsert_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Upsert documents to the search index.

        Args:
            documents: List of document dictionaries to upsert
        """
        if not documents:
            logger.warning("No documents to upsert")
            return

        try:
            result = self.search_client.upload_documents(documents=documents)
            success_count = sum(1 for r in result if r.succeeded)
            logger.info(f"Upserted {success_count}/{len(documents)} documents")
        except Exception as e:
            logger.error(f"Error upserting documents: {e}")
            raise

    def get_sync_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve sync metadata from the index.

        Returns:
            Dictionary containing last_sync_time and work_item_count, or None if not found
        """
        try:
            result = self.search_client.get_document(key=self.METADATA_DOC_ID)
            return {
                "last_sync_time": result.get("last_sync_time"),
                "work_item_count": result.get("work_item_count", 0),
            }
        except Exception:
            return None

    def update_sync_metadata(
        self, last_sync_time: datetime, work_item_count: int
    ) -> None:
        """
        Update sync metadata in the index.

        Args:
            last_sync_time: Timestamp of the last successful sync
            work_item_count: Total number of work items indexed
        """
        # Format datetime with timezone for Edm.DateTimeOffset
        last_sync_time_str = last_sync_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        metadata_doc = {
            "id": self.METADATA_DOC_ID,
            "is_metadata": True,
            "last_sync_time": last_sync_time_str,
            "work_item_count": work_item_count,
            "work_item_id": self.METADATA_DOC_ID,
            "title": "Sync Metadata",
            "description": "Internal metadata document",
            "work_item_type": "Metadata",
            "state": "Active",
            "project_name": "System",
            "work_item_url": "",
            "content": "",
            "content_vector": [0.0] * self.embedding_dimension,  # Dummy vector
        }

        try:
            self.search_client.upload_documents(documents=[metadata_doc])
            logger.info(f"Updated sync metadata: {work_item_count} work items")
        except Exception as e:
            logger.error(f"Error updating sync metadata: {e}")
            raise

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_expr: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using vector similarity.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_expr: Optional OData filter expression

        Returns:
            List of matching documents with scores
        """
        try:
            vector_query = VectorizedQuery(
                vector=query_vector, k_nearest_neighbors=top_k, fields="content_vector"
            )

            results = self.search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                filter=filter_expr,
                select=[
                    "work_item_id",
                    "title",
                    "description",
                    "work_item_type",
                    "state",
                    "assigned_to",
                    "tags",
                    "work_item_url",
                    "content",
                ],
                top=top_k,
            )

            documents = []
            for result in results:
                doc = dict(result)
                doc["score"] = result.get("@search.score", 0)
                documents.append(doc)

            logger.info(f"Search returned {len(documents)} results")
            return documents

        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise

    def hybrid_search(
        self,
        query_text: str,
        query_vector: List[float],
        top_k: int = 5,
        filter_expr: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector and keyword search with semantic ranking.

        Args:
            query_text: Text query for keyword search
            query_vector: Query embedding vector for vector search
            top_k: Number of results to return
            filter_expr: Optional OData filter expression

        Returns:
            List of matching documents with scores
        """
        try:
            vector_query = VectorizedQuery(
                vector=query_vector, k_nearest_neighbors=50, fields="content_vector"
            )

            results = self.search_client.search(
                search_text=query_text,
                vector_queries=[vector_query],
                filter=filter_expr,
                select=[
                    "work_item_id",
                    "title",
                    "description",
                    "work_item_type",
                    "state",
                    "assigned_to",
                    "tags",
                    "created_date",
                    "changed_date",
                    "work_item_url",
                    "content",
                ],
                top=top_k,
                query_type="semantic",
                semantic_configuration_name="semantic-config",
            )

            documents = []
            for result in results:
                doc = dict(result)
                doc["score"] = result.get("@search.score", 0)
                doc["reranker_score"] = result.get("@search.reranker_score", 0)
                documents.append(doc)

            logger.info(f"Hybrid search returned {len(documents)} results")
            return documents

        except Exception as e:
            logger.error(f"Error during hybrid search: {e}")
            raise

    def get_work_item_count(self) -> int:
        """
        Get total count of indexed work items (excluding metadata).

        Returns:
            Total number of work items in the index
        """
        try:
            results = self.search_client.search(
                search_text="*",
                filter="is_metadata eq false or is_metadata eq null",
                include_total_count=True,
                top=0,
            )
            return results.get_count()
        except Exception:
            return 0
    
    def get_filtered_count(self, filter_expr: str) -> int:
        """
        Get count of work items matching a filter expression.
        
        Args:
            filter_expr: OData filter expression
            
        Returns:
            Count of matching work items
        """
        try:
            logger.info(f"Getting count with filter: {filter_expr}")
            results = self.search_client.search(
                search_text="*",
                filter=filter_expr,
                include_total_count=True,
                top=0,
            )
            count = results.get_count()
            logger.info(f"Filtered count result: {count}")
            return count
        except Exception as e:
            logger.error(f"Error getting filtered count: {e}")
            return 0
    
    def get_all_work_item_ids(self) -> set:
        """
        Get all work item IDs from the search index.
        
        Returns:
            Set of work item IDs as strings
        """
        try:
            results = self.search_client.search(
                search_text="*",
                filter="is_metadata eq false or is_metadata eq null",
                select=["work_item_id"],
                top=10000  # Adjust if you have more items
            )
            
            work_item_ids = set(str(doc['work_item_id']) for doc in results)
            logger.info(f"Retrieved {len(work_item_ids)} work item IDs from index")
            return work_item_ids
        except Exception as e:
            logger.error(f"Error getting work item IDs: {e}")
            return set()
    
    def delete_documents(self, work_item_ids: list, project_name: str) -> None:
        """
        Delete documents from the search index by work item IDs.
        
        Args:
            work_item_ids: List of work item IDs to delete
            project_name: Project name to construct full document IDs
        """
        try:
            if not work_item_ids:
                return
            
            # Create documents with proper ID format: {project_name}_{work_item_id}
            documents_to_delete = [{"id": f"{project_name}_{wid}"} for wid in work_item_ids]
            
            logger.info(f"Deleting {len(documents_to_delete)} documents from index")
            result = self.search_client.delete_documents(documents=documents_to_delete)
            
            # Check results
            succeeded = sum(1 for r in result if r.succeeded)
            failed = len(result) - succeeded
            
            if failed > 0:
                logger.warning(f"Deleted {succeeded} documents, {failed} failed")
            else:
                logger.info(f"Successfully deleted {succeeded} documents")
                
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
