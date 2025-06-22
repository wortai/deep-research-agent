import asyncio
import logging
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()

# Import the classes from your files
from researcher.web_search.web_search import WebSearch
from vectore_store import QdrantService
from vectore_store import VectorStoreManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_research_workflow(query: str, max_web_results: int = 5 , search_queries :List[str] = None ):
    """
    Orchestrates the web search, data loading, and vector store search process.

    Args:
        query (str): The initial web search query.
        max_web_results (int): Maximum number of web search results to process.
    """




    extract_data=[]


    # --- Step 1: Perform Web Search and Data Extraction ---
    logger.info("Initiating web search...")
    web_search = WebSearch(query=query, max_results=max_web_results)
    scraped_data = await web_search.initiate_research() # starting research here 

    if not scraped_data:
        logger.warning("No data scraped from web search. Exiting workflow.")
        return

    logger.info(f"Successfully scraped data from {len(scraped_data)} URLs.")
    # The scraped_data is a list of dicts: [{"url": "...", "content": "..."}, ...]

    # --- Step 2: Initialize Vector Store and Load Data ---
    # logger.info("Initializing Qdrant vector store and loading data...")
    # Use a specific collection name for web documents
    qdrant_service = QdrantService(collection_name="Testing")

    # # Initialize VectorStoreManager with the Qdrant vector store instance
    vector_store_manager = VectorStoreManager(vector_store=qdrant_service.vector_store)

    # Load the scraped data into the vector store
    # The load method expects a list of dicts with 'content' and 'url' keys
    vector_store_manager.load(scraped_data)
    logger.info("Data successfully loaded into the vector store.")

    # --- Step 3: Perform Similarity Searches on the Vector Store ---
    logger.info("Performing similarity searches on the vector store...")






    if search_queries is not None:
        search_queries = search_queries
        logger.info(f"Using provided search query: '{search_queries}'")
    else:
        search_queries = [
            f"What are the key findings about {query}?",
            f"facts realated to {query}",
           
        ]
        logger.info("Using default search queries.")





    for search_query in search_queries:
        logger.info(f"\nSearching vector store for: '{search_query}'")
        # Perform similarity search
        
        vector_search_results = vector_store_manager.similarity_search(query=search_query, k=4) # Get top 4 results

        if vector_search_results:
            logger.info(f"Found {len(vector_search_results)} relevant documents.")
            for doc in vector_search_results:
                
                extract_data.append({
                    "source": doc.metadata.get('source', 'N/A'), 
                    "content": doc.page_content
                })
        else :
            logger.info("No relevant documents found in the vector store for this query.")







    logger.info("Research workflow completed.")
    return extract_data








# --- Example Usage ---
if __name__ == "__main__":
    # Define the initial web search query
    research_query = "latest advancements in large language models"
    search_query = ["Explain the Main advancement in large language models" ,"Recent LLM inovations " , "what major changes happend in large language models "]
    # Run the asynchronous workflow
    data = asyncio.run(run_research_workflow(research_query, max_web_results=5 , search_queries=search_query))
    # this data will have data =[{} ,{} ,{}] where each {}--> contains metadata = source = url , page_content = content 
    # to access loop over it and access for doc in docs : doc.source , doc.content 
    print(data)