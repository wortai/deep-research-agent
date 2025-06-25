# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Deep Research Agent** - an AI-powered research tool that performs comprehensive research across domains like finance, coding, biology, business, and market analysis. The system uses LangChain, Google Gemini AI, and multiple data sources to deliver three levels of research depth: WebSearch, DeepSearch, and ExtremeSearch.

## Development Environment

**Language**: Python 3.8+
**Package Management**: Uses both `requirements.txt` and `pyproject.toml`

### Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Environment Variables
Configure `.env` file with:
- `GOOGLE_API_KEY` - Required for Gemini AI model
- Additional API keys for external services (SerpAPI, etc.)

## Architecture Overview

### Core Components

1. **Research Engine** (`researcher/research_engine.py`)
   - Main orchestrator routing queries to appropriate search depth
   - Methods: `web_search()`, `deep_search()`, `extreme_search()`

2. **Query Router** (`categorizer/router.py`)
   - Categorizes research queries using Google Gemini AI
   - Routes to appropriate research components based on content type

3. **Deep Search Planner** (`researcher/planner/planner.py`)
   - Advanced planning system with iterative refinement
   - Components: QueryEnhancer, PlanGenerator, PlanEvaluator, PlanRefiner

4. **Web Search System** (`researcher/web_search/web_search.py`)
   - Multi-source data collection and processing
   - Integrates with various scrapers and retrievers

### Data Collection & Processing

**Scrapers** (`researcher/scrapers/`):
- `arxiv/` - Academic paper scraping from ArXiv
- `medrxiv/`, `biorxiv/` - Medical/biological research papers
- `browser/` - Web browser automation with Playwright
- `tavily/` - Tavily API integration
- `agentql/` - AgentQL for structured web scraping
- `finance/` - Financial data with yfinance
- `ecommerce/` - E-commerce data scraping

**Retrievers** (`researcher/retrievers/`):
- `serpapi/` - Google Search API integration
- `arxiv/` - ArXiv API retrieval
- `research_rssharvest/` - RSS feed processing

**Vector Store** (`researcher/vector_store/`):
- Qdrant integration for similarity search
- Document embedding and retrieval

### Advanced Features

**Gap Questions** (`researcher/gap_questions/`):
- Intelligent follow-up question generation
- Uses LangGraph for orchestration
- Identifies knowledge gaps in research

**Graph RAG** (`researcher/graph_rag/`):
- Graph-based retrieval augmented generation
- Advanced knowledge graph construction

## Testing

The codebase includes example usage patterns in main modules. To test components:

```python
# Test Research Engine
from researcher.research_engine import ResearchEngine
engine = ResearchEngine("deep", "technology", websocket, "markdown")
results = await engine.SearchEngine("AI trends 2024")

# Test Query Router
from categorizer.router import ResearchRouter
router = ResearchRouter()
result = router.categorize_query(["AI research"], "Find AI trends")
```

## Key Dependencies

- **LangChain**: Core framework for LLM applications
- **Google Generative AI**: Gemini models for query processing
- **Qdrant**: Vector database for similarity search
- **Playwright**: Web browser automation
- **AgentQL**: Structured web scraping
- **Pydantic**: Data validation and settings management
- **asyncio**: Asynchronous programming support

## Search Modes Configuration

- **WebSearch**: max_results=5, no academic papers
- **DeepSearch**: max_results=15, arxiv_max_results=5, medbio_max_results=5  
- **ExtremeSearch**: max_results=25, arxiv_max_results=10, medbio_max_results=10

## Important Files to Understand

- `researcher/research_engine.py` - Main entry point for research operations
- `categorizer/router.py` - Query categorization and routing logic
- `researcher/planner/planner.py` - Advanced research planning system
- `researcher/web_search/web_search.py` - Web search orchestration
- `architecture.md` - Detailed system architecture documentation
- `pyproject.toml` - Project configuration and dependencies

## Development Notes

- The system is async-first - most operations use `async/await`
- Extensive logging is implemented throughout the system
- Modular design allows for easy extension of scrapers and retrievers
- Pydantic models ensure type safety and data validation
- The planner system supports iterative refinement with quality scoring