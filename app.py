"""Streamlit chat application for ADO RAG."""

import logging
import time
from datetime import datetime

import streamlit as st

from src.ado_service import ADOConnector
from src.embedding_service import EmbeddingService
from src.rag_service import RAGService
from src.search_service import SearchIndexManager
from src.sync_service import SyncManager
from src.utils import load_config, setup_logging, validate_config

# Configure page
st.set_page_config(
    page_title="ADO Work Item Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def initialize_services():
    """Initialize all services with caching."""
    try:
        # Load configuration
        config = load_config()
        validate_config(config)

        # Setup logging
        setup_logging(config["log_level"])
        logger = logging.getLogger(__name__)
        logger.info("Initializing services...")

        # Initialize Azure DevOps connector
        ado_connector = ADOConnector(
            organization_url=config["ado_organization"],
            personal_access_token=config["ado_pat"],
        )

        # Initialize embedding service
        embedding_service = EmbeddingService(
            endpoint=config["openai_endpoint"],
            api_key=config["openai_api_key"],
            api_version=config["openai_api_version"],
            deployment_name=config["openai_embedding_deployment"],
        )

        # Initialize search manager
        search_manager = SearchIndexManager(
            endpoint=config["search_endpoint"],
            api_key=config["search_api_key"],
            index_name=config["search_index_name"],
        )

        # Initialize sync manager
        sync_manager = SyncManager(
            ado_connector=ado_connector,
            embedding_service=embedding_service,
            search_manager=search_manager,
            project_name=config["ado_project_name"],
        )

        # Initialize RAG service
        rag_service = RAGService(
            openai_endpoint=config["openai_endpoint"],
            openai_api_key=config["openai_api_key"],
            openai_api_version=config["openai_api_version"],
            chat_deployment_name=config["openai_chat_deployment"],
            embedding_service=embedding_service,
            search_manager=search_manager,
        )

        logger.info("Services initialized successfully")

        return {
            "config": config,
            "sync_manager": sync_manager,
            "rag_service": rag_service,
            "search_manager": search_manager,
        }

    except Exception as e:
        st.error(f"Error initializing services: {str(e)}")
        st.stop()


def perform_sync(sync_manager, force_full=False):
    """Perform synchronization operation."""
    # Check if sync is already in progress
    if st.session_state.get("sync_in_progress", False):
        st.warning("⚠️ Sync is already in progress. Please wait for it to complete.")
        return
    
    # Set sync lock
    st.session_state.sync_in_progress = True
    
    progress_bar = st.progress(0, text="🔄 Starting sync...")
    status_text = st.empty()
    
    def update_progress(step, current, total, message):
        """Update progress bar and status text."""
        progress_pct = int((current / total) * 100) if total > 0 else 0
        progress_bar.progress(progress_pct, text=message)
    
    try:
        start_time = time.time()

        synced_count, total_count = sync_manager.sync(
            force_full_sync=force_full,
            progress_callback=update_progress
        )

        elapsed_time = time.time() - start_time
        progress_bar.progress(100, text="✅ Sync complete!")

        status_text.success(
            f"✅ Sync completed in {elapsed_time:.1f}s\n\n"
            f"- **Items synced**: {synced_count}\n"
            f"- **Total items**: {total_count}"
        )

        # Update session state
        st.session_state.last_sync_time = datetime.now()
        st.session_state.work_item_count = total_count
        st.session_state.sync_completed = True
        
        # Note: Even if metadata update fails, work items are still indexed and searchable

    except Exception as e:
        progress_bar.empty()
        
        # Check if sync completed but only metadata update failed
        if "Edm.DateTimeOffset" in str(e) or "sync metadata" in str(e).lower():
            status_text.warning(
                f"⚠️ Sync completed but metadata update failed\n\n"
                f"Work items were successfully indexed and are searchable.\n"
                f"You can retry sync to update metadata.\n\n"
                f"Error: {str(e)}"
            )
            # Still mark as completed since work items were synced
            st.session_state.sync_completed = True
        else:
            status_text.error(f"❌ Sync failed: {str(e)}")
            logging.getLogger(__name__).error(f"Sync failed: {str(e)}", exc_info=True)
    
    finally:
        # Clear sync lock
        st.session_state.sync_in_progress = False


def check_initial_sync(services):
    """Check if initial sync is needed and perform it."""
    search_manager = services["search_manager"]
    sync_manager = services["sync_manager"]

    # Check if we already performed initial sync in this session
    if st.session_state.get("initial_sync_completed"):
        return

    # Check if index exists and has data
    if not search_manager.index_exists():
        st.info("🔄 Performing initial sync - this may take a few minutes...")
        perform_sync(sync_manager, force_full=True)
        st.session_state.initial_sync_completed = True
        st.rerun()
    else:
        # Check if index has data
        metadata = search_manager.get_sync_metadata()
        if metadata and metadata.get("work_item_count", 0) > 0:
            st.session_state.last_sync_time = datetime.fromisoformat(
                metadata["last_sync_time"].replace("Z", "+00:00")
            )
            st.session_state.work_item_count = metadata["work_item_count"]
            st.session_state.initial_sync_completed = True
        else:
            # Index exists but is empty
            st.info("🔄 Performing initial sync - this may take a few minutes...")
            perform_sync(sync_manager, force_full=True)
            st.session_state.initial_sync_completed = True
            st.rerun()


def render_sidebar(services):
    """Render sidebar with project info and sync controls."""
    config = services["config"]
    sync_manager = services["sync_manager"]

    with st.sidebar:
        st.title("🔍 ADO Work Item Assistant")

        st.markdown("---")

        # Project information
        st.subheader("📊 Project Information")
        st.text(f"Project: {config['ado_project_name']}")

        # Sync status
        if st.session_state.get("last_sync_time"):
            last_sync = st.session_state.last_sync_time
            st.text(f"Last Sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")

        if st.session_state.get("work_item_count"):
            st.text(f"Work Items: {st.session_state.work_item_count}")

        st.markdown("---")

        # Sync controls
        st.subheader("🔄 Sync Controls")
        
        sync_in_progress = st.session_state.get("sync_in_progress", False)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Delta Sync", use_container_width=True, disabled=sync_in_progress):
                perform_sync(sync_manager, force_full=False)
                st.rerun()

        with col2:
            if st.button("🔃 Full Sync", use_container_width=True, disabled=sync_in_progress):
                perform_sync(sync_manager, force_full=True)
                st.rerun()
        
        if sync_in_progress:
            st.info("⏳ Sync in progress... Please wait.")

        st.caption("💡 Delta sync fetches only changed items since last sync")

        st.markdown("---")

        # Help section
        with st.expander("ℹ️ Help"):
            st.markdown("""
            **How to use:**
            1. Ask questions about work items
            2. View relevant work items in responses
            3. Click on work item links to open in ADO
            
            **Example queries:**
            - What bugs are assigned to me?
            - Show me high priority features
            - What's the status of sprint items?
            - Tell me about authentication issues
            """)


def render_chat_interface(services):
    """Render main chat interface."""
    rag_service = services["rag_service"]

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about work items..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                for chunk in rag_service.query(question=prompt, top_k=5):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

            except Exception as e:
                error_message = f"❌ Error: {str(e)}"
                message_placeholder.markdown(error_message)
                full_response = error_message
                logging.error(f"Query error: {e}", exc_info=True)

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})


def main():
    """Main application entry point."""
    # Initialize session state
    if "initial_sync_completed" not in st.session_state:
        st.session_state.initial_sync_completed = False

    # Initialize services
    services = initialize_services()

    # Check and perform initial sync if needed
    check_initial_sync(services)

    # Render UI
    render_sidebar(services)

    # Main content area
    st.title(f"💬 Chat with {services['config']['ado_project_name']} Work Items")

    # Only show chat interface after initial sync
    if st.session_state.get("initial_sync_completed"):
        render_chat_interface(services)
    else:
        st.info("⏳ Initializing... Please wait.")


if __name__ == "__main__":
    main()
