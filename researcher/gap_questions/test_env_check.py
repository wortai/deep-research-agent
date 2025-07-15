import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check if required environment variables are set."""
    logger.info("Checking required environment variables...")
    
    required_vars = {
        "OPENAI_API_KEY": "Required for embeddings",
        "QDRANT_URL": "Required for Qdrant connection",
        "QDRANT_API_KEY": "Required for Qdrant authentication",
        "GOOGLE_API_KEY": "Required for web search"
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: {'*' * 10} (set)")
        else:
            logger.warning(f"❌ {var}: Not set ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        return False
    else:
        logger.info("✅ All required environment variables are set")
        return True

def test_qdrant_connection():
    """Test basic Qdrant connection."""
    try:
        logger.info("Testing Qdrant connection...")
        from researcher.vectore_store import QdrantService
        
        # Use a simple test collection
        qdrant_service = QdrantService(collection_name="env_test_collection")
        logger.info("✅ Qdrant connection successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Qdrant connection failed: {e}")
        return False

def test_web_search_import():
    """Test web search import."""
    try:
        logger.info("Testing web search import...")
        from researcher.web_search import WebSearch
        logger.info("✅ Web search import successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Web search import failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Environment and Dependencies Check")
    logger.info("=" * 50)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Test imports and connections
    web_search_ok = test_web_search_import()
    qdrant_ok = test_qdrant_connection()
    
    logger.info("=" * 50)
    logger.info("Summary:")
    logger.info(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    logger.info(f"Web Search Import: {'✅ PASS' if web_search_ok else '❌ FAIL'}")
    logger.info(f"Qdrant Connection: {'✅ PASS' if qdrant_ok else '❌ FAIL'}")
    
    if env_ok and web_search_ok and qdrant_ok:
        logger.info("✅ All checks passed! Ready to test query processor.")
    else:
        logger.error("❌ Some checks failed. Please fix the issues above.")
    
    logger.info("=" * 50)