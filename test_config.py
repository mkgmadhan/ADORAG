"""
Test configuration and validation script for ADO RAG.

Run this script to validate your configuration before starting the application.
"""

import os
import sys
from datetime import datetime

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_status(test_name, passed, message=""):
    """Print test status."""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"      {message}")


def test_python_version():
    """Test Python version."""
    print_header("Python Version Check")
    
    version = sys.version_info
    required = (3, 10)
    passed = version >= required
    
    print_status(
        "Python Version",
        passed,
        f"Found: {version.major}.{version.minor}.{version.micro}, Required: {required[0]}.{required[1]}+"
    )
    
    return passed


def test_environment_variables():
    """Test environment variables."""
    print_header("Environment Variables Check")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "ADO_ORGANIZATION",
        "ADO_PROJECT_NAME",
        "ADO_PAT",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_KEY",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_KEY",
    ]
    
    all_passed = True
    
    for var in required_vars:
        value = os.getenv(var)
        passed = value is not None and value.strip() != ""
        all_passed = all_passed and passed
        
        if passed:
            # Mask sensitive values
            if "KEY" in var or "PAT" in var:
                display = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            else:
                display = value[:50] + "..." if len(value) > 50 else value
            print_status(var, True, display)
        else:
            print_status(var, False, "Not set or empty")
    
    return all_passed


def test_dependencies():
    """Test Python dependencies."""
    print_header("Dependencies Check")
    
    dependencies = [
        "streamlit",
        "azure.devops",
        "azure.search.documents",
        "openai",
        "tiktoken",
        "bs4",
    ]
    
    all_passed = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print_status(dep, True)
        except ImportError as e:
            print_status(dep, False, str(e))
            all_passed = False
    
    return all_passed


def test_ado_connection():
    """Test Azure DevOps connection."""
    print_header("Azure DevOps Connection Test")
    
    try:
        from src.ado_service import ADOConnector
        from src.utils import load_config
        
        config = load_config()
        
        connector = ADOConnector(
            organization_url=config["ado_organization"],
            personal_access_token=config["ado_pat"],
        )
        
        result = connector.test_connection(config["ado_project_name"])
        
        print_status("ADO Connection", result, 
                    f"Project: {config['ado_project_name']}")
        
        return result
        
    except Exception as e:
        print_status("ADO Connection", False, str(e))
        return False


def test_openai_connection():
    """Test Azure OpenAI connection."""
    print_header("Azure OpenAI Connection Test")
    
    try:
        from src.embedding_service import EmbeddingService
        from src.utils import load_config
        
        config = load_config()
        
        service = EmbeddingService(
            endpoint=config["openai_endpoint"],
            api_key=config["openai_api_key"],
            api_version=config["openai_api_version"],
            deployment_name=config["openai_embedding_deployment"],
        )
        
        # Test embedding generation
        embedding = service.generate_embedding("test")
        passed = len(embedding) == 1536
        
        print_status("OpenAI Embedding", passed, 
                    f"Deployment: {config['openai_embedding_deployment']}, Dimension: {len(embedding)}")
        
        # Test chat deployment
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            azure_endpoint=config["openai_endpoint"],
            api_key=config["openai_api_key"],
            api_version=config["openai_api_version"],
        )
        
        response = client.chat.completions.create(
            model=config["openai_chat_deployment"],
            messages=[{"role": "user", "content": "test"}],
            max_tokens=10,
        )
        
        chat_passed = response.choices[0].message.content is not None
        
        print_status("OpenAI Chat", chat_passed,
                    f"Deployment: {config['openai_chat_deployment']}")
        
        return passed and chat_passed
        
    except Exception as e:
        print_status("OpenAI Connection", False, str(e))
        return False


def test_search_connection():
    """Test Azure AI Search connection."""
    print_header("Azure AI Search Connection Test")
    
    try:
        from src.search_service import SearchIndexManager
        from src.utils import load_config
        
        config = load_config()
        
        manager = SearchIndexManager(
            endpoint=config["search_endpoint"],
            api_key=config["search_api_key"],
            index_name=config["search_index_name"],
        )
        
        # Test connection by checking if index exists
        exists = manager.index_exists()
        
        print_status("Search Service", True,
                    f"Index '{config['search_index_name']}' {'exists' if exists else 'will be created'}")
        
        if exists:
            count = manager.get_work_item_count()
            metadata = manager.get_sync_metadata()
            
            if metadata:
                last_sync = metadata.get("last_sync_time")
                print(f"      Last sync: {last_sync}")
                print(f"      Work items: {count}")
        
        return True
        
    except Exception as e:
        print_status("Search Service", False, str(e))
        return False


def test_configuration():
    """Test configuration validation."""
    print_header("Configuration Validation")
    
    try:
        from src.utils import load_config, validate_config
        
        config = load_config()
        result = validate_config(config)
        
        print_status("Config Validation", result)
        
        # Print configuration summary
        print("\nConfiguration Summary:")
        print(f"  ADO Project: {config['ado_project_name']}")
        print(f"  Search Index: {config['search_index_name']}")
        print(f"  Embedding Model: {config['openai_embedding_deployment']}")
        print(f"  Chat Model: {config['openai_chat_deployment']}")
        print(f"  Log Level: {config['log_level']}")
        
        return result
        
    except Exception as e:
        print_status("Config Validation", False, str(e))
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║           ADO RAG Configuration Validator                 ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Configuration", test_configuration()))
    results.append(("ADO Connection", test_ado_connection()))
    results.append(("OpenAI Connection", test_openai_connection()))
    results.append(("Search Connection", test_search_connection()))
    
    # Print summary
    print_header("Test Summary")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        print_status(name, passed)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n✅ All tests passed! You're ready to run the application.")
        print("\nRun: streamlit run app.py")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above before running the application.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
