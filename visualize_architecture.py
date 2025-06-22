#!/usr/bin/env python3
"""
Deep Research Agent - Architecture Visualization
Creates interactive diagrams showing project structure and data flow
"""

import os
import webbrowser
from pathlib import Path

def create_mermaid_html(mermaid_code, title="Architecture Diagram"):
    """Create HTML file with Mermaid diagram"""
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .mermaid {{
            text-align: center;
            margin: 20px 0;
        }}
        .description {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 {title}</h1>
        <div class="description">
            <p><strong>Deep Research Agent Architecture:</strong> This diagram shows how all components interact in the research system.</p>
            <ul>
                <li>🎯 <strong>Blue nodes:</strong> Entry points and routing</li>
                <li>🧠 <strong>Purple nodes:</strong> Core processing components</li>
                <li>🌐 <strong>Green nodes:</strong> Data scrapers and retrievers</li>
                <li>🗄️ <strong>Orange nodes:</strong> Storage systems</li>
                <li>📊 <strong>Pink nodes:</strong> Output and reporting</li>
            </ul>
        </div>
        <div class="mermaid">
{mermaid_code}
        </div>
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true
            }}
        }});
    </script>
</body>
</html>
"""
    return html_template

def get_main_architecture_diagram():
    """Main architecture diagram showing all components"""
    return """
graph TB
    %% Entry Points
    USER[👤 User Query] --> ROUTER[🎯 Research Router<br/>categorizer/router.py]
    
    %% Core Categorization
    ROUTER --> PROMPT[📝 Prompt Club<br/>Prompts/prompt.py]
    ROUTER --> CATEGORIES[📊 Categories<br/>categorizer/categories.py]
    
    %% Planning Layer
    ROUTER --> PLANNER_V2[🧠 Planner v2<br/>planner/v2/]
    PLANNER_V2 --> PLAN_TREE[🌳 Plan Tree<br/>plan_tree.py]
    PLANNER_V2 --> QUERY_ENHANCER[⚡ Query Enhancer<br/>query_enhancer.py]
    PLANNER_V2 --> AMBIGUITY[❓ Ambiguity Resolver<br/>ambiguity_resolver.py]
    
    %% Main Research Workflows
    ROUTER --> WEB_SEARCH[🌐 Web Search<br/>web_search.py]
    ROUTER --> SEARCH_STORE[🔄 Search Store Retrieve<br/>_search_store_retrieve_.py]
    ROUTER --> GAP_GEN[🎯 Gap Question Generator<br/>gap_questions/generator.py]
    
    %% Web Search Components
    WEB_SEARCH --> SERPAPI[🔍 SerpAPI<br/>retrievers/serpapi/]
    WEB_SEARCH --> BROWSER[🌐 Universal Loader<br/>scrapers/browser/]
    WEB_SEARCH --> TAVILY[📡 Tavily Scraper<br/>scrapers/tavily/]
    WEB_SEARCH --> AGENTQL[🤖 AgentQL<br/>scrapers/agentql/]
    
    %% Academic Research Tools
    ROUTER --> TOOLS[🛠️ Research Tools<br/>tools/tools.py]
    TOOLS --> ARXIV_RET[📚 ArXiv Retriever<br/>retrievers/arxiv/]
    TOOLS --> RSS_RET[📰 RSS Retriever<br/>retrievers/research_rssharvest/]
    ARXIV_RET --> ARXIV_SCRAPER[📄 ArXiv Scraper<br/>scrapers/arxiv/]
    RSS_RET --> MEDRXIV_SCRAPER[🧬 MedRxiv Scraper<br/>scrapers/medrxiv/]
    RSS_RET --> BIORXIV_SCRAPER[🔬 BioRxiv Scraper<br/>scrapers/biorxiv/]
    
    %% Vector Store System
    SEARCH_STORE --> VECTOR_MGR[🗄️ Vector Store Manager<br/>vectore_store/vector_store.py]
    VECTOR_MGR --> QDRANT[💾 Qdrant Service<br/>vectore_store/qdrant_db.py]
    
    %% YouTube Processing
    BROWSER --> YOUTUBE[📺 YouTube Transcriber<br/>browser/youtube_transcriber.py]
    
    %% Graph RAG Advanced
    GAP_GEN --> GRAPH_RAG[🕸️ Graph RAG<br/>graph_rag/graphiti_graph.py]
    
    %% Data Flow
    WEB_SEARCH --> DATA_FLOW[📊 Scraped Data]
    TOOLS --> DATA_FLOW
    DATA_FLOW --> VECTOR_MGR
    VECTOR_MGR --> SEARCH_RESULTS[🎯 Search Results]
    SEARCH_RESULTS --> GAP_GEN
    
    %% Output Generation
    GAP_GEN --> LOGS[📋 Execution Logs<br/>gap_generator_logs/]
    LOGS --> REPORTS[📊 Reports & Visualizations]
    
    %% Styling
    classDef entry fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef core fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef scraper fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef storage fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class USER,ROUTER entry
    class PLANNER_V2,PLAN_TREE,WEB_SEARCH,SEARCH_STORE,GAP_GEN core
    class SERPAPI,BROWSER,TAVILY,AGENTQL,ARXIV_SCRAPER,MEDRXIV_SCRAPER,BIORXIV_SCRAPER scraper
    class VECTOR_MGR,QDRANT storage
    class LOGS,REPORTS output
"""

def get_data_flow_diagram():
    """Simplified data flow diagram"""
    return """
flowchart LR
    A[👤 User Query] --> B[🎯 Router]
    B --> C[🌐 Web Search]
    B --> D[📚 Academic Tools]
    B --> E[🧠 Gap Generator]
    
    C --> F[📊 Data Collection]
    D --> F
    
    F --> G[🗄️ Vector Store]
    G --> H[🔍 Similarity Search]
    H --> E
    
    E --> I[📋 Final Report]
    
    style A fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style B fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style I fill:#fce4ec,stroke:#880e4f,stroke-width:3px
    style F fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    style G fill:#fff3e0,stroke:#e65100,stroke-width:2px
"""

def get_component_hierarchy():
    """Component hierarchy diagram"""
    return """
graph TD
    ROOT[🔍 Deep Research Agent]
    
    ROOT --> CAT[📊 Categorizer]
    ROOT --> RES[🔬 Researcher]
    ROOT --> PROM[📝 Prompts]
    
    CAT --> ROUTER[router.py]
    CAT --> CATEGORIES[categories.py]
    
    RES --> SCRAPERS[🌐 Scrapers]
    RES --> RETRIEVERS[🔍 Retrievers]
    RES --> TOOLS[🛠️ Tools]
    RES --> VECTOR[🗄️ Vector Store]
    RES --> PLANNER[🧠 Planner]
    RES --> GAP[🎯 Gap Questions]
    
    SCRAPERS --> ARXIV_S[ArXiv]
    SCRAPERS --> BROWSER_S[Browser]
    SCRAPERS --> TAVILY_S[Tavily]
    SCRAPERS --> AGENTQL_S[AgentQL]
    SCRAPERS --> MEDRXIV_S[MedRxiv]
    SCRAPERS --> BIORXIV_S[BioRxiv]
    
    RETRIEVERS --> ARXIV_R[ArXiv]
    RETRIEVERS --> SERPAPI_R[SerpAPI]
    RETRIEVERS --> RSS_R[RSS Harvest]
    
    VECTOR --> QDRANT_V[Qdrant DB]
    VECTOR --> MANAGER_V[Vector Manager]
    
    PLANNER --> V1[v1]
    PLANNER --> V2[v2]
    
    V2 --> PLAN_TREE[Plan Tree]
    V2 --> QUERY_ENH[Query Enhancer]
    V2 --> AMBIGUITY[Ambiguity Resolver]
    
    style ROOT fill:#ff9999,stroke:#d32f2f,stroke-width:3px
    style CAT fill:#99ccff,stroke:#1976d2,stroke-width:2px
    style RES fill:#99ff99,stroke:#388e3c,stroke-width:2px
    style PROM fill:#ffcc99,stroke:#f57c00,stroke-width:2px
"""

def create_all_diagrams():
    """Create all architecture diagrams as HTML files"""
    
    # Create output directory
    output_dir = Path("architecture_diagrams")
    output_dir.mkdir(exist_ok=True)
    
    diagrams = [
        {
            "name": "main_architecture",
            "title": "Deep Research Agent - Main Architecture",
            "code": get_main_architecture_diagram()
        },
        {
            "name": "data_flow",
            "title": "Deep Research Agent - Data Flow",
            "code": get_data_flow_diagram()
        },
        {
            "name": "component_hierarchy",
            "title": "Deep Research Agent - Component Hierarchy",
            "code": get_component_hierarchy()
        }
    ]
    
    created_files = []
    
    for diagram in diagrams:
        html_content = create_mermaid_html(diagram["code"], diagram["title"])
        file_path = output_dir / f"{diagram['name']}.html"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        created_files.append(file_path)
        print(f"✅ Created: {file_path}")
    
    return created_files

def create_markdown_documentation():
    """Create comprehensive markdown documentation"""
    
    markdown_content = f"""# 🔍 Deep Research Agent - Architecture Documentation

## 📋 Project Overview

The **Deep Research Agent** is a sophisticated AI-powered research system that performs multi-modal research across various domains with three search modes: WebSearch, DeepSearch, and ExtremeSearch.

## 🏗️ Main Architecture

```mermaid
{get_main_architecture_diagram()}
```

## 📊 Data Flow

```mermaid
{get_data_flow_diagram()}
```

## 🏗️ Component Hierarchy

```mermaid
{get_component_hierarchy()}
```

## 🔄 Component Relationships & Data Flow

### 1. **Entry Point & Routing** 🎯
- **User Query** → **Research Router** (`categorizer/router.py`)
- Router uses **Prompt Club** (`Prompts/prompt.py`) for LLM prompts
- Categorizes queries into: `coding`, `finance`, `news`, `history`, `general`, `writing`, `current_day_events`

### 2. **Planning Layer** 🧠
- **Planner v2** (`planner/v2/`) creates research strategies
- **Plan Tree** (`plan_tree.py`) builds dependency-driven question hierarchies
- **Query Enhancer** optimizes search queries
- **Ambiguity Resolver** clarifies unclear queries

### 3. **Core Research Workflows** 🔄

#### A. **Web Search Pipeline** 🌐
```
web_search.py → [SerpAPI → Browser → Tavily → AgentQL] → Scraped Data
```

#### B. **Academic Research Pipeline** 📚
```
tools.py → [ArXiv/RSS Retrievers] → [Specialized Scrapers] → Research Papers
```

#### C. **Vector Store Pipeline** 🗄️
```
Scraped Data → Vector Store Manager → Qdrant → Similarity Search
```

### 4. **Advanced Processing** 🎯
- **Gap Question Generator** identifies knowledge gaps and generates follow-up research queries
- Uses LangGraph for orchestration with comprehensive logging

## 🚀 Execution Modes

### **WebSearch** 🌐
- Quick web-based research using SerpAPI + multiple scrapers

### **DeepSearch** 🔬
- Combines web + academic sources with vector store integration

### **ExtremeSearch** ⚡
- Full pipeline activation with dependency-driven research and Graph RAG

## 📁 Key File Dependencies

```
Main Entry Points:
├── web_search.py (Web research)
├── _search_store_retrieve_.py (Vector workflow)
└── gap_questions/generator.py (Advanced research)

Core Infrastructure:
├── categorizer/router.py (Query routing)
├── vectore_store/ (Data storage)
├── tools/tools.py (Academic tools)
└── scrapers/ (Data collection)
```

## 🛠️ How to Use This Documentation

1. **View Interactive Diagrams**: Open the HTML files in your browser
2. **GitHub/GitLab**: This markdown renders automatically with mermaid support
3. **VS Code**: Install Mermaid extensions for live preview
4. **Online**: Copy diagrams to https://mermaid.live/ for editing

"""
    
    with open("ARCHITECTURE.md", 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("✅ Created: ARCHITECTURE.md")
    return "ARCHITECTURE.md"

def main():
    """Main function to create all visualizations"""
    print("🎨 Creating Deep Research Agent Architecture Visualizations...")
    print("=" * 60)
    
    # Create HTML diagrams
    html_files = create_all_diagrams()
    
    # Create markdown documentation
    md_file = create_markdown_documentation()
    
    print("\n📊 Created Files:")
    print("-" * 30)
    for file_path in html_files:
        print(f"🌐 {file_path}")
    print(f"📝 {md_file}")
    
    print("\n🚀 How to View:")
    print("-" * 30)
    print("1. 🌐 Open HTML files in your browser for interactive diagrams")
    print("2. 📝 View ARCHITECTURE.md in VS Code with Mermaid extension")
    print("3. 🔗 Copy mermaid code to https://mermaid.live/ for online editing")
    print("4. 📱 Push to GitHub/GitLab for automatic rendering")
    
    # Try to open the main architecture in browser
    main_file = Path("architecture_diagrams/main_architecture.html")
    if main_file.exists():
        try:
            webbrowser.open(f"file://{main_file.absolute()}")
            print(f"\n🎯 Opening main architecture diagram in browser...")
        except:
            print(f"\n💡 Manually open: {main_file.absolute()}")

if __name__ == "__main__":
    main()
