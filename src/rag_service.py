"""RAG service for querying and generating responses using Azure OpenAI."""

import logging
import re
from typing import Dict, Generator, List, Optional

from openai import AzureOpenAI

from .embedding_service import EmbeddingService
from .search_service import SearchIndexManager

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based query and response generation."""

    def __init__(
        self,
        openai_endpoint: str,
        openai_api_key: str,
        openai_api_version: str,
        chat_deployment_name: str,
        embedding_service: EmbeddingService,
        search_manager: SearchIndexManager,
    ):
        """
        Initialize RAG Service.

        Args:
            openai_endpoint: Azure OpenAI endpoint URL
            openai_api_key: Azure OpenAI API key
            openai_api_version: API version
            chat_deployment_name: Name of the chat model deployment (e.g., gpt-4o-mini)
            embedding_service: Embedding service instance
            search_manager: Search index manager instance
        """
        self.client = AzureOpenAI(
            azure_endpoint=openai_endpoint,
            api_key=openai_api_key,
            api_version=openai_api_version,
        )
        self.chat_deployment = chat_deployment_name
        self.embedding_service = embedding_service
        self.search_manager = search_manager

    def query(
        self,
        question: str,
        top_k: int = 5,
        temperature: float = 0.7,
        stream: bool = True,
    ) -> Generator[str, None, None]:
        """
        Query the RAG system and generate streaming response.

        Args:
            question: User's question
            top_k: Number of relevant work items to retrieve
            temperature: Sampling temperature for response generation
            stream: Whether to stream the response

        Yields:
            Response text chunks
        """
        logger.info(f"Processing query: {question[:100]}...")

        # Check if query is a simple greeting or conversational
        if self._is_greeting_or_conversational(question):
            yield self._get_conversational_response(question)
            return
        
        # Check if this is a bug triage/similarity query
        if self._is_bug_triage_query(question):
            for chunk in self._handle_bug_triage(question, temperature, stream):
                yield chunk
            return

        # Check if user is asking about a specific work item number
        work_item_filter = self._extract_work_item_filter(question)
        
        # Check if user is asking about a specific work item type
        type_filter = self._extract_work_item_type_filter(question)
        
        # Extract additional filters (state, priority, severity)
        comprehensive_filters = self._extract_comprehensive_filters(question)
        
        # Check if this is a count/list query to retrieve more results
        is_count_query = self._is_count_or_list_query(question)
        # Check if user wants to see the list of items or just the count
        wants_list = any(word in question.lower() for word in ['list', 'show', 'display', 'what are', 'which'])
        search_top_k = 50 if is_count_query else top_k

        # Generate embedding for the question
        question_embedding = self.embedding_service.generate_embedding(question)

        # Build filter expression
        filter_expr = "is_metadata eq false or is_metadata eq null"
        if work_item_filter:
            filter_expr = f"({filter_expr}) and ({work_item_filter})"
        if type_filter:
            filter_expr = f"({filter_expr}) and ({type_filter})"
        if comprehensive_filters:
            filter_expr = f"({filter_expr}) and ({comprehensive_filters})"

        # Retrieve relevant work items using hybrid search
        relevant_docs = self.search_manager.hybrid_search(
            query_text=question,
            query_vector=question_embedding,
            top_k=search_top_k,
            filter_expr=filter_expr,
        )
        
        print(f"[DEBUG RAG] Hybrid search returned {len(relevant_docs)} results")
        print(f"[DEBUG RAG] Filter: {filter_expr}")
        print(f"[DEBUG RAG] Work item types in results: {[d.get('work_item_type') for d in relevant_docs[:10]]}")

        if not relevant_docs:
            yield "I couldn't find any relevant work items to answer your question. Please try rephrasing or ask about different topics."
            return

        # For count queries, get the actual total count from the index
        actual_count = None
        print(f"[DEBUG] is_count_query={is_count_query}, type_filter={type_filter}, comprehensive_filters={comprehensive_filters}, work_item_filter={work_item_filter}")
        if is_count_query and (type_filter or work_item_filter or comprehensive_filters):
            print(f"[DEBUG] Calling get_filtered_count with filter: {filter_expr}")
            actual_count = self.search_manager.get_filtered_count(filter_expr)
            logger.info(f"Actual count for query: {actual_count}")
            print(f"[DEBUG] actual_count={actual_count}")
        else:
            print(f"[DEBUG] NOT calling get_filtered_count")

        # Build context based on whether user wants details or just count
        if actual_count is not None and not wants_list:
            # For simple count queries, just provide the number
            context = f"""===== ANSWER: {actual_count} =====
The total count is {actual_count}. Provide this number as your complete answer.
Do not list individual items unless the user asked to see them.
=================="""
            print(f"[DEBUG] Count-only response: {actual_count}")
        else:
            # Build full context with work item details
            context = self._build_context(relevant_docs)
            
            if actual_count is not None:
                context = f"""===== ANSWER: {actual_count} =====
The total count is {actual_count}. Use this number as your answer.
Below are {len(relevant_docs)} sample items for reference.
==================\n\n{context}"""
                print(f"[DEBUG] Added count {actual_count} with {len(relevant_docs)} items")
            else:
                print(f"[DEBUG] Regular query with {len(relevant_docs)} items")
        
        # Debug: Log the context being sent to AI
        logger.info(f"Context being sent to AI (length: {len(context)} chars):\n{context[:500]}...")

        # Build work item references
        references = self._build_references(relevant_docs)

        # Generate response
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(),
            },
            {
                "role": "user",
                "content": f"""Context from Azure DevOps work items:

{context}

Question: {question}

Please provide a comprehensive answer based on the work items above. Include specific work item IDs when referencing information.""",
            },
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=messages,
                temperature=temperature,
                stream=stream,
                max_tokens=1000,
            )

            if stream:
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content

            # Only append references if user wants to see the list
            if wants_list or not is_count_query:
                yield "\n\n---\n\n**Relevant Work Items:**\n\n"
                yield references

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            yield f"\n\nError generating response: {str(e)}"

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the chat model.

        Returns:
            System prompt string
        """
        return """You are an AI assistant for Azure DevOps work items.

**CRITICAL RULE FOR COUNTS:**
If the context starts with "===== ANSWER: [number] =====", that number IS your answer.
- If it says "Do not list individual items", provide ONLY the count (e.g., "There are 2097 user stories.")
- If it says "Below are X sample items", provide the count AND list the items
- NEVER count items in the list yourself - use the ANSWER number

General guidelines:
1. Answer using ONLY the provided context
2. Be concise - don't provide unnecessary details
3. Reference work item IDs when listing items (e.g., "Work Item #123")
4. Include metadata when relevant: Type, State, Priority, Severity

For specific work items:
- Include all relevant fields from context
- Quote directly from Comments or Acceptance Criteria when relevant
- Be comprehensive but concise

Remember: Only use information from the provided context. Don't invent details.

Be helpful, concise, and accurate."""

    def _build_context(self, documents: List[Dict]) -> str:
        """
        Build context string from retrieved documents.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        # Sort documents by work_item_id numerically
        sorted_docs = sorted(documents, key=lambda doc: int(doc.get("work_item_id", "0")))
        
        context_parts = []

        for i, doc in enumerate(sorted_docs, 1):
            work_item_id = doc.get("work_item_id", "Unknown")
            title = doc.get("title", "No title")
            work_item_type = doc.get("work_item_type", "Unknown")
            state = doc.get("state", "Unknown")
            assigned_to = doc.get("assigned_to", "Unassigned")
            tags = doc.get("tags", "")
            created_date = doc.get("created_date", "")
            changed_date = doc.get("changed_date", "")
            content = doc.get("content", "")

            # Build comprehensive work item context with all fields
            item_context = f"""
Work Item #{work_item_id}: {title}
Type: {work_item_type} | State: {state} | Assigned To: {assigned_to}
"""
            if tags:
                item_context += f"Tags: {tags}\n"
            if created_date:
                item_context += f"Created: {created_date}\n"
            if changed_date:
                item_context += f"Last Updated: {changed_date}\n"
            
            item_context += f"\n{content}"
            
            context_parts.append(item_context.strip())

        return "\n\n---\n\n".join(context_parts)

    def _build_references(self, documents: List[Dict]) -> str:
        """
        Build markdown references for work items.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted references string
        """
        # Sort documents by work_item_id numerically
        sorted_docs = sorted(documents, key=lambda doc: int(doc.get("work_item_id", "0")))
        
        references = []

        for doc in sorted_docs:
            work_item_id = doc.get("work_item_id", "Unknown")
            title = doc.get("title", "No title")
            work_item_type = doc.get("work_item_type", "Unknown")
            state = doc.get("state", "Unknown")
            url = doc.get("work_item_url", "#")

            reference = f"- [#{work_item_id}]({url}) - **{title}** ({work_item_type} - {state})"
            references.append(reference)

        return "\n".join(references)

    def _extract_work_item_type_filter(self, question: str) -> Optional[str]:
        """
        Extract work item type from the question and build a filter expression.
        
        Args:
            question: User's question
            
        Returns:
            Filter expression for work item type or None
        """
        question_lower = question.lower()
        
        # Map of common terms to work item types
        type_mapping = {
            'bug': 'Bug',
            'bugs': 'Bug',
            'issue': 'Bug',
            'issues': 'Bug',
            'defect': 'Bug',
            'defects': 'Bug',
            'user story': 'User Story',
            'user stories': 'User Story',
            'story': 'User Story',
            'stories': 'User Story',
            'task': 'Task',
            'tasks': 'Task',
            'epic': 'Epic',
            'epics': 'Epic',
            'feature': 'Feature',
            'features': 'Feature',
        }
        
        for term, work_item_type in type_mapping.items():
            if re.search(r'\b' + re.escape(term) + r'\b', question_lower):
                return f"work_item_type eq '{work_item_type}'"
        
        return None
    
    def _extract_comprehensive_filters(self, question: str) -> Optional[str]:
        """
        Extract comprehensive filters for state, priority, severity.
        
        Args:
            question: User question
            
        Returns:
            Combined filter expression or None
        """
        question_lower = question.lower()
        filters = []
        
        # State filters
        state_mappings = {
            'closed': 'Closed',
            'resolved': 'Resolved',
            'completed': 'Closed',
            'done': 'Closed',
            'active': 'Active',
            'open': 'Active',
            'in progress': 'Active',
            'new': 'New',
        }
        
        for term, state in state_mappings.items():
            if term in question_lower:
                filters.append(f"state eq '{state}'")
                break
        
        # Priority filters
        if 'priority 1' in question_lower or 'p1' in question_lower or 'highest priority' in question_lower:
            filters.append("priority eq '1'")
        elif 'priority 2' in question_lower or 'p2' in question_lower or 'high priority' in question_lower:
            filters.append("priority eq '2'")
        elif 'priority 3' in question_lower or 'p3' in question_lower or 'medium priority' in question_lower:
            filters.append("priority eq '3'")
        elif 'priority 4' in question_lower or 'p4' in question_lower or 'low priority' in question_lower:
            filters.append("priority eq '4'")
        
        # Severity filters
        if 'critical' in question_lower or 'severity 1' in question_lower:
            filters.append("severity eq '1 - Critical'")
        elif 'high severity' in question_lower or 'severity 2' in question_lower:
            filters.append("severity eq '2 - High'")
        elif 'medium severity' in question_lower or 'severity 3' in question_lower:
            filters.append("severity eq '3 - Medium'")
        elif 'low severity' in question_lower or 'severity 4' in question_lower:
            filters.append("severity eq '4 - Low'")
        
        if filters:
            return ' and '.join(filters)
        return None
    
    def _is_count_or_list_query(self, question: str) -> bool:
        """
        Detect if the question is asking for a count or list of items.
        
        Args:
            question: User's question
            
        Returns:
            True if it's a count/list query
        """
        count_patterns = [
            r'how many',
            r'count',
            r'number of',
            r'list all',
            r'show all',
            r'give me all',
            r'total',
        ]
        
        question_lower = question.lower()
        return any(re.search(pattern, question_lower) for pattern in count_patterns)
    
    def _extract_work_item_filter(self, question: str) -> Optional[str]:
        """
        Extract work item number(s) from the question and build a filter expression.

        Args:
            question: User's question

        Returns:
            Filter expression for work item IDs or None
        """
        import re
        
        # Match patterns like: #123, #61, WI-123, work item 123, item #123
        patterns = [
            r'#(\d+)',  # #123
            r'WI-(\d+)',  # WI-123
            r'work\s*item\s*#?(\d+)',  # work item 123 or work item #123
            r'item\s*#?(\d+)',  # item 123 or item #123
        ]
        
        work_item_ids = []
        for pattern in patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            work_item_ids.extend(matches)
        
        if not work_item_ids:
            return None
        
        # Remove duplicates while preserving order
        unique_ids = list(dict.fromkeys(work_item_ids))
        
        # Build filter expression
        if len(unique_ids) == 1:
            return f"work_item_id eq '{unique_ids[0]}'"
        else:
            # Multiple work items: (work_item_id eq '123' or work_item_id eq '456')
            conditions = [f"work_item_id eq '{wid}'" for wid in unique_ids]
            return "(" + " or ".join(conditions) + ")"
    
    def _is_bug_triage_query(self, question: str) -> bool:
        """
        Detect if user is asking to triage a bug or find similar bugs.
        
        Args:
            question: User's question
            
        Returns:
            True if it's a bug triage/similarity query
        """
        question_lower = question.lower()
        
        triage_patterns = [
            'similar bug', 'duplicate bug', 'same bug', 'related bug',
            'already logged', 'already reported', 'already exists',
            'valid bug', 'is this a bug', 'triage', 'related requirement',
            'match with requirement', 'associated requirement', 'check for duplicate'
        ]
        
        return any(pattern in question_lower for pattern in triage_patterns)
    
    def _handle_bug_triage(self, question: str, temperature: float = 0.3, stream: bool = True):
        """
        Handle bug triage queries: find similar bugs, match with requirements, determine validity.
        
        Args:
            question: User's question
            temperature: Temperature for response generation
            stream: Whether to stream the response
            
        Yields:
            Response chunks
        """
        try:
            # Extract bug ID if mentioned
            bug_id_filter = self._extract_work_item_filter(question)
            
            # Get bug details if ID provided
            bug_details = None
            bug_description = None
            
            if bug_id_filter:
                # Fetch the specific bug
                filter_expr = f"(is_metadata eq false or is_metadata eq null) and ({bug_id_filter}) and (work_item_type eq 'Bug')"
                bugs = self.search_manager.hybrid_search(
                    query_text=question,
                    query_vector=self.embedding_service.generate_embedding(question),
                    top_k=1,
                    filter_expr=filter_expr
                )
                if bugs:
                    bug_details = bugs[0]
                    bug_description = bug_details.get('content', '')
            else:
                # Extract bug description from question
                bug_description = question
            
            if not bug_description:
                yield "Please provide a bug ID (e.g., #123) or describe the bug you want to analyze."
                return
            
            # Search for similar bugs using semantic search
            similar_bugs_filter = "(is_metadata eq false or is_metadata eq null) and (work_item_type eq 'Bug')"
            if bug_id_filter:
                # Exclude the current bug
                similar_bugs_filter += f" and not ({bug_id_filter})"
            
            # Use full bug content for semantic embedding - captures complete context
            # Use vector-only search (empty query_text) to rely on semantic similarity
            embedding_text = bug_description if bug_description else question
            similar_bugs = self.search_manager.hybrid_search(
                query_text="",  # Empty to rely on vector search only
                query_vector=self.embedding_service.generate_embedding(embedding_text),
                top_k=10,
                filter_expr=similar_bugs_filter
            )
            
            # Search for related requirements (User Stories) using full content
            requirements = self.search_manager.hybrid_search(
                query_text="",  # Empty to rely on vector search only
                query_vector=self.embedding_service.generate_embedding(embedding_text),
                top_k=5,
                filter_expr="(is_metadata eq false or is_metadata eq null) and (work_item_type eq 'User Story')"
            )
            
            # Build context
            context_parts = []
            
            if bug_details:
                context_parts.append(f"""CURRENT BUG:
Work Item #{bug_details.get('work_item_id')}: {bug_details.get('title')}
Type: {bug_details.get('work_item_type')}
State: {bug_details.get('state')}
Priority: {bug_details.get('priority', 'N/A')}
Severity: {bug_details.get('severity', 'N/A')}

Description:
{bug_details.get('description', 'N/A')}

Repro Steps:
{bug_details.get('repro_steps', 'N/A')}
""")
            else:
                context_parts.append(f"BUG DESCRIPTION PROVIDED:\n{bug_description}\n")
            
            if similar_bugs:
                context_parts.append("\nSIMILAR BUGS FOUND:")
                for idx, bug in enumerate(similar_bugs[:5], 1):
                    desc = bug.get('description', 'N/A')
                    if len(desc) > 200:
                        desc = desc[:200] + "..."
                    context_parts.append(f"""
{idx}. Work Item #{bug.get('work_item_id')}: {bug.get('title')}
   State: {bug.get('state')} | Priority: {bug.get('priority', 'N/A')} | Severity: {bug.get('severity', 'N/A')}
   Description: {desc}""")
            else:
                context_parts.append("\nNo similar bugs found.")
            
            if requirements:
                context_parts.append("\n\nRELATED REQUIREMENTS (User Stories):")
                for idx, req in enumerate(requirements, 1):
                    desc = req.get('description', 'N/A')
                    if len(desc) > 200:
                        desc = desc[:200] + "..."
                    criteria = req.get('acceptance_criteria', 'N/A')
                    if len(criteria) > 200:
                        criteria = criteria[:200] + "..."
                    context_parts.append(f"""
{idx}. Work Item #{req.get('work_item_id')}: {req.get('title')}
   State: {req.get('state')}
   Description: {desc}
   Acceptance Criteria: {criteria}""")
            else:
                context_parts.append("\n\nNo directly related requirements found.")
            
            context = "\n".join(context_parts)
            
            # Build triage prompt
            triage_prompt = """Analyze this bug and provide:

1. **Similar Bugs**: List any similar or duplicate bugs found. Explain the similarities and likelihood of being duplicates.
2. **Related Requirements**: Identify which user stories/requirements this bug relates to. Explain the connection.
3. **Triage Decision**: Determine if this is:
   - A valid bug (explain why based on requirements and expected behavior)
   - A duplicate (reference the duplicate bug ID)
   - Not a bug / By design (explain based on requirements)
   - Needs more information (explain what's missing)

Provide a clear, structured analysis with specific references to work item IDs."""
            
            messages = [
                {"role": "system", "content": "You are a bug triage specialist. Analyze bugs for duplicates, match them with requirements, and provide triage decisions based on the provided context."},
                {"role": "user", "content": f"{context}\n\n{triage_prompt}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=messages,
                temperature=temperature,
                stream=stream,
                max_tokens=1500
            )
            
            if stream:
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content
            
            # Add references
            if similar_bugs or requirements:
                yield "\n\n---\n\n**Referenced Work Items:**\n\n"
                if similar_bugs:
                    yield "**Similar Bugs:**\n"
                    for bug in similar_bugs[:5]:
                        yield f"- [#{bug.get('work_item_id')} - {bug.get('title')}]({bug.get('work_item_url')})\n"
                if requirements:
                    yield "\n**Related Requirements:**\n"
                    for req in requirements:
                        yield f"- [#{req.get('work_item_id')} - {req.get('title')}]({req.get('work_item_url')})\n"
        
        except Exception as e:
            logger.error(f"Error in bug triage: {e}")
            yield f"Error analyzing bug: {str(e)}"

    def _is_greeting_or_conversational(self, text: str) -> bool:
        """
        Check if the query is a simple greeting or conversational message.

        Args:
            text: Query text

        Returns:
            True if it's a greeting/conversational, False otherwise
        """
        text_lower = text.lower().strip()
        
        # Simple greetings
        greetings = [
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon", 
            "good evening", "howdy", "hiya", "sup", "what's up", "whats up"
        ]
        
        # Conversational phrases that don't need work item search
        conversational = [
            "how are you", "thank you", "thanks", "bye", "goodbye", "ok", "okay",
            "nice", "cool", "great", "awesome", "perfect"
        ]
        
        # Check if text is just a greeting or conversational
        if text_lower in greetings or text_lower in conversational:
            return True
        
        # Check if text starts with greeting
        for greeting in greetings:
            if text_lower.startswith(greeting + " ") or text_lower.startswith(greeting + "!"):
                # But not if it's followed by a work item question
                question_keywords = ["show", "find", "search", "get", "list", "what", "how", "which", "when", "who", "bug", "issue", "task", "work item"]
                if not any(keyword in text_lower for keyword in question_keywords):
                    return True
        
        return False

    def _get_conversational_response(self, text: str) -> str:
        """
        Get a conversational response for greetings and casual messages.

        Args:
            text: Query text

        Returns:
            Conversational response
        """
        text_lower = text.lower().strip()
        
        if any(greeting in text_lower for greeting in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            return ("Hello! I'm your Azure DevOps Work Item Assistant. I can help you find and analyze work items from your DemoBugSense project.\n\n"
                   "Try asking me questions like:\n"
                   "- 'Show me all open bugs'\n"
                   "- 'What work items are assigned to [name]?'\n"
                   "- 'Find high priority tasks'\n"
                   "- 'What's the status of work item #123?'\n"
                   "- 'Show recent issues'")
        
        elif "thank" in text_lower:
            return "You're welcome! Feel free to ask me anything about your work items."
        
        elif any(bye in text_lower for bye in ["bye", "goodbye"]):
            return "Goodbye! Come back anytime you need help with your work items."
        
        else:
            return "I'm here to help you search and analyze Azure DevOps work items. Ask me a question about your work items!"

    def extract_work_item_ids(self, text: str) -> List[str]:
        """
        Extract work item IDs mentioned in text.

        Args:
            text: Text to search for work item IDs

        Returns:
            List of work item IDs
        """
        # Pattern to match Work Item #123 or #123
        pattern = r"#(\d+)"
        matches = re.findall(pattern, text)
        return list(set(matches))  # Remove duplicates
