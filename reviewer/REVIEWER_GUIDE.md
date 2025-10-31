# Reviewer System - Complete Guide

## Overview

The **Reviewer** is a content enrichment system that analyzes research output and generates synthesis queries to deepen understanding. Each review query is resolved through the Solver to produce comprehensive, source-backed answers.

## Architecture

### Key Components

1. **ReviewNode** - Represents a review query with its resolution
2. **Reviewer** - Main orchestrator that generates and resolves review queries
3. **Solver Integration** - Each review query is resolved using the Solver with specific configuration

### Configuration

```python
Reviewer(
    num_review_queries=3,           # Number of review queries to generate
    collection_name="research-documents"  # Vector store collection
)
```

### Solver Configuration for Review Queries

Each review query is resolved with:
- `num_web_queries=3` - Generate 3 web search queries
- `num_vector_queries=3` - Generate 3 vector search queries
- `max_web_results=3` - Retrieve 3 web results per query
- `num_gaps_per_node=0` - No gap generation (terminal resolution)

## Execution Flow

### Step 1: Generate Review Queries

**Input:**
- Original research query
- Content dictionary (query-answer pairs from Solver.resolve())

**Process:**
1. Format existing content into readable summary
2. Create LLM prompt requesting synthesis questions
3. Invoke `gemini-2.0-flash-001` model
4. Parse JSON response containing review queries

**Output:** List of n review queries

**Example:**
```python
original_query = "What are the key differences between Python async/await and threading?"

content = {
    "How does async/await work in Python?": "Async/await enables cooperative multitasking...",
    "What are threading performance characteristics?": "Threading uses OS-level threads..."
}

# Generated review queries:
[
    "What are the main trade-offs between async/await and threading for I/O-bound tasks?",
    "How do async/await and threading compare in terms of debugging complexity?",
    "What are the best use cases for choosing async/await vs threading?"
]
```

---

### Step 2: Create ReviewNodes

Each review query is wrapped in a `ReviewNode` object:

```python
class ReviewNode:
    def __init__(self, query: str):
        self.query = query    # The review query
        self.answer = None    # Will be filled by Solver
```

---

### Step 3: Resolve Each ReviewNode

For each ReviewNode sequentially:

1. **Initialize Solver** with review configuration
2. **Execute Solver.resolve()** pipeline:
   - Generate 3 web search queries
   - Retrieve web content and store in vector DB
   - Generate 3 vector search queries
   - Perform gap analysis (returns 0 gaps due to config)
   - Return query-answer pairs with sources

3. **Store answer** in ReviewNode

**Example Resolution:**

```
Review Query: "What are the main trade-offs between async/await and threading for I/O-bound tasks?"

Solver Process:
├── Web Search Queries:
│   ├── "async/await vs threading I/O performance Python"
│   ├── "cooperative vs preemptive multitasking comparison"
│   └── "asyncio event loop overhead analysis"
│
├── Web Content → Vector Store (3 results)
│
├── Vector Search Queries:
│   ├── "What are the performance implications of async/await for I/O operations?"
│   ├── "How does threading handle I/O-bound tasks differently than async?"
│   └── "What is the overhead of the asyncio event loop?"
│
├── Gap Analysis:
│   └── Returns answers with sources (no gaps)
│
└── Output:
    {
        "What are the performance implications of async/await for I/O operations?":
            "Async/await excels at I/O-bound tasks by avoiding thread overhead...\n\n**Sources:**\n- https://...",

        "How does threading handle I/O-bound tasks differently than async?":
            "Threading uses OS-level context switching which has higher overhead...\n\n**Sources:**\n- https://...",

        "What is the overhead of the asyncio event loop?":
            "The event loop adds minimal overhead compared to thread switching...\n\n**Sources:**\n- https://..."
    }
```

---

### Step 4: Merge Content

Enriched content = Original content + All review answers

```python
# Original content (2 items)
{
    "How does async/await work in Python?": "Async/await enables...",
    "What are threading performance characteristics?": "Threading uses..."
}

# After 2 review queries resolved (assuming 3 sub-answers each = 6 new items)
# Enriched content (8 items total)
{
    # Original content
    "How does async/await work in Python?": "Async/await enables...",
    "What are threading performance characteristics?": "Threading uses...",

    # Review Query 1 answers
    "What are the performance implications of async/await for I/O operations?": "Async/await excels...",
    "How does threading handle I/O-bound tasks differently than async?": "Threading uses...",
    "What is the overhead of the asyncio event loop?": "The event loop...",

    # Review Query 2 answers
    "How do debugging tools differ between async and threading?": "Async debugging requires...",
    "What are common pitfalls when debugging async code?": "Race conditions in async...",
    "What threading debugging tools are available in Python?": "Threading provides..."
}
```

---

## Usage Example

### Basic Usage

```python
import asyncio
from reviewer.reviewer import Reviewer
from researcher.solution_tree.main import Solver

async def main():
    # Step 1: Get initial research from Solver
    solver = Solver(query="What is quantum computing?")
    gaps, content = await solver.resolve()

    # Step 2: Review and enrich content
    reviewer = Reviewer(num_review_queries=3)
    enriched_content = await reviewer.review_and_enrich(
        original_query="What is quantum computing?",
        content=content
    )

    # Step 3: Use enriched content
    print(f"Original items: {len(content)}")
    print(f"Enriched items: {len(enriched_content)}")

    for query, answer in enriched_content.items():
        print(f"\nQ: {query}")
        print(f"A: {answer}")

asyncio.run(main())
```

### Advanced Usage with Custom Configuration

```python
async def advanced_review():
    # Custom reviewer configuration
    reviewer = Reviewer(
        num_review_queries=5,                    # Generate 5 review queries
        collection_name="specialized-research"   # Use custom collection
    )

    # Run review process
    enriched = await reviewer.review_and_enrich(
        original_query="Compare transformer architectures",
        content=existing_research_content
    )

    return enriched
```

---

## Key Features

### 1. Same Model as Solution Tree
Uses `gemini-2.0-flash-001` for consistency with solution_tree system

### 2. Terminal Resolution
Review queries are fully resolved without generating new gaps (`num_gaps_per_node=0`)

### 3. Content Enrichment
Original content is preserved and augmented with review insights

### 4. Source Attribution
All answers include source citations from vector store retrieval

### 5. Robust Error Handling
Graceful degradation if review query generation or resolution fails

---

## Complexity Analysis

**For num_review_queries=n:**

- **LLM Calls:** 1 (review generation) + n (review resolutions) = n+1
- **Web Searches:** n × 3 web queries = 3n web searches
- **Vector Searches:** n × 3 vector queries = 3n vector searches
- **Content Growth:** Original items + (n × ~3 sub-answers) ≈ Original + 3n items

**Example with n=3:**
- 4 LLM calls total
- 9 web searches
- 9 vector searches
- ~9 new query-answer pairs added

---

## Integration with Solution Tree

### Combined Pipeline

```python
async def full_research_pipeline():
    # Phase 1: Build Solution Tree (depth-first expansion)
    from researcher.solution_tree.main import step_executor

    initial_query = "Compare Vision Transformers and CNNs"
    research_tree_root = await step_executor(
        initial_queries=[initial_query],
        max_depth=2,
        num_gaps_per_node=2
    )

    # Phase 2: Review each resolved node
    reviewer = Reviewer(num_review_queries=2)

    # Get root node answer (other nodes can be reviewed similarly)
    if research_tree_root and research_tree_root.answer:
        enriched_root_content = await reviewer.review_and_enrich(
            original_query=research_tree_root.query,
            content=research_tree_root.answer
        )

        # Update the tree node with enriched content
        research_tree_root.answer = enriched_root_content

    return research_tree_root
```

---

## Design Principles

### Simplicity
- Minimal class hierarchy (ReviewNode + Reviewer)
- Clear separation of concerns
- Single main method: `review_and_enrich()`

### Robustness
- Comprehensive error handling
- Graceful fallbacks (returns original content on failure)
- Detailed logging throughout pipeline

### Consistency
- Uses same LLM model as solution_tree
- Reuses Solver infrastructure
- Follows same async patterns

---

## Testing

Run the example code:

```bash
python -m reviewer.reviewer
```

This executes a dry run with mock content showing:
1. Initial content from Solver
2. Review query generation
3. Review query resolution
4. Enriched content output

---

## Future Enhancements

1. **Parallel Resolution** - Resolve multiple review queries concurrently
2. **Adaptive Query Count** - Dynamically adjust num_review_queries based on content complexity
3. **Quality Scoring** - Rate review answer quality and retry low-scoring resolutions
4. **Caching** - Cache review resolutions for similar queries
5. **Export Formats** - Generate structured reports from enriched content
