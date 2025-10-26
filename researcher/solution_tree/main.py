# web_search function that runs retrievers and scrapers over various platforms
# vector_store function - retrieve and upload
import json
import logging
import asyncio
from collections import deque
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
from researcher.solution_tree.utils import dump_query_solution

logging.basicConfig(level=logging.INFO)

class Solver():
    _vector_store_manager = None
    _active_collection = None

    def __init__(self, query, num_web_queries=1, num_vector_queries=1, max_web_results=1, 
                 collection_name="research-documents", batch_size=100, num_gaps_per_node=2):
        self.query = query

        self._initialize_or_reuse_vector_store(collection_name)
        
        self.num_web_queries = num_web_queries
        self.num_vector_queries = num_vector_queries
        self.num_gaps_per_node = num_gaps_per_node

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
        """
        context_by_query = {}
        
        search_results = self.vector_store_manager.batch_similarity_search(
            vector_search_queries, 
            k=5 
        )

        # --- THIS IS THE KEY UPDATE ---
        # We will now process documents to ensure source URLs are unique.
        for query, documents in search_results.items():
            if not documents:
                context_by_query[query] = "No relevant information found."
                continue

            # Use a list for content and a set for unique URLs
            all_content_parts = []
            unique_sources = set()

            for doc in documents:
                all_content_parts.append(doc.page_content)
                source_url = doc.metadata.get('source')
                if source_url:
                    unique_sources.add(source_url)

            # Construct a clean context block with unique sources listed at the top.
            # We sort the list of URLs for consistent, clean output.
            sources_list = sorted(list(unique_sources))
            
            sources_header = "Sources:\n" + "\n".join(f"- {url}" for url in sources_list)
            content_body = "Content:\n" + "\n\n---\n\n".join(all_content_parts)

            context_by_query[query] = f"{sources_header}\n\n{content_body}"
        # --- END OF UPDATE ---

        # The rest of the function remains exactly the same
        prompt = get_gap_analysis_prompt(
            main_query=self.query,
            vector_queries=vector_search_queries,
            context_by_query=context_by_query,
            num_gaps_per_node=self.num_gaps_per_node
        )

        parser = JsonOutputParser()
        
        if hasattr(self.analysis_llm, 'max_tokens'):
            analysis_llm_configured = self.analysis_llm.bind(max_tokens=4000)
        else:
            analysis_llm_configured = self.analysis_llm
        
        chain = analysis_llm_configured | parser

        try:
            logging.info("Invoking Gap Analysis")
            data = chain.invoke(prompt)
            # ... (rest of the function is unchanged)
            main_query = data.get("main_query", self.query)
            query_answers = data.get("query_answers", {})
            gaps = data.get("gaps", [])
            return main_query, query_answers, gaps
        except Exception as e:
            logging.error(f"Error in analyze_gaps: {e}")
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
        dump_query_solution(query, answer, filename="query_solutions.md")
        
        logging.info(f"Resolved query with {len(gaps)} gaps remaining")

        return gaps, answer


class Node:
    """A simple class to represent a node in the research tree."""
    def __init__(self, query: str, depth: int = 0, parent=None):
        self.query = query
        self.depth = depth
        self.parent = parent
        self.children = []
        self.answer = None  # This will be filled by the Solver

def print_tree(node: Node, prefix: str = "", is_last: bool = True):
    """Prints a visual representation of the research tree."""
    print(prefix + ("└── " if is_last else "├── ") + node.query)
    child_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        print_tree(child, child_prefix, is_last_child)

async def step_executor(initial_queries: List[str], max_depth: int = 2, num_gaps_per_node: int = 2):
    """
    Builds and resolves a tree of research queries using a breadth-first approach.
    """
    if not initial_queries:
        return None
    
    # Use the first query as the root of our research tree
    root_node = Node(query=initial_queries[0])
    
    # Initialize a queue with the root node to start the process
    queue = deque([root_node])

    while queue:
        # Dequeue the next node to process
        current_node = queue.popleft()

        print("=" * 40)
        logging.info(f"Resolving Node at Depth {current_node.depth}: '{current_node.query}'")
        print("=" * 40)

        # Stop expanding the tree if the maximum depth is reached
        if current_node.depth >= max_depth:
            logging.info("Max depth reached for this branch. Not generating new gaps.")
            # We don't resolve the final layer, just identify them as leaves
            continue

        try:
            # Use the Solver to resolve the current query
            solver = Solver(query=current_node.query, num_gaps_per_node=num_gaps_per_node)
            gaps, answer = await solver.resolve()
            
            # Store the generated answer in the node
            current_node.answer = answer
            
            logging.info(f"Query resolved. Found {len(gaps)} new child nodes (gaps).")

            # Create child nodes from the identified gaps
            for gap_query in gaps:
                child_node = Node(
                    query=gap_query, 
                    depth=current_node.depth + 1, 
                    parent=current_node
                )
                current_node.children.append(child_node)
                # Enqueue the new children to be processed in the next level
                queue.append(child_node)

        except Exception as e:
            logging.error(f"An error occurred while resolving '{current_node.query}': {e}")
            
    logging.info("Research tree resolution is complete.")
    return root_node

if __name__ == "__main__":
    async def main():
        initial_queries = [
            "Provide a comprehensive comparison between Vision Transformers (ViT) and Convolutional Neural Networks (CNNs) for image classification tasks.",
        ]
        
        # Start the process. Note 'depth' is now 'max_depth'.
        research_tree_root = await step_executor(
            initial_queries, 
            max_depth=2, 
            num_gaps_per_node=2
        )
        
        print("\n" + "=" * 40)
        logging.info("RESEARCH PROCESS COMPLETE")
        print("=" * 40)

        if research_tree_root:
            print("Final Research Tree Structure:")
            print_tree(research_tree_root)
        else:
            print("No research was conducted.")
    
    asyncio.run(main())
    
if __name__ == "__main__":
    async def main():
        # A more detailed initial query often yields better results
        initial_queries = [
            "Provide a comprehensive comparison between Vision Transformers (ViT) and Convolutional Neural Networks (CNNs) for image classification tasks.",
        ]
        
        # Start the process with the initial high-level query
        remaining_gaps = await step_executor(initial_queries, max_depth=2)
        
        print("\n" + "=" * 40)
        logging.info("RESEARCH PROCESS COMPLETE")
        print("=" * 40)

        if remaining_gaps:
            print(f"Final unresolved gaps after {2} iterations: {remaining_gaps}")
        else:
            print("All queries were resolved with no remaining gaps.")
    
    asyncio.run(main())