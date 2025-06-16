# gap_question_generator.py
"""
Gap Question Generator System using LangGraph
This is the main system that orchestrates gap detection and query generation.
The external search system is imported and can be easily replaced.
"""

from typing import List, Dict, Tuple, Optional
from collections import deque
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# LangChain imports for Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# LangGraph imports (only what we need)
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

# Import external system (can be easily replaced)
from gap_questions.external_search_system import create_external_system, MockVectorStore

# Load environment variables from .env file
load_dotenv()

class StopCondition(Enum):
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    CONFIDENCE_THRESHOLD_MET = "confidence_threshold_met"
    QUEUE_EMPTY = "queue_empty"

@dataclass
class CompletionCheckResult:
    is_complete: bool
    confidence_score: float
    missing_aspects: List[str]
    completeness_percentage: float

# Simple state for LangGraph orchestrator
class OrchestratorState(dict):
    current_iteration: int
    should_continue: bool
    stop_condition: Optional[StopCondition]

class GeminiLLMClient:
    """LangChain-based Gemini client with model selection for different tasks"""
    
    def __init__(self, api_key: str = None):
        # Load from .env file first, then fallback to parameter or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key or self.api_key == "your_google_api_key_here":
            raise ValueError(
                "Google API key is required. Please set GOOGLE_API_KEY in your .env file.\n"
                "You can get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        # Different models for different tasks
        self.thinking_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-thinking-exp",  # Best for complex reasoning
            google_api_key=self.api_key,
            temperature=0.1
        )
        
        self.analysis_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",  # Good for analysis tasks
            google_api_key=self.api_key,
            temperature=0.2
        )
        
        self.generation_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Fast for generation tasks
            google_api_key=self.api_key,
            temperature=0.3
        )
    
    def _select_model(self, prompt: str):
        """Select the best Gemini model based on the prompt type"""
        prompt_lower = prompt.lower()
        
        # Use thinking model for complex analysis and reasoning
        if any(keyword in prompt_lower for keyword in [
            "analyze", "determine", "reasoning", "complex", "evaluate", "assess"
        ]):
            return self.thinking_model
        
        # Use analysis model for detailed content analysis
        elif any(keyword in prompt_lower for keyword in [
            "can_answer", "missing_info", "content analysis", "query resolution"
        ]):
            return self.analysis_model
        
        # Use generation model for creating queries and simple tasks
        else:
            return self.generation_model
    
    def generate(self, prompt: str) -> str:
        """Generate response using appropriate Gemini model"""
        try:
            model = self._select_model(prompt)
            messages = [HumanMessage(content=prompt)]
            response = model.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
    
    def complete(self, prompt: str) -> str:
        """Alias for generate to support different interfaces"""
        return self.generate(prompt)

class GapQuestionGenerator:
    def __init__(
        self,
        llm_client,  # Your LLM client (OpenAI, Anthropic, etc.)
        user_query: str, # Initial User Query
        memory, # Memory of Research Agent
        max_iterations: int = 5,
        confidence_threshold: float = 0.85,
        improvement_threshold: float = 0.05,
        use_real_search: bool = True  # Toggle between real and mock search
    ):
        # Core components
        self.llm_client = llm_client
        self.user_query = user_query
        self.memory = memory
        self.use_real_search = use_real_search
        
        # Configuration parameters
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold
        self.improvement_threshold = improvement_threshold
        
        # State management
        self.gap_query_queue = deque()
        self.processed_queries = []
        self.unresolved_queries = []
        
        # Tracking and metrics
        self.current_iteration = 0
        self.confidence_history = []
        self.current_confidence = 0.0
        self.previous_confidence = 0.0
        
        # Execution state
        self.is_running = False
        self.stop_condition = None
        self.execution_results = {
            'total_gaps_identified': 0,
            'gaps_resolved': 0,
            'gaps_remaining': 0,
            'queries_processed': 0,
            'final_confidence': 0.0,
            'iterations_completed': 0,
            'external_system_calls': 0,
            'content_items_added': 0,
            'sources_processed': 0
        }
        
        # Error handling
        self.error_count = 0
        self.max_errors = 10
        self.last_error = None
        
        # Logging setup
        self.logger = logging.getLogger(f"{__class__.__name__}")
        
        # Session metadata
        self.session_id = f"gap_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.created_at = datetime.now()
        
        # LangGraph orchestrator (only for main workflow)
        self.checkpointer = MemorySaver()
        self.orchestrator = self._build_orchestrator()
        
        # External system will be initialized on first use
        self.external_system = None
        
        # Validation
        self._validate_initialization()
        
        self.logger.info(f"GapQuestionGenerator initialized with session_id: {self.session_id}")

    def _validate_initialization(self):
        """Validate initialization parameters"""
        if not self.llm_client:
            raise ValueError("LLM client cannot be None")
        
        if not self.user_query or not self.user_query.strip():
            raise ValueError("User query cannot be empty")
        
        if not self.memory:
            raise ValueError("Memory component cannot be None")
        
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        
        if not 0 < self.confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        
        if self.improvement_threshold < 0:
            raise ValueError("improvement_threshold must be non-negative")
        
        self.logger.info("Initialization validation passed")

    def _get_external_system(self):
        """Lazy initialization of external system"""
        if self.external_system is None:
            self.external_system = create_external_system(
                self.llm_client, 
                self.memory, 
                use_real_search=self.use_real_search
            )
            system_type = "Real Web Search" if self.use_real_search else "Mock"
            self.logger.info(f"{system_type} external system initialized")
        return self.external_system

    def generate_gap_queries(self, max_questions: int = 5) -> List[str]:
        """
        This function first analyzes what are the gaps in the search query and plan w.r.t current memory
        and then, generates the queries that aim to resolve the gap questions directly by running them through retrievers and scrapers.

        Consider:
        1. Plan
        2. User Query
        3. Memory
        4. How Many Gap Questions?
        5. LLM Client
        
        Output: List of Gap Queries (That could be directly searched over the web to get results i.e. Web Optimized)
        """
        try:
            self.logger.info(f"Generating gap queries, max_questions: {max_questions}")
            
            # Get current memory context
            memory_context = self._get_memory_summary()
            
            # Check if we can answer with current memory
            can_answer, missing_info = self._attempt_query_resolution(memory_context)
            
            if can_answer:
                self.logger.info("Query can be fully answered with existing memory content")
                return []
            
            # Generate gap queries for missing information
            gap_queries = self._generate_queries_for_missing_info(missing_info, max_questions)
            
            # Optimize queries for web search
            optimized_queries = self._optimize_queries_for_web_search(gap_queries)
            
            # Limit and prioritize queries
            final_queries = self._prioritize_and_limit_queries(optimized_queries, max_questions)
            
            # Add to queue for processing
            for query in final_queries:
                self.gap_query_queue.append(query)
            
            # Update tracking
            self.execution_results['total_gaps_identified'] += len(final_queries)
            
            self.logger.info(f"Generated {len(final_queries)} gap queries")
            return final_queries
            
        except Exception as e:
            self._handle_error(f"Error generating gap queries: {str(e)}")
            return []

    def check_gap_elimination(self, max_retry=3):
        """
        This function sees if after the gap query execution, and memory updation the gap queries are resolved or not
        by cross verifying the new updations and summarized earlier memory.

        Consider:
        1. Memory
        2. List of earlier Gap Queries
        
        Output: List of Gap Queries Unresolved -> to call execution of gap_query again with {max_tries}
        """
        try:
            self.logger.info("Checking gap elimination...")
            
            if not self.processed_queries:
                return []
            
            # Get updated memory context
            updated_memory = self._get_memory_summary()
            
            # Check each processed query against updated memory
            unresolved = []
            for query in self.processed_queries:
                if not self._is_query_resolved(query, updated_memory):
                    unresolved.append(query)
            
            self.unresolved_queries = unresolved
            self.execution_results['gaps_resolved'] = len(self.processed_queries) - len(unresolved)
            self.execution_results['gaps_remaining'] = len(unresolved)
            
            self.logger.info(f"Gap elimination check: {len(unresolved)} queries remain unresolved")
            return unresolved
            
        except Exception as e:
            self._handle_error(f"Error in gap elimination check: {str(e)}")
            return self.processed_queries  # Assume all unresolved on error

    def check_query_completeness(self) -> CompletionCheckResult:
        """
        Check if the gap_query queue is empty first
        Then tries to check if each part of the query can be answered.
        """
        try:
            self.logger.info("Checking query completeness...")
            
            # First check if queue is empty
            if self.gap_query_queue:
                return CompletionCheckResult(
                    is_complete=False,
                    confidence_score=self.current_confidence,
                    missing_aspects=list(self.gap_query_queue),
                    completeness_percentage=0.0
                )
            
            # Get current memory and attempt full query resolution
            memory_context = self._get_memory_summary()
            can_answer, missing_aspects = self._attempt_query_resolution(memory_context)
            
            if can_answer:
                completeness = 100.0
                confidence = 0.95
            else:
                completeness = max(0.0, 100.0 - (len(missing_aspects) * 20))  # Rough estimation
                confidence = completeness / 100.0
            
            self.current_confidence = confidence
            self.confidence_history.append(confidence)
            
            result = CompletionCheckResult(
                is_complete=can_answer,
                confidence_score=confidence,
                missing_aspects=missing_aspects,
                completeness_percentage=completeness
            )
            
            self.logger.info(f"Completeness check: {completeness}% complete, confidence: {confidence}")
            return result
            
        except Exception as e:
            self._handle_error(f"Error in completeness check: {str(e)}")
            return CompletionCheckResult(
                is_complete=False,
                confidence_score=0.0,
                missing_aspects=["Error in completeness check"],
                completeness_percentage=0.0
            )

    def check_stop_conditions(
        self,
        current_iteration: int,
        current_confidence: float,
        previous_confidence: float
    ) -> Tuple[bool, StopCondition]:
        """
        This function checks if GapQuestionGenerator should stop its execution or continue
        """
        # Check max iterations
        if current_iteration >= self.max_iterations:
            return True, StopCondition.MAX_ITERATIONS_REACHED
        
        # Check confidence threshold
        if current_confidence >= self.confidence_threshold:
            return True, StopCondition.CONFIDENCE_THRESHOLD_MET
        
        # Check if queue is empty
        if not self.gap_query_queue and not self.unresolved_queries:
            return True, StopCondition.QUEUE_EMPTY
        
        # Continue execution
        return False, None

    def state_manager(self):
        """
        THIS FUNCTION EXPLICITLY USES A QUEUE TO MANAGE THE GAP QUESTIONS 
        (To Pass the Gap Query to Retrievers and Scrapers to eventually update the memory: POP from Queue)
        This function manages the state of Gap Question Generator, 
        Keeping a Queue of Gap Questions.
        """
        try:
            self.logger.info("Managing gap query queue...")
            
            if not self.gap_query_queue:
                self.logger.info("Gap query queue is empty")
                return None
            
            # Pop query from queue
            current_query = self.gap_query_queue.popleft()
            self.logger.info(f"Processing gap query: {current_query}")
            
            # Pass to external system (BLACK BOX CALL - easily replaceable)
            self._pass_query_to_external_system(current_query)
            
            # Move to processed queries
            self.processed_queries.append(current_query)
            self.execution_results['queries_processed'] += 1
            
            return current_query
            
        except Exception as e:
            self._handle_error(f"Error in state management: {str(e)}")
            return None

    def _pass_query_to_external_system(self, query: str):
        """
        MAIN INTERFACE TO BLACK BOX SYSTEM
        This is the only method that calls the external system.
        Replace this call to switch to a different external system.
        """
        try:
            self.logger.info(f"🔗 Passing query to external system: {query}")
            
            # Get external system (lazy initialization)
            external_system = self._get_external_system()
            
            # BLACK BOX CALL - This is what you'll replace in production
            result = external_system.process_query(query)
            
            if result["success"]:
                self.logger.info(f"✅ External system success: {result['summary']}")
                
                # Update tracking with external system results
                self.execution_results['external_system_calls'] += 1
                self.execution_results['content_items_added'] += result.get('content_added', 0)
                self.execution_results['sources_processed'] += result.get('sources_found', 0)
                
            else:
                self.logger.warning(f"❌ External system failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error calling external system: {str(e)}")
            self.logger.info(f"⚠️ External system unavailable, query '{query}' queued for retry")

    # LangGraph orchestrator (simple workflow)
    def _build_orchestrator(self):
        """Build simple LangGraph orchestrator for main workflow"""
        graph = StateGraph(OrchestratorState)
        
        graph.add_node("generate_gaps", self._orchestrator_generate_gaps)
        graph.add_node("process_queue", self._orchestrator_process_queue)
        graph.add_node("check_completion", self._orchestrator_check_completion)
        graph.add_node("check_elimination", self._orchestrator_check_elimination)
        
        # Simple linear flow with conditional continuation
        graph.add_edge(START, "generate_gaps")
        graph.add_edge("generate_gaps", "process_queue")
        graph.add_edge("process_queue", "check_elimination")
        graph.add_edge("check_elimination", "check_completion")
        
        # Conditional edge for continuation
        graph.add_conditional_edges(
            "check_completion",
            self._should_continue,
            {
                "continue": "generate_gaps",
                "stop": END
            }
        )
        
        return graph.compile(checkpointer=self.checkpointer)

    def _orchestrator_generate_gaps(self, state: OrchestratorState) -> OrchestratorState:
        """Generate gap queries step in orchestrator"""
        if state["current_iteration"] == 0:
            # First iteration - generate initial gaps
            self.generate_gap_queries()
        else:
            # Subsequent iterations - generate gaps for unresolved queries
            if self.unresolved_queries:
                for query in self.unresolved_queries:
                    self.gap_query_queue.append(query)
        
        return state

    def _orchestrator_process_queue(self, state: OrchestratorState) -> OrchestratorState:
        """Process all queries in queue"""
        while self.gap_query_queue:
            self.state_manager()
        return state

    def _orchestrator_check_elimination(self, state: OrchestratorState) -> OrchestratorState:
        """Check gap elimination"""
        self.check_gap_elimination()
        return state

    def _orchestrator_check_completion(self, state: OrchestratorState) -> OrchestratorState:
        """Check completion and update state"""
        completion_result = self.check_query_completeness()
        
        state["current_iteration"] += 1
        self.current_iteration = state["current_iteration"]
        
        # Check stop conditions
        should_stop, stop_condition = self.check_stop_conditions(
            state["current_iteration"],
            completion_result.confidence_score,
            self.previous_confidence
        )
        
        state["should_continue"] = not should_stop
        state["stop_condition"] = stop_condition
        
        self.previous_confidence = self.current_confidence
        self.stop_condition = stop_condition
        
        return state

    def _should_continue(self, state: OrchestratorState) -> str:
        """Determine if orchestrator should continue"""
        return "stop" if not state["should_continue"] else "continue"

    def run(self) -> Dict:
        """
        The main orchestrator function
        This function is responsible to maintain the flow of Gap Question Generator
        This function uses the state manager's queue to pass the queries to update the memory.
        """
        try:
            self.logger.info("Starting Gap Question Generator execution...")
            self.is_running = True
            
            # Initialize orchestrator state
            initial_state = {
                "current_iteration": 0,
                "should_continue": True,
                "stop_condition": None
            }
            
            # Run the LangGraph orchestrator
            config = {"configurable": {"thread_id": self.session_id}}
            final_state = self.orchestrator.invoke(initial_state, config)
            
            # Update final execution results
            self.execution_results['iterations_completed'] = final_state["current_iteration"]
            self.execution_results['final_confidence'] = self.current_confidence
            
            self.is_running = False
            
            self.logger.info(f"Gap Question Generator completed. Stop condition: {self.stop_condition}")
            return self.execution_results
            
        except Exception as e:
            self._handle_error(f"Error in main execution: {str(e)}")
            self.is_running = False
            return self.execution_results

    # Helper methods for LLM interactions and processing
    def _get_memory_summary(self) -> str:
        """Extract relevant context from memory store"""
        try:
            if hasattr(self.memory, 'get_relevant_context'):
                return self.memory.get_relevant_context(self.user_query, max_items=10)
            elif hasattr(self.memory, 'search'):
                results = self.memory.search(self.user_query, k=5)
                return "\n".join([str(result) for result in results])
            else:
                return str(self.memory)[:1000] if self.memory else "No memory context available"
        except Exception as e:
            self.logger.warning(f"Could not extract memory context: {str(e)}")
            return "Memory context unavailable"

    def _attempt_query_resolution(self, memory_content: str) -> Tuple[bool, List[str]]:
        """Attempt to resolve user query with existing memory content"""
        prompt = f"""
Analyze if the provided content can answer the user's query.

USER QUERY: {self.user_query}
CONTENT: {memory_content}

Respond: CAN_ANSWER: [YES/NO]
MISSING_INFO: [List missing info, one per line, or "None"]
"""
        
        try:
            response = self._call_llm(prompt)
            lines = response.strip().split('\n')
            can_answer = False
            missing_info = []
            
            for line in lines:
                if line.startswith('CAN_ANSWER:'):
                    can_answer = line.split(':', 1)[1].strip().upper() == 'YES'
                elif line.startswith('MISSING_INFO:'):
                    info = line.split(':', 1)[1].strip()
                    if info.lower() != 'none':
                        missing_info.append(info)
                elif line.strip() and missing_info:
                    missing_info.append(line.strip())
            
            return can_answer, missing_info
        except Exception as e:
            self.logger.warning(f"Error in query resolution: {str(e)}")
            return False, ["Unable to determine missing information"]

    def _generate_queries_for_missing_info(self, missing_info: List[str], max_questions: int) -> List[str]:
        """Generate web search queries for missing information"""
        if not missing_info:
            return []
        
        prompt = f"""
Generate web search queries for missing information:

USER QUERY: {self.user_query}
MISSING: {chr(10).join([f"- {info}" for info in missing_info])}

Generate up to {max_questions} web-optimized queries (one per line):
"""
        
        try:
            response = self._call_llm(prompt)
            queries = []
            for line in response.strip().split('\n'):
                line = line.strip().lstrip('- •*0123456789.)').strip()
                if line and len(line) > 3:
                    queries.append(line)
            return queries
        except Exception as e:
            self.logger.warning(f"Error generating queries: {str(e)}")
            return []

    def _optimize_queries_for_web_search(self, queries: List[str]) -> List[str]:
        """Optimize queries for web search engines"""
        optimized = []
        for query in queries:
            optimized_query = query.lower().strip()
            words = optimized_query.split()
            
            # Remove leading question words
            if words and words[0] in ['what', 'how', 'why', 'when', 'where', 'who', 'which']:
                if len(words) > 3:
                    words = words[1:]
                    optimized_query = ' '.join(words)
            
            optimized_query = optimized_query.replace('?', '').replace('!', '')
            optimized_query = ' '.join(optimized_query.split())
            
            if 3 <= len(optimized_query) <= 100:
                optimized.append(optimized_query)
        
        return optimized

    def _prioritize_and_limit_queries(self, queries: List[str], max_questions: int) -> List[str]:
        """Prioritize and limit queries to max_questions"""
        if len(queries) <= max_questions:
            return queries
        
        # Remove duplicates and sort by length (shorter often better for web search)
        unique_queries = []
        seen = set()
        
        for query in queries:
            normalized = query.lower().strip()
            if normalized not in seen:
                unique_queries.append(query)
                seen.add(normalized)
        
        unique_queries.sort(key=len)
        return unique_queries[:max_questions]

    def _is_query_resolved(self, query: str, updated_memory: str) -> bool:
        """Check if a specific query is resolved with updated memory"""
        prompt = f"""
Can this query be answered with the provided information?

QUERY: {query}
INFORMATION: {updated_memory}

Answer: YES or NO
"""
        
        try:
            response = self._call_llm(prompt)
            return response.strip().upper().startswith('YES')
        except:
            return False

    def _call_llm(self, prompt: str) -> str:
        """Call LLM with error handling"""
        try:
            if hasattr(self.llm_client, 'generate'):
                response = self.llm_client.generate(prompt)
            elif hasattr(self.llm_client, 'complete'):
                response = self.llm_client.complete(prompt)
            elif callable(self.llm_client):
                response = self.llm_client(prompt)
            else:
                raise ValueError("Unknown LLM client interface")
            
            if hasattr(response, 'text'):
                return response.text
            elif isinstance(response, str):
                return response
            else:
                return str(response)
        except Exception as e:
            raise Exception(f"LLM call failed: {str(e)}")

    def _handle_error(self, error_message: str):
        """Handle errors with logging and tracking"""
        self.error_count += 1
        self.last_error = error_message
        self.logger.error(error_message)
        
        if self.error_count >= self.max_errors:
            self.logger.critical(f"Maximum error count ({self.max_errors}) reached")
            raise Exception(f"Too many errors encountered: {error_message}")


# Example Usage and Testing
def main():
    """
    Main example showing Gap Question Generator with real/mock external systems
    """
    print("🚀 Starting Gap Question Generator with Modular External System")
    print("=" * 70)
    
    try:
        # Initialize Gemini LLM client
        print("📡 Initializing Gemini LLM client...")
        gemini_client = GeminiLLMClient()
        print("✅ Gemini client initialized successfully")
        
        # Initialize mock vector store
        print("💾 Setting up vector store...")
        memory_store = MockVectorStore()
        print("✅ Vector store initialized")
        
        # Test queries
        user_queries = [
            "What is the current state of the AI market and its future prospects?",
            "How are companies adopting machine learning in their operations?"
        ]
        
        # Test both real and mock systems
        for use_real_search in [False, True]:  # Test mock first, then real
            system_type = "Real Web Search" if use_real_search else "Mock System"
            print(f"\n🔧 Testing with {system_type}")
            print("=" * 50)
            
            for i, user_query in enumerate(user_queries, 1):
                print(f"\n📋 Example {i}: {user_query[:50]}...")
                print("-" * 40)
                
                # Initialize Gap Question Generator
                generator = GapQuestionGenerator(
                    llm_client=gemini_client,
                    user_query=user_query,
                    memory=memory_store,
                    max_iterations=2,  # Reduced for demo
                    confidence_threshold=0.85,
                    use_real_search=use_real_search
                )
                
                # Run the complete workflow
                if use_real_search:
                    print("⚠️  Real web search may take a few minutes...")
                
                results = generator.run()
                
                print("📊 Results:")
                print(f"  • Gaps identified: {results['total_gaps_identified']}")
                print(f"  • Queries processed: {results['queries_processed']}")
                print(f"  • External calls: {results['external_system_calls']}")
                print(f"  • Content added: {results['content_items_added']}")
                print(f"  • Final confidence: {results['final_confidence']:.2f}")
                print(f"  • Stop condition: {generator.stop_condition}")
                
                # Show external system stats
                if generator.external_system:
                    stats = generator.external_system.get_processing_stats()
                    print(f"  • Vector store items: {stats['total_items_stored']}")
                
                if i == 1:  # Only test first query for real search
                    break
        
    except Exception as e:
        print(f"❌ Error in example execution: {str(e)}")

def main_with_mock():
    """Fallback demo with mock client"""
    print("🚀 Running Gap Question Generator Demo (Mock LLM Mode)")
    print("=" * 60)
    
    class MockGeminiClient:
        def generate(self, prompt):
            if "CAN_ANSWER" in prompt:
                return "CAN_ANSWER: NO\nMISSING_INFO: Current market data\nCompetitive landscape\nTechnology trends"
            elif "Generate web search" in prompt or "web search queries" in prompt.lower():
                return "AI market size 2024\nartificial intelligence trends\nmachine learning adoption enterprise"
            elif "Can this query be answered" in prompt:
                return "NO"
            else:
                return "Analysis complete"
        
        def complete(self, prompt):
            return self.generate(prompt)
    
    mock_client = MockGeminiClient()
    memory_store = MockVectorStore()
    user_query = "What is the current state of the AI market and its future prospects?"
    
    # Test with mock external system
    generator = GapQuestionGenerator(
        llm_client=mock_client,
        user_query=user_query,
        memory=memory_store,
        max_iterations=2,
        confidence_threshold=0.85,
        use_real_search=False  # Use mock external system
    )
    
    print(f"📋 Processing Query: {user_query}")
    print("-" * 50)
    
    results = generator.run()
    
    print("\n📊 Demo Results:")
    for key, value in results.items():
        print(f"  • {key}: {value}")
    
    print("\n✅ Demo completed successfully!")
    print("💡 To use real systems:")
    print("   1. Set GOOGLE_API_KEY in .env file")
    print("   2. Set use_real_search=True")

if __name__ == "__main__":
    # Check if .env file exists and provide helpful guidance
    env_file_path = ".env"
    
    if not os.path.exists(env_file_path):
        print("📄 Creating sample .env file...")
        sample_env_content = """# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Set other configurations
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your_langsmith_api_key_here
"""
        try:
            with open(env_file_path, 'w') as f:
                f.write(sample_env_content)
            print(f"✅ Created {env_file_path} file")
            print("📝 Please update the GOOGLE_API_KEY in the .env file")
            print("   You can get your API key from: https://makersuite.google.com/app/apikey")
        except Exception as e:
            print(f"❌ Could not create .env file: {e}")
    
    # Check if API key is available after loading .env
    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_google_api_key_here":
        print("⚠️  WARNING: GOOGLE_API_KEY not properly set in .env file!")
        print(f"   Please edit {env_file_path} and add your actual Google API key")
        print("\n🔄 Running with mock responses for demonstration...")
        
        # Run with mock client for demonstration
        main_with_mock()
    else:
        print("✅ GOOGLE_API_KEY loaded successfully from .env file")
        main()