# external_search_system.py
"""
Black Box External Search System
This file contains all the web search, content extraction, and processing logic.
It can be easily replaced with a different implementation without changing the main GapQueryGenerator.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, unquote
import time
import random
from typing import List, Dict, Optional
import logging

class ExternalSearchSystem:
    """
    External search system interface - can be easily replaced with different implementations
    """
    
    def __init__(self, llm_client, vector_store):
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.logger = logging.getLogger(f"{__class__.__name__}")
        
    def process_query(self, query: str) -> Dict[str, any]:
        """
        Main interface method - implement this in any replacement system
        
        Args:
            query: Search query string
            
        Returns:
            Dict with keys: success, query, sources_found, content_added, summary, error (optional)
        """
        raise NotImplementedError("Subclasses must implement process_query method")
    
    def get_processing_stats(self) -> Dict[str, int]:
        """Get processing statistics"""
        raise NotImplementedError("Subclasses must implement get_processing_stats method")


class RealWebSearchSystem(ExternalSearchSystem):
    """
    Real web search system using DuckDuckGo and web scraping
    """
    
    def __init__(self, llm_client, vector_store):
        super().__init__(llm_client, vector_store)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def process_query(self, query: str) -> Dict[str, any]:
        """
        Main entry point for real web search and processing
        """
        try:
            self.logger.info(f"🌐 Real Web Search: Processing query '{query}'")
            
            # Step 1: Perform actual web search
            search_results = self._search_duckduckgo(query)
            
            if not search_results:
                self.logger.warning("No search results found")
                return {
                    "success": False,
                    "query": query,
                    "error": "No search results found",
                    "summary": f"No results found for query '{query}'"
                }
            
            # Step 2: Extract content from top results
            extracted_content = self._extract_content_from_results(search_results)
            
            # Step 3: Process with LLM for relevance and quality
            processed_content = self._process_with_llm(query, extracted_content)
            
            # Step 4: Update vector store
            self._update_vector_store(query, processed_content)
            
            return {
                "success": True,
                "query": query,
                "sources_found": len(search_results),
                "content_extracted": len(extracted_content),
                "content_added": len(processed_content),
                "summary": f"Found {len(search_results)} sources, extracted and processed {len(processed_content)} relevant pieces of information"
            }
            
        except Exception as e:
            self.logger.error(f"Real Web Search Error: {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "summary": f"Failed to process query '{query}': {str(e)}"
            }
    
    def _search_duckduckgo(self, query: str, max_results: int = 8) -> List[Dict[str, str]]:
        """
        Perform actual web search using DuckDuckGo
        """
        try:
            self.logger.info(f"Searching DuckDuckGo for: {query}")
            
            # DuckDuckGo instant answers API (free, no auth required)
            search_url = "https://html.duckduckgo.com/html/"
            encoded_query = quote_plus(query)
            
            params = {
                'q': encoded_query,
                'b': '',  # Start from first result
                'kl': 'us-en',  # Language
                'df': '',  # Date filter
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse search results
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Find search result containers
            result_containers = soup.find_all('div', {'class': 'result'})
            
            for container in result_containers[:max_results]:
                try:
                    # Extract title
                    title_elem = container.find('a', {'class': 'result__a'})
                    title = title_elem.get_text().strip() if title_elem else "No title"
                    
                    # Extract URL
                    url = title_elem.get('href') if title_elem else None
                    if url and url.startswith('/l/?uddg='):
                        # DuckDuckGo wraps URLs, extract the real URL
                        try:
                            url = url.split('uddg=')[1].split('&')[0]
                            url = unquote(url)
                        except:
                            continue
                    
                    # Extract snippet
                    snippet_elem = container.find('a', {'class': 'result__snippet'})
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                    
                    if url and title:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Error parsing result: {e}")
                    continue
            
            self.logger.info(f"Found {len(results)} search results")
            
            # Add small delay to be respectful
            time.sleep(random.uniform(1, 2))
            
            return results
            
        except Exception as e:
            self.logger.error(f"DuckDuckGo search failed: {e}")
            return []
    
    def _extract_content_from_results(self, search_results: List[Dict[str, str]]) -> List[str]:
        """
        Extract actual content from web pages
        """
        extracted_content = []
        
        for i, result in enumerate(search_results[:5]):  # Limit to top 5 for speed
            try:
                self.logger.info(f"Extracting content from: {result['title'][:50]}...")
                
                # Get the webpage content
                response = self.session.get(result['url'], timeout=10)
                response.raise_for_status()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Extract text content
                text_content = soup.get_text()
                
                # Clean up the text
                lines = (line.strip() for line in text_content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Take first 2000 characters to avoid too much content
                if len(clean_text) > 100:  # Only add if substantial content
                    content_piece = {
                        'source_title': result['title'],
                        'source_url': result['url'],
                        'content': clean_text[:2000] + "..." if len(clean_text) > 2000 else clean_text,
                        'snippet': result['snippet']
                    }
                    extracted_content.append(content_piece)
                
                # Be respectful with delays
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                self.logger.warning(f"Failed to extract from {result.get('url', 'unknown')}: {e}")
                # Fall back to snippet if content extraction fails
                if result['snippet']:
                    content_piece = {
                        'source_title': result['title'],
                        'source_url': result.get('url', ''),
                        'content': result['snippet'],
                        'snippet': result['snippet']
                    }
                    extracted_content.append(content_piece)
                continue
        
        self.logger.info(f"Successfully extracted content from {len(extracted_content)} sources")
        return extracted_content
    
    def _process_with_llm(self, query: str, extracted_content: List[Dict]) -> List[str]:
        """
        Process extracted content with LLM for relevance and quality
        """
        try:
            if not extracted_content:
                return []
            
            self.logger.info(f"Processing {len(extracted_content)} content pieces with LLM...")
            
            # Prepare content for LLM processing
            content_text = ""
            for i, content in enumerate(extracted_content, 1):
                content_text += f"\nSource {i} - {content['source_title']}:\n{content['content']}\n"
            
            prompt = f"""
You are a research assistant processing web search results. Extract the most relevant and factual information that directly answers the query.

QUERY: {query}

WEB CONTENT:
{content_text}

Instructions:
1. Extract only information that directly relates to the query
2. Focus on recent, factual data (numbers, dates, specific claims)
3. Remove marketing language and promotional content
4. Ensure information is current and credible
5. Format as clear, concise bullet points
6. Include source context when relevant

Provide the key insights as bullet points, one insight per line:
"""
            
            response = self.llm_client.generate(prompt)
            
            # Parse response into clean insights
            insights = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    clean_insight = line.lstrip('-•* ').strip()
                    if len(clean_insight) > 30:  # Filter out very short insights
                        insights.append(clean_insight)
            
            self.logger.info(f"LLM extracted {len(insights)} relevant insights")
            return insights[:10]  # Limit to top 10 insights
            
        except Exception as e:
            self.logger.warning(f"LLM processing failed: {e}")
            # Fallback: return cleaned snippets
            fallback = []
            for content in extracted_content:
                if content['snippet'] and len(content['snippet']) > 50:
                    fallback.append(content['snippet'])
            return fallback[:5]
    
    def _update_vector_store(self, query: str, processed_content: List[str]):
        """
        Update vector store with processed content
        """
        try:
            category = self._categorize_content(query)
            
            # Add to vector store
            if hasattr(self.vector_store, 'add_documents'):
                self.vector_store.add_documents(processed_content, category=category)
            else:
                # For our mock vector store
                if category not in self.vector_store.data:
                    self.vector_store.data[category] = []
                
                for content in processed_content:
                    if content not in self.vector_store.data[category]:
                        self.vector_store.data[category].append(content)
            
            self.logger.info(f"Added {len(processed_content)} insights to '{category}' category")
            
        except Exception as e:
            self.logger.warning(f"Vector store update failed: {e}")
    
    def _categorize_content(self, query: str) -> str:
        """Categorize content based on query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['market', 'size', 'revenue', 'funding', 'valuation']):
            return "market_data"
        elif any(word in query_lower for word in ['trend', 'adoption', 'growth', 'forecast']):
            return "trends_analysis"
        elif any(word in query_lower for word in ['regulation', 'policy', 'law', 'compliance']):
            return "regulatory_info"
        elif any(word in query_lower for word in ['company', 'startup', 'competition', 'competitor']):
            return "competitive_landscape"
        elif any(word in query_lower for word in ['technology', 'technical', 'development', 'innovation']):
            return "technology_updates"
        else:
            return "general_ai_info"
    
    def get_processing_stats(self) -> Dict[str, int]:
        """Get processing statistics"""
        total_categories = len(self.vector_store.data)
        total_items = sum(len(items) for items in self.vector_store.data.values())
        
        return {
            "total_categories": total_categories,
            "total_items_stored": total_items,
            "categories": list(self.vector_store.data.keys())
        }


class MockExternalSystem(ExternalSearchSystem):
    """
    Mock external system for testing (fallback when real web search is not available)
    """
    
    def __init__(self, llm_client, vector_store):
        super().__init__(llm_client, vector_store)
        self.search_results_db = self._initialize_mock_web_data()
        
    def _initialize_mock_web_data(self):
        """Simulate a web search results database"""
        return {
            "ai market size 2024": [
                "The global AI market reached $207 billion in 2024, growing 35% year-over-year.",
                "IDC reports AI software market alone was worth $85 billion in 2024.",
                "Generative AI segment accounts for $43 billion of total AI market value.",
                "Enterprise AI adoption increased to 72% of organizations in 2024."
            ],
            "artificial intelligence trends": [
                "Multimodal AI models became mainstream in 2024 with GPT-4V and Gemini Vision.",
                "AI agents and autonomous systems saw 400% growth in enterprise deployments.",
                "Edge AI computing grew 250% as companies prioritize data privacy and latency.",
                "AI regulation frameworks were established in EU, US, and 15 other countries."
            ],
            "machine learning adoption enterprise": [
                "78% of Fortune 500 companies now use ML in production systems.",
                "MLOps platforms market grew to $15.8 billion in 2024.",
                "AutoML adoption increased 180% among non-technical business users.",
                "Real-time ML inference became standard with 95% of new deployments."
            ]
        }
    
    def process_query(self, query: str) -> Dict[str, any]:
        """
        Mock processing that simulates web search results
        """
        try:
            self.logger.info(f"Mock External System: Processing query '{query}'")
            
            # Simulate web search
            raw_search_results = self._simulate_web_search(query)
            
            # Process results with LLM
            processed_content = self._process_with_llm_mock(query, raw_search_results)
            
            # Update vector store
            self._update_vector_store(query, processed_content)
            
            return {
                "success": True,
                "query": query,
                "sources_found": len(raw_search_results),
                "content_added": len(processed_content),
                "summary": f"Mock: Added {len(processed_content)} relevant pieces of information about '{query}'"
            }
            
        except Exception as e:
            self.logger.error(f"Mock External System Error: {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "summary": f"Mock: Failed to process query '{query}'"
            }
    
    def _simulate_web_search(self, query: str) -> List[str]:
        """Simulate web search by finding relevant mock data"""
        query_lower = query.lower()
        results = []
        
        # Find matching data based on keywords
        for search_term, content_list in self.search_results_db.items():
            search_words = search_term.split()
            query_words = query_lower.split()
            
            # Check for keyword overlap
            if any(word in query_words for word in search_words):
                results.extend(content_list)
        
        # If no specific matches, return some general results
        if not results:
            results = [
                f"General information related to '{query}' from mock search simulation.",
                f"Baseline data point for query '{query}' - placeholder content.",
                f"Additional context for '{query}' from simulated search results."
            ]
        
        self.logger.info(f"Mock Web Search: Found {len(results)} raw results")
        return results[:8]  # Limit to top 8 results
    
    def _process_with_llm_mock(self, query: str, raw_results: List[str]) -> List[str]:
        """Mock LLM processing"""
        try:
            # For mock, just return cleaned raw results
            processed_items = []
            for result in raw_results:
                if len(result.strip()) > 20:
                    processed_items.append(result.strip())
            
            self.logger.info(f"Mock LLM Processing: Processed to {len(processed_items)} items")
            return processed_items[:6]  # Limit to top 6 processed items
            
        except Exception as e:
            self.logger.warning(f"Mock LLM Processing failed: {e}")
            return raw_results[:5]
    
    def _update_vector_store(self, query: str, processed_content: List[str]):
        """Update the vector store with new processed content"""
        try:
            # Determine the best category for this content
            category = self._categorize_content(query)
            
            # Add to vector store
            if hasattr(self.vector_store, 'add_documents'):
                self.vector_store.add_documents(processed_content, category=category)
            else:
                # For our mock vector store, directly update the data
                if category not in self.vector_store.data:
                    self.vector_store.data[category] = []
                
                # Add new content, avoiding duplicates
                for content in processed_content:
                    if content not in self.vector_store.data[category]:
                        self.vector_store.data[category].append(content)
            
            self.logger.info(f"Mock: Added {len(processed_content)} items to '{category}' category")
            
        except Exception as e:
            self.logger.warning(f"Mock vector store update failed: {e}")
    
    def _categorize_content(self, query: str) -> str:
        """Categorize content based on query keywords"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['market', 'size', 'revenue', 'funding']):
            return "market_data"
        elif any(word in query_lower for word in ['trend', 'adoption', 'growth']):
            return "trends_analysis"
        elif any(word in query_lower for word in ['regulation', 'policy', 'law']):
            return "regulatory_info"
        elif any(word in query_lower for word in ['company', 'startup', 'competition']):
            return "competitive_landscape"
        elif any(word in query_lower for word in ['technology', 'technical', 'development']):
            return "technology_updates"
        else:
            return "general_ai_info"

    def get_processing_stats(self) -> Dict[str, int]:
        """Get statistics about processing activity"""
        total_categories = len(self.vector_store.data)
        total_items = sum(len(items) for items in self.vector_store.data.values())
        
        return {
            "total_categories": total_categories,
            "total_items_stored": total_items,
            "categories": list(self.vector_store.data.keys())
        }


# Mock Vector Store for demonstration
class MockVectorStore:
    """Simple mock vector store for demonstration"""
    
    def __init__(self):
        self.data = {
            "AI market": [
                "The global AI market was valued at approximately $136 billion in 2022.",
                "Key players include OpenAI, Google, Microsoft, and Meta.",
                "Machine learning segment dominates the market share."
            ],
            "technology trends": [
                "Generative AI is experiencing rapid growth in 2024.",
                "Enterprise adoption of AI increased by 40% in the last year.",
                "Regulation discussions are intensifying globally."
            ]
        }
    
    def search(self, query: str, k: int = 5):
        """Simple keyword-based search simulation"""
        results = []
        query_lower = query.lower()
        
        for category, documents in self.data.items():
            if any(word in category for word in query_lower.split()):
                results.extend(documents[:k])
        
        return results[:k] if results else ["Limited information available in memory store."]
    
    def get_relevant_context(self, query: str, max_items: int = 10):
        """Get relevant context for a query"""
        results = self.search(query, k=max_items)
        return "\n".join(results)


def create_external_system(llm_client, vector_store, use_real_search: bool = True) -> ExternalSearchSystem:
    """
    Factory function to create the appropriate external system
    
    Args:
        llm_client: LLM client for processing
        vector_store: Vector store for content storage
        use_real_search: If True, use real web search; if False, use mock
    
    Returns:
        ExternalSearchSystem instance
    """
    if use_real_search:
        try:
            return RealWebSearchSystem(llm_client, vector_store)
        except ImportError as e:
            logging.warning(f"Real web search dependencies not available: {e}")
            logging.info("Falling back to mock external system")
            return MockExternalSystem(llm_client, vector_store)
    else:
        return MockExternalSystem(llm_client, vector_store)


# Example usage and testing
if __name__ == "__main__":
    # This file can be run independently to test the external system
    import os
    from dotenv import load_dotenv
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage
    
    # Load environment variables
    load_dotenv()
    
    class GeminiLLMClient:
        """LangChain-based Gemini client for external system testing"""
        
        def __init__(self):
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key or api_key == "your_google_api_key_here":
                raise ValueError("Please set GOOGLE_API_KEY in .env file")
            
            # Use Gemini 1.5 Flash for content processing (fast and efficient)
            self.model = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.2
            )
        
        def generate(self, prompt: str) -> str:
            try:
                messages = [HumanMessage(content=prompt)]
                response = self.model.invoke(messages)
                return response.content
            except Exception as e:
                raise Exception(f"Gemini API call failed: {str(e)}")
        
        def complete(self, prompt: str) -> str:
            return self.generate(prompt)
    
    # Test the external system
    print("🧪 Testing External Search System with Gemini")
    print("=" * 60)
    
    try:
        # Initialize Gemini client
        print("📡 Initializing Gemini LLM client...")
        gemini_llm = GeminiLLMClient()
        print("✅ Gemini client initialized")
        
        mock_vector_store = MockVectorStore()
        
        # Test both systems
        for system_name, use_real in [("Mock System", False), ("Real Web Search System", True)]:
            print(f"\n🔧 Testing {system_name}:")
            
            external_system = create_external_system(gemini_llm, mock_vector_store, use_real_search=use_real)
            
            test_query = "AI market size 2024"
            print(f"Processing query: '{test_query}'")
            
            if use_real:
                print("⚠️  This will make actual web requests and may take a few minutes...")
            
            result = external_system.process_query(test_query)
            
            print(f"Success: {result['success']}")
            print(f"Summary: {result['summary']}")
            
            if result['success']:
                print(f"Sources found: {result.get('sources_found', 0)}")
                print(f"Content added: {result.get('content_added', 0)}")
            
            stats = external_system.get_processing_stats()
            print(f"Vector store stats: {stats}")
            print("-" * 40)
            
            # Only test first system if no API key
            if not os.getenv("GOOGLE_API_KEY"):
                break
    
    except ValueError as e:
        print(f"⚠️  Configuration Error: {e}")
        print("\n🔄 Running with Mock LLM client instead...")
        
        # Fallback Mock LLM Client
        class MockLLMClient:
            def generate(self, prompt):
                if "research assistant processing web search results" in prompt.lower():
                    return """- Global AI market reached $207 billion in 2024 with 35% growth
- Enterprise AI adoption increased to 72% of organizations  
- Generative AI segment accounts for $43 billion market value
- MLOps platforms market grew to $15.8 billion
- AI startup funding totaled $42 billion globally"""
                else:
                    return "Mock LLM response for testing"
            
            def complete(self, prompt):
                return self.generate(prompt)
        
        mock_llm = MockLLMClient()
        mock_vector_store = MockVectorStore()
        
        # Test with mock LLM
        print("🔧 Testing with Mock LLM:")
        external_system = create_external_system(mock_llm, mock_vector_store, use_real_search=False)
        
        test_query = "AI market size 2024"
        result = external_system.process_query(test_query)
        
        print(f"Query: {test_query}")
        print(f"Success: {result['success']}")
        print(f"Summary: {result['summary']}")
        
        stats = external_system.get_processing_stats()
        print(f"Stats: {stats}")
        
        print("\n💡 To use Gemini:")
        print("   1. Set GOOGLE_API_KEY in your .env file")
        print("   2. Run this script again")
    
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    print("\n✅ External system testing complete!")