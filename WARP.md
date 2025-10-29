# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a **Deep Research Agent** - an AI-powered research tool that performs comprehensive research across domains like finance, coding, biology, business, and market analysis. The system is built using LangGraph and provides three levels of research depth: WebSearch, DeepSearch, and ExtremeSearch.

**Key Technologies**: Python 3.8+, LangGraph, Google Gemini AI, Qdrant Vector Database, LangChain, Playwright

## Development Setup

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode (recommended)
pip install -e .
```

### Environment Configuration
Create a `.env` file with these required variables:
```bash
GOOGLE_API_KEY=your_gemini_api_key        # Required for Gemini AI models
OPENAI_API_KEY=your_openai_key           # Required for embeddings
QDRANT_URL=your_qdrant_url               # Vector database connection
QDRANT_API_KEY=your_qdrant_api_key       # Qdrant authentication
```

### Environment Testing
```bash
# Test environment setup and dependencies
python researcher/gap_questions/test_env_check.py
```

## Architecture & Code Structure

### LangGraph Workflow Pattern
The codebase follows a **RESEARCHER → REVIEWER → WRITER → PUBLISHER** flow using LangGraph:
- ** Reviewer and Researchers suppose to be one subgraph that connected and does research  or improve until it improve by reviewr and then writer --> publisher access it.
- **States**: All workflow state is managed through `AgentGraphState` in `states/state.py`
- **Node Pattern**: Each component has a single `run()` method that serves as a LangGraph node
- **Structured Output**: Uses Pydantic models for LLM responses and type safety

### Core Components

#### 1. **States System** (`states/state.py`)
- `AgentGraphState`: Global workflow state containing report sections, research data, file paths
- `ReportSection`: Individual report section structure  
- `ResearchReviewData`: Research review workflow state
- Pydantic models for structured LLM outputs

#### 2. **Research Engine** (`researcher/`)
- **Core**: `research_engine.py` - Main research orchestrator
- **Workflow**: `sub_researcher_graph.py` - LangGraph implementation for research → review → improve cycle
- **Scrapers**: Multiple specialized scrapers (ArXiv, MedRxiv, BioRxiv, web browsers)
- **Vector Store**: Qdrant-based similarity search and document embedding

#### 3. **Query Processing** (`categorizer/`)
- `router.py`: Categorizes queries and routes to appropriate search depth
- `categories.py`: Domain-specific category definitions

#### 4. **Review System** (`reviewer/reviewer.py`)  
- Evaluates research completeness and quality
- Provides feedback for iterative improvement
- Uses LangGraph pattern with state management

#### 5. **Report Generation** (`writer/writer.py`)
- Generates structured report components (introduction, sections, abstract, conclusion)
- Uses Pydantic schemas for consistent output formatting
- Async methods for parallel processing

#### 6. **Publishing** (`publisher/publisher.py`)
- Outputs reports in PDF, DOCX, and Markdown formats
- Uses utility functions for format conversion

### Search Modes

| Mode | Response Time | Sources | Use Case |
|------|--------------|---------|----------|
| **WebSearch** | ~30 seconds | 5-10 | Quick queries, current events |
| **DeepSearch** | ~2-5 minutes | 15-25 | Research projects, detailed analysis |
| **ExtremeSearch** | ~5-15 minutes | 25+ | Comprehensive analysis, thesis work |

### Key Architectural Patterns

#### Small Function Decomposition
- Complex code is broken into small, focused functions within classes
- Utility functions are extracted to `utils.py` files in subdirectories
- Each component directory has its own utils when functions don't belong in the main class

#### Documentation Standards  
- Simple one-liner docstrings for straightforward methods
- Focus on clarity and maintainability over complex implementations
- Avoid unnecessary complexity that might break other parts of the system

#### LangGraph Integration
- Each workflow component implements a `run()` method for LangGraph nodes
- State flows through the system using TypedDict classes
- Structured output ensures type safety with Pydantic models

## Common Development Commands

### Testing Components
```bash
# Test individual components with their __main__ blocks
python -m reviewer.reviewer          # Test reviewer with sample data
python -m writer.writer              # Test writer with fake data  
python -m publisher.publisher        # Test publisher functionality
python -m sub_researcher_graph       # Test research workflow
```

### Research Engine Usage
```bash
# Quick web search
from researcher.research_engine import ResearchEngine
engine = ResearchEngine("web", "technology", websocket, "markdown")
results = await engine.SearchEngine("AI trends 2024")

# Deep research with academic sources
engine = ResearchEngine("deep", "biology", websocket, "pdf") 
results = await engine.SearchEngine("CRISPR gene editing advances")
```

### Vector Database Operations
```bash
# Test Qdrant connection
from researcher.vectore_store import QdrantService
qdrant_service = QdrantService(collection_name="test_collection")
```

## Important Implementation Notes

### Async/Await Pattern
- The system is async-first - most operations use `async/await`
- Always use `await` when calling async methods in writer, publisher, and research components
- Example: `result = await writer.generate_section_report(state)`

### LLM Client Usage  
- Uses `GeminiLLMClient()` from `researcher/gap_questions/llm_client.py`
- Multiple model support via `LlmsHouse()` in `llms/llms.py`
- Structured output with Pydantic schemas for consistent responses

### State Management
- State flows through LangGraph nodes as dictionaries
- Update state in-place and return the modified state
- Use `Annotated[List[str], operator.add]` for accumulating feedback lists

### Error Handling
- Extensive logging throughout the system
- Graceful degradation when components fail
- Always check for required state keys before processing

## Project Configuration

### Package Structure (pyproject.toml)
```toml
[project]
name = "deep-research-agent"
requires-python = ">=3.8"
dependencies = [
    "langchain", "langgraph", "google-generative-ai",
    "qdrant-client", "playwright", "agentql", "pydantic"
]
```

### Key Dependencies
- **LangChain/LangGraph**: Core framework for LLM applications and workflows
- **Google Generative AI**: Gemini models for query processing  
- **Qdrant**: Vector database for similarity search
- **Playwright**: Web browser automation for scraping
- **AgentQL**: Structured web scraping
- **Pydantic**: Data validation and structured outputs

This architecture enables scalable research workflows with iterative refinement, structured outputs, and multi-format publishing capabilities.
