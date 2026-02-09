# 🔍 Deep Research Agent - Architecture Documentation

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Status](https://img.shields.io/badge/status-active-green.svg)]()


## 🏗️ System Architecture

![Deep Research Agent Workflow](researcher/workflow.png)

*The complete system workflow showing all components and their interactions*

### 🔄 Core Components

| Component | Description | Location |
|-----------|-------------|----------|
| **Planner v2** | Advanced research planning with dependency trees | `researcher/planner/v2/` |
| **Solution Tree** | Recursive research solver with gap analysis | `researcher/solution_tree/` |
| **Web Search Engine** | Multi-source web scraping and retrieval | `researcher/web_search/web_search.py` |
| **Academic Tools** | ArXiv, MedRxiv, BioRxiv integration | `researcher/tools/tools.py` |
| **Vector Store** | Qdrant-based similarity search | `researcher/vectore_store/` |
| **Reviewer** | Research quality assurance | `reviewer/reviewer.py` |
| **Writer** | Content generation and formatting | `writer/writer.py` |
| **Publisher** | Output publication | `publisher/publisher.py` |

---

## 🚀 Search Modes

### 🌐 WebSearch Mode
**Quick web-based research for immediate answers**

- Uses SerpAPI for search results
- Multiple scraper integration (Tavily, AgentQL, Browser)
- Fast response time
- Ideal for: Current events, quick facts, general queries

### 🔬 DeepSearch Mode
**Comprehensive research combining multiple sources**

- Web search + Academic sources
- Vector store integration for context
- Enhanced query processing
- Ideal for: Research projects, detailed analysis, academic work

### ⚡ ExtremeSearch Mode
**Full-pipeline research with advanced AI techniques**

- Complete dependency-driven research
- Graph RAG integration
- Ambiguity resolution
- Gap question generation
- Ideal for: Complex research, thesis work, comprehensive reports

---

## 📊 Current Data Flow Architecture

```mermaid
flowchart TD
    A[👤 User Query] --> B[🎯 Research Router]
    B --> C{Query Category}
    
    C -->|Web| D[🌐 Web Search]
    C -->|Academic| E[📚 Academic Tools]
    C -->|Complex| F[🧠 Planner v2]
    
    D --> G[🔍 Multi-Source Scraping]
    E --> H[📄 Paper Retrieval]
    F --> I[🌳 Plan Tree Generation]
    
    G --> J[📊 Data Processing]
    H --> J
    I --> K[🎯 Gap Analysis]
    
    J --> L[🗄️ Vector Store]
    L --> M[🔍 Similarity Search]
    M --> K
    
    K --> N[📋 Final Report]
    
    style A fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style N fill:#fce4ec,stroke:#880e4f,stroke-width:3px
    style B fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
```

---

## 🏗️ Component Structure

### 📁 Project Organization

```
deep-research-agent/
├── 🔬 Researcher/           # Core research components
│   ├── scrapers/           # Data collection modules
│   │   ├── browser/        # Web browser automation
│   │   ├── tavily/         # Tavily API integration
│   │   ├── agentql/        # AgentQL scraping
│   │   ├── arxiv/          # ArXiv paper scraping
│   │   ├── medrxiv/        # MedRxiv integration
│   │   ├── biorxiv/        # BioRxiv integration
│   │   ├── ecommerce/      # Ecommerce scraping
│   │   └── finance/        # Finance scraping
│   ├── retrievers/         # Search and retrieval
│   │   ├── serpapi/        # Google Search API
│   │   ├── arxiv/          # ArXiv API
│   │   └── research_rssharvest/ # RSS feed processing
│   ├── vectore_store/      # Vector database
│   │   ├── vector_store.py # Vector operations
│   │   ├── qdrant_db.py    # Qdrant integration
│   │   ├── long_term_memory/
│   │   ├── reddis/
│   │   └── short_conversational_memory/
│   ├── planner/            # Research planning
│   │   ├── v1/             # Legacy planner
│   │   ├── v2/             # Advanced planner
│   │   ├── archive-tree-based/
│   │   ├── planner.py      # Main planner logic
│   │   └── ...             # Planner utilities
│   ├── solution_tree/      # Solution tree implementation
│   ├── web_search/         # Web search module
│   ├── graph_rag/          # Graph RAG implementation
│   ├── tools/              # Research utilities
│   └── research_engine.py  # Research engine entry point
├── 📝 Prompts/             # LLM prompt management
│   └── prompt.py
├── 🧠 LLMs/                # LLM integration
│   └── llms.py
├── 📢 Publisher/           # Publishing module
│   └── publisher.py
├── 🧐 Reviewer/            # Reviewer module
│   └── reviewer.py
├── 💾 States/              # State management
│   └── state.py
├── ✍️ Writer/              # Writing module
│   └── writer.py
├── researcher_reviewer_graph.py # Main graph definition
└── workflow_results/       # Workflow results
```

---

## 🔧 Technical Implementation

### 🧠 Planning System

The **Planner v2** system creates intelligent research strategies:

- **Plan Tree**: Builds dependency-driven question hierarchies
- **Query Enhancer**: Optimizes search queries for better results
- **Ambiguity Resolver**: Clarifies unclear or ambiguous queries
- **Dependency Management**: Ensures logical research flow

### 🗄️ Vector Store Integration

**Qdrant-powered similarity search**:

```python
# Example vector store workflow
scraped_data → vector_embedding → qdrant_storage → similarity_search → relevant_context
```

### 🎯 Gap Question Generation

Advanced AI system that:
- Identifies knowledge gaps in research
- Generates intelligent follow-up questions
- Uses LangGraph for orchestration
- Provides comprehensive logging and visualization

---

## 🚦 Getting Started

### Prerequisites

- Python 3.8+
- Qdrant database
- API keys for external services (SerpAPI, etc.)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/deep-research-agent.git
   cd deep-research-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Set up your API keys and configuration
   cp .env.example .env
   ```

4. **Run a simple search**
   ```python
   from researcher.web_search import WebSearch
   
   # Quick web search
   results = WebSearch().search("AI research trends 2024")
   ```

---

## 📈 Performance & Scalability

| Mode | Response Time | Sources | Accuracy | Use Case |
|------|---------------|---------|----------|----------|
| WebSearch | ~30 seconds | 5-10 | Good | Quick queries |
| DeepSearch | ~2-5 minutes | 15-25 | High | Research projects |
| ExtremeSearch | ~5-15 minutes | 25+ | Excellent | Comprehensive analysis |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links


- [Issues](https://github.com/your-repo/deep-research-agent/issues)

---

*Built By WORT TEAM*
