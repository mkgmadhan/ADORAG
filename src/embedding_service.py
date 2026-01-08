"""Azure OpenAI embedding service for generating embeddings."""

import logging
from typing import List

import tiktoken
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Azure OpenAI."""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str,
        deployment_name: str,
        max_tokens: int = 8191,
    ):
        """
        Initialize Embedding Service.

        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            api_version: API version (e.g., '2024-02-15-preview')
            deployment_name: Name of the embedding model deployment
            max_tokens: Maximum tokens per request (default: 8191 for text-embedding-3-small)
        """
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        self.deployment_name = deployment_name
        self.max_tokens = max_tokens

        # Initialize tokenizer for text-embedding-3-small (uses cl100k_base encoding)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * 1536  # Return zero vector for empty text

        # Truncate text if it exceeds max tokens
        text = self._truncate_text(text)

        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.deployment_name,
            )
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of dimension {len(embedding)}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 16
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of input texts
            batch_size: Number of texts to process per API call

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Truncate texts in batch
            batch = [self._truncate_text(text) for text in batch]

            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.deployment_name,
                )

                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                logger.info(
                    f"Generated embeddings for batch {i // batch_size + 1}: "
                    f"{len(batch_embeddings)} embeddings"
                )

            except Exception as e:
                logger.error(f"Error generating embeddings for batch: {e}")
                # Add zero vectors for failed batch
                embeddings.extend([[0.0] * 1536] * len(batch))

        return embeddings

    def _truncate_text(self, text: str) -> str:
        """
        Truncate text to fit within max token limit.

        Args:
            text: Input text

        Returns:
            Truncated text
        """
        if not text:
            return ""

        tokens = self.tokenizer.encode(text)

        if len(tokens) <= self.max_tokens:
            return text

        # Truncate tokens and decode back to text
        truncated_tokens = tokens[:self.max_tokens]
        truncated_text = self.tokenizer.decode(truncated_tokens)

        logger.warning(
            f"Text truncated from {len(tokens)} to {self.max_tokens} tokens"
        )

        return truncated_text

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in text.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        if not text:
            return 0

        tokens = self.tokenizer.encode(text)
        return len(tokens)
