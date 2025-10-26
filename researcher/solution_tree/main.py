# web_search function that runs retrievers and scrapers over various platforms
# vector_store function - retrieve and upload
import json
import logging
from typing import List
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from llms import LlmsHouse
from researcher.solution_tree.prompts import (
    get_web_search_queries_prompt,
    get_vector_search_queries_prompt,
    get_gap_analysis_prompt
)
from researcher.web_search import WebSearch
from researcher.vectore_store.vector_store import VectorStoreManager  # Import the VectorStoreManager
from researcher.vectore_store.qdrant_db import QdrantService  # Import QdrantService for initialization

logging.basicConfig(level=logging.INFO)

class Solver():
    _vector_store_manager = None
    _active_collection = None

    def __init__(self, query, num_web_queries=1, num_vector_queries=5, max_web_results=1, 
                 collection_name="research-documents", batch_size=100):
        self.query = query

        self._initialize_or_reuse_vector_store(collection_name)
        
        self.num_web_queries = num_web_queries
        self.num_vector_queries = num_vector_queries

        self.max_results = max_web_results # Web Results
        self.batch_size = batch_size
        self.collection_name = collection_name

        # --- The Optimal Change: Assigning a team of specialized LLMs ---
        # 1. Best for creating keyword-based search queries
        self.web_search_llm = LlmsHouse.google_model("gemini-2.0-flash-001")
        
        # 2. Best for understanding semantics and creating conceptual queries
        self.vector_search_llm = LlmsHouse.google_model("gemini-2.0-flash-001")
        
        # 3. Best for rigorous, context-bound analysis and reasoning
        self.analysis_llm = LlmsHouse.google_model("gemini-2.0-flash-001")

    def _invoke_and_log(self, llm, prompt, operation_name):
        """Invoke LLM and log the operation."""
        logging.info(f"Invoking {operation_name}")
        response = llm.invoke(prompt)
        logging.info(f"{operation_name} completed")
        return response

    @classmethod
    def _initialize_or_reuse_vector_store(cls, collection_name):
        """
        Check if vector store is already initialized with the same collection.
        If yes, reuse it. If no, initialize a new one.
        """
        try:
            # Check if vector store is already initialized with the same collection
            if cls._vector_store_manager is not None and cls._active_collection == collection_name:
                logging.info(f"Reusing existing vector store with collection: {collection_name}")
                return
            
            # If collection name is different, reinitialize
            if cls._active_collection != collection_name:
                logging.info(f"Switching from collection '{cls._active_collection}' to '{collection_name}'")
            
            # Initialize new vector store
            logging.info(f"Initializing vector store with collection: {collection_name}")
            qdrant_service = QdrantService(collection_name)
            cls._vector_store_manager = VectorStoreManager(qdrant_service.vector_store)
            cls._active_collection = collection_name
            logging.info(f"Vector store successfully initialized for collection: {collection_name}")
            
        except Exception as e:
            logging.error(f"Failed to initialize vector store: {e}")
            cls._vector_store_manager = None
            cls._active_collection = None

    @property
    def vector_store_manager(self):
        """Property to access the class-level vector store manager."""
        return Solver._vector_store_manager
    
    @classmethod
    def clear_vector_store(cls):
        """Clear the cached vector store (useful for testing or resetting)."""
        cls._vector_store_manager = None
        cls._active_collection = None
        logging.info("Vector store cache cleared")

    def dump_query_solution(self, query: str, answer: str, filename: str = "query_solutions.md"):
        """
        Append query and solution to a markdown document.
        Creates the file if it doesn't exist, appends if it does.
        
        Args:
            query: The original query/question
            answer: The generated answer/solution
            filename: Output filename (default: query_solutions.md)
        """
        try:
            # Create markdown formatted content
            content = f"""
            ## Query
            {query}

            ## Solution
            {answer}

            ---

            """
            
            # Append to file (create if doesn't exist)
            with open(filename, "a") as f:
                f.write(content)
            
            logging.info(f"Query and solution appended to {filename}")
            
        except Exception as e:
            logging.error(f"Failed to dump query solution to {filename}: {e}")


    def create_web_search_queries(self):
        parser = JsonOutputParser()
        chain = self.web_search_llm | parser

        prompt = get_web_search_queries_prompt(self.query, self.num_web_queries)
        
        try:
            data = chain.invoke(prompt)
            return data.get("queries", [])
        except OutputParserException as e:
            print("Error: Failed to decode JSON from web search query generation.", e)
            return []
        

    # def retrieve_store_content(self, web_search_queries: list):
    #     for query in web_search_queries:
    #         content = web_search(query) # I wanna see this content in a text file.
    #         self.vector_store.upload(content)

    async def retrieve_store_content(self, web_search_queries: List[str]):
        """
        Retrieve content from web using WebSearch class and store in vector store using VectorStoreManager.
        Uses async to handle multiple queries efficiently with batch optimization.
        """
        all_web_content = []
        documents_to_upload = []
        
        if not self.vector_store_manager:
            logging.error("Vector store manager not initialized. Cannot store content.")
            return all_web_content
        
        for query in web_search_queries:
            try:
                logging.info(f"Starting web search for query: {query}")
                
                # Initialize WebSearch with the query
                web_search = WebSearch(query=query, max_results=self.max_results)
                
                # Execute the async research
                results = await web_search.initiate_research()
                
                logging.info(f"Retrieved {len(results)} results for query: {query}")
                
                # Process and prepare results for batch upload
                if results:
                    for result in results:
                        # Prepare document in the format expected by VectorStoreManager
                        document = {
                            "content": result['content'],
                            "url": result['url']
                        }
                        documents_to_upload.append(document)
                        all_web_content.append(result['content'])
            
                
            except Exception as e:
                logging.error(f"Error during web search for query '{query}': {e}")
        
        # Batch upload all documents to vector store with optimization
        if documents_to_upload:
            try:
                logging.info(f"Uploading {len(documents_to_upload)} documents to vector store in batches...")
                success = self.vector_store_manager.load_batch_optimized(
                    documents_to_upload,
                    batch_size=self.batch_size
                )
                if success:
                    logging.info(f"Successfully uploaded {len(documents_to_upload)} documents to vector store")
                else:
                    logging.warning("Batch upload completed with warnings")
            except Exception as e:
                logging.error(f"Failed to upload documents to vector store: {e}")
        
        return all_web_content

    def create_vector_search_queries(self):
        parser = JsonOutputParser()
        chain = self.vector_search_llm | parser

        prompt = get_vector_search_queries_prompt(self.query, self.num_vector_queries)

        try:
            data = chain.invoke(prompt)
            return data.get("queries", [])
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON from vector search query generation.")
            return []
        
    def analyze_gaps(self, vector_search_queries):
        """
        Analyzes whether vector search results are sufficient to answer the main query.
        
        Returns:
            Tuple of (main_query, query_answers_dict, gaps_list)
        """
        # Store context organized by query
        context_by_query = {}
        
        # Use the VectorStoreManager's batch_similarity_search method
        search_results = self.vector_store_manager.batch_similarity_search(
            vector_search_queries, 
            k=4
        )

        # Extract page_content from LangChain Document objects, organized by query
        for query, documents in search_results.items():
            # Combine all documents for this query
            query_contexts = [doc.page_content for doc in documents]
            context_by_query[query] = "\n\n".join(query_contexts) if query_contexts else "No relevant information found."

        # Create the prompt
        prompt = get_gap_analysis_prompt(
            main_query=self.query,
            vector_queries=vector_search_queries,
            context_by_query=context_by_query
        )

        # Set up parser and chain with increased max_tokens
        parser = JsonOutputParser()
        
        # Configure LLM with higher token limit if using OpenAI
        if hasattr(self.analysis_llm, 'max_tokens'):
            analysis_llm_configured = self.analysis_llm.bind(max_tokens=4000)  # Increase from default
        else:
            analysis_llm_configured = self.analysis_llm
        
        chain = analysis_llm_configured | parser

        try:
            # Invoke the chain
            logging.info("Invoking Gap Analysis")
            data = chain.invoke(prompt)
            logging.info("Gap Analysis completed")
            
            # Extract the three components
            main_query = data.get("main_query", self.query)
            query_answers = data.get("query_answers", {})
            gaps = data.get("gaps", [])
            
            # Validate the response
            if not isinstance(query_answers, dict):
                logging.error("query_answers is not a dictionary")
                query_answers = {}
            
            if not isinstance(gaps, list):
                logging.error("gaps is not a list")
                gaps = []
            
            return main_query, query_answers, gaps
        
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from gap analysis: {e}")
            return self.query, {}, []
        
        except Exception as e:
            logging.error(f"Unexpected error in analyze_gaps: {e}")
            return self.query, {}, []
    
    async def resolve(self):
        """
        Main resolution pipeline using web search and vector store.
        Saves query-solution pairs to a single document.
        """
        # Step 1: Generate web search queries
        web_search_queries = self.create_web_search_queries()
        logging.info(f"Generated web search queries: {web_search_queries}")
        
        # Step 2: Execute web searches and store content
        web_content = await self.retrieve_store_content(web_search_queries)
        logging.info(f"Retrieved {len(web_content)} web content items")
        
        # Step 3: Generate vector search queries
        vector_search_queries = self.create_vector_search_queries()
        logging.info(f"Generated vector search queries: {vector_search_queries}")
        
        # Step 4: Analyze gaps using vector store
        query, answer, gaps = self.analyze_gaps(vector_search_queries)

        # Step 5: Dump query and solution to document
        self.dump_query_solution(query, answer, filename="query_solutions.md")
        
        logging.info(f"Resolved query with {len(gaps)} gaps remaining")

        return gaps, answer


async def step_executor(unresolved: List[str], depth=2):
    """Execute resolution for multiple unresolved queries."""
    for iteration in range(depth):
        logging.info(f"Executing iteration {iteration + 1} of {depth}")
        new_unresolved = []

        for query in unresolved:
            try:
                solver = Solver(query=query)  # ✅ Pass query
                gaps, answer = await solver.resolve()  # ✅ Await async call
                
                logging.info(f"Query '{query}' resolved with {len(gaps)} gaps")
                
                if gaps:
                    new_unresolved.extend(gaps)
            except Exception as e:
                logging.error(f"Error resolving '{query}': {e}")
                new_unresolved.append(query)

        unresolved = new_unresolved
        if not unresolved:
            break

    return unresolved
    
if __name__ == "__main__":
    import asyncio
    
    async def main():
        queries = [
            "What is quantum computing?",
        ]
        remaining_gaps = await step_executor(queries, depth=2)
        print(f"Remaining gaps: {remaining_gaps}")
    
    asyncio.run(main())