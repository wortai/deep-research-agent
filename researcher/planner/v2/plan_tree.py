from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from langchain_core.language_models.base import BaseLanguageModel


class QuestionType(Enum):
    """Enumeration of different types of research questions."""
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"
    VERIFICATION = "verification"
    CONTEXTUAL = "contextual"
    PREDICTIVE = "predictive"


@dataclass
class DependencyQuestion:
    """Represents a research question with dependency information."""
    question_id: str
    question_text: str
    question_type: QuestionType
    complexity_level: int = 1  # 1=simple, 5=very complex
    priority: int = 1  # 1=highest, 5=lowest
    search_keywords: List[str] = field(default_factory=list)
    expected_answer_type: str = ""
    is_prerequisite: bool = True  # True if this must be answered before parent
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"[{self.question_type.value}] {self.question_text}"


@dataclass
class DependencyNode:
    """Represents a node in the dependency-driven research tree."""
    node_id: str
    question: DependencyQuestion
    dependencies: List['DependencyNode'] = field(default_factory=list)  # Child nodes (prerequisites)
    parent: Optional['DependencyNode'] = None
    depth: int = 0
    is_resolved: bool = False  # Whether this question has been answered
    
    def add_dependency(self, dependency_node: 'DependencyNode') -> None:
        """Add a dependency (child) node to this node."""
        dependency_node.parent = self
        dependency_node.depth = self.depth + 1
        self.dependencies.append(dependency_node)
    
    def get_all_dependencies(self) -> List['DependencyNode']:
        """Get all dependency nodes (direct and indirect prerequisites)."""
        all_deps = []
        for dep in self.dependencies:
            all_deps.append(dep)
            all_deps.extend(dep.get_all_dependencies())
        return all_deps
    
    def get_leaf_dependencies(self) -> List['DependencyNode']:
        """Get all leaf dependencies (nodes with no prerequisites)."""
        if not self.dependencies:
            return [self]
        
        leaves = []
        for dep in self.dependencies:
            leaves.extend(dep.get_leaf_dependencies())
        return leaves
    
    def can_be_resolved(self) -> bool:
        """Check if this node can be resolved (all dependencies are resolved)."""
        return all(dep.is_resolved for dep in self.dependencies)
    
    def get_unresolved_dependencies(self) -> List['DependencyNode']:
        """Get all unresolved dependencies for this node."""
        return [dep for dep in self.dependencies if not dep.is_resolved]
    
    def mark_resolved(self) -> None:
        """Mark this node as resolved."""
        self.is_resolved = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "node_id": self.node_id,
            "question": {
                "question_id": self.question.question_id,
                "question_text": self.question.question_text,
                "question_type": self.question.question_type.value,
                "complexity_level": self.question.complexity_level,
                "priority": self.question.priority,
                "search_keywords": self.question.search_keywords,
                "expected_answer_type": self.question.expected_answer_type,
                "is_prerequisite": self.question.is_prerequisite,
                "metadata": self.question.metadata
            },
            "depth": self.depth,
            "is_resolved": self.is_resolved,
            "dependencies_count": len(self.dependencies),
            "dependencies": [dep.to_dict() for dep in self.dependencies]
        }


class DependencyResearchTree:
    """Tree data structure representing hierarchical research questions with dependencies."""
    
    def __init__(self, root_query: str, max_depth: int = 4, max_dependencies_per_node: int = 4):
        self.root_query = root_query
        self.max_depth = max_depth
        self.max_dependencies_per_node = max_dependencies_per_node
        self.root: Optional[DependencyNode] = None
        self.nodes: Dict[str, DependencyNode] = {}
        self.total_questions = 0
        self.resolved_questions = 0
    
    def set_root(self, root_node: DependencyNode) -> None:
        """Set the root node of the tree."""
        self.root = root_node
        self.nodes[root_node.node_id] = root_node
        self.total_questions += 1
    
    def add_dependency_node(self, node: DependencyNode, parent_id: str) -> bool:
        """
        Add a dependency node to the tree.
        
        Returns:
            bool: True if node was added, False if constraints violated
        """
        if parent_id not in self.nodes:
            return False
        
        parent_node = self.nodes[parent_id]
        
        # Check depth constraint
        if parent_node.depth >= self.max_depth:
            return False
        
        # Check dependencies count constraint
        if len(parent_node.dependencies) >= self.max_dependencies_per_node:
            return False
        
        self.nodes[node.node_id] = node
        parent_node.add_dependency(node)
        self.total_questions += 1
        return True
    
    def get_execution_order(self) -> List[DependencyNode]:
        """Get questions in dependency-resolved execution order (bottom-up)."""
        if not self.root:
            return []
        
        # Get all nodes in topological order (dependencies first)
        execution_order = []
        visited: Set[str] = set()
        
        def visit_node(node: DependencyNode):
            if node.node_id in visited:
                return
            
            # Visit all dependencies first
            for dep in sorted(node.dependencies, key=lambda x: (x.question.priority, x.question.complexity_level)):
                visit_node(dep)
            
            # Then visit this node
            execution_order.append(node)
            visited.add(node.node_id)
        
        visit_node(self.root)
        return execution_order
    
    def get_ready_to_resolve_questions(self) -> List[DependencyNode]:
        """Get questions that are ready to be resolved (all dependencies satisfied)."""
        ready_questions = []
        for node in self.nodes.values():
            if not node.is_resolved and node.can_be_resolved():
                ready_questions.append(node)
        
        # Sort by priority and complexity
        return sorted(ready_questions, key=lambda x: (x.question.priority, x.question.complexity_level))
    
    def get_leaf_questions(self) -> List[DependencyNode]:
        """Get all leaf questions (questions with no dependencies)."""
        if not self.root:
            return []
        return self.root.get_leaf_dependencies()
    
    def mark_question_resolved(self, node_id: str) -> None:
        """Mark a question as resolved."""
        if node_id in self.nodes:
            self.nodes[node_id].mark_resolved()
            self.resolved_questions += 1
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current resolution progress."""
        return {
            "total_questions": self.total_questions,
            "resolved_questions": self.resolved_questions,
            "progress_percentage": (self.resolved_questions / self.total_questions * 100) if self.total_questions > 0 else 0,
            "ready_to_resolve": len(self.get_ready_to_resolve_questions()),
            "remaining_questions": self.total_questions - self.resolved_questions
        }
    
    def print_tree(self, node: Optional[DependencyNode] = None, prefix: str = "", is_last: bool = True) -> None:
        """Print a visual representation of the dependency tree."""
        if node is None:
            node = self.root
            if node is None:
                print("Empty dependency tree")
                return
            print(f"Dependency Research Tree: {self.root_query}")
            print(f"Max Depth: {self.max_depth}, Max Dependencies: {self.max_dependencies_per_node}")
            print("=" * 80)
        
        # Print current node with resolution status
        connector = "└── " if is_last else "├── "
        status = "✓" if node.is_resolved else "○"
        print(f"{prefix}{connector}{status} {node.question}")
        
        if node.question.search_keywords:
            keyword_prefix = prefix + ("    " if is_last else "│   ")
            print(f"{keyword_prefix}Keywords: {', '.join(node.question.search_keywords)}")
        
        # Print dependencies (children)
        for i, dep in enumerate(node.dependencies):
            dep_is_last = i == len(node.dependencies) - 1
            dep_prefix = prefix + ("    " if is_last else "│   ")
            self.print_tree(dep, dep_prefix, dep_is_last)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire tree to dictionary representation."""
        leaf_questions = self.get_leaf_questions()
        progress = self.get_progress()
        
        return {
            "root_query": self.root_query,
            "max_depth": self.max_depth,
            "max_dependencies_per_node": self.max_dependencies_per_node,
            "progress": progress,
            "tree": self.root.to_dict() if self.root else None,
            "leaf_questions": [node.question.question_text for node in leaf_questions],
            "execution_order": [node.question.question_text for node in self.get_execution_order()]
        }


def generate_dependency_questions(
    parent_question: str,
    model: BaseLanguageModel,
    max_dependencies: int = 4,
    current_depth: int = 0,
    max_depth: int = 4
) -> List[Dict[str, Any]]:
    """
    Generate dependency questions for a given parent question.
    
    Args:
        parent_question: The question to generate dependencies for
        model: LLM model for generating questions
        max_dependencies: Maximum number of dependencies to generate
        current_depth: Current depth in the tree
        max_depth: Maximum allowed depth
    
    Returns:
        List of dependency question data
    """
    
    if current_depth >= max_depth:
        return []
    
    dependency_prompt = f"""You are an expert research strategist. Given a research question, identify the prerequisite questions that MUST be answered first before you can properly address the main question.

MAIN QUESTION: {parent_question}

Think step by step:
1. What fundamental knowledge is needed to answer this question?
2. What key facts, definitions, or context must be established first?
3. What simpler sub-problems need to be solved as building blocks?

CONSTRAINTS:
- Generate maximum {max_dependencies} dependency questions
- Each dependency should be simpler than the main question
- Dependencies should be specific and answerable
- Focus on prerequisite knowledge, not parallel aspects
- Each dependency should be necessary to answer the main question

QUESTION TYPES:
- factual: Basic facts and definitions
- contextual: Background information needed
- quantitative: Numbers and data required
- verification: Confirm assumptions or claims
- analytical: Understanding mechanisms or processes

Respond with a JSON array of dependency questions:
[
    {{
        "question_text": "What is the definition of [key concept]?",
        "question_type": "factual",
        "complexity_level": 1,
        "priority": 1,
        "search_keywords": ["keyword1", "keyword2"],
        "expected_answer_type": "definition",
        "reasoning": "This definition is needed to understand the main question"
    }}
]

Generate the dependency questions now:"""
    
    try:
        response = model.invoke(dependency_prompt)
        response_text = response.content.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.rfind("```")
            response_text = response_text[start:end].strip()
        
        dependencies = json.loads(response_text)
        
        # Validate and limit dependencies
        if isinstance(dependencies, list):
            return dependencies[:max_dependencies]
        else:
            return []
            
    except Exception as e:
        print(f"Error generating dependencies for '{parent_question}': {str(e)}")
        return []


def build_dependency_research_tree(
    enhanced_query: str,
    model: BaseLanguageModel,
    max_depth: int = 4,
    max_dependencies_per_node: int = 4
) -> DependencyResearchTree:
    """
    Build a complete dependency research tree for the given query.
    
    Args:
        enhanced_query: The main research query
        model: LLM model for generating questions
        max_depth: Maximum tree depth
        max_dependencies_per_node: Maximum dependencies per question
    
    Returns:
        Complete dependency research tree
    """
    
    if not enhanced_query or not enhanced_query.strip():
        raise ValueError("Enhanced query cannot be empty")
    
    # Create the tree
    tree = DependencyResearchTree(enhanced_query, max_depth, max_dependencies_per_node)
    
    # Create root question
    root_question = DependencyQuestion(
        question_id="root",
        question_text=enhanced_query,
        question_type=QuestionType.ANALYTICAL,
        complexity_level=5,
        priority=1,
        search_keywords=enhanced_query.split()[:5],
        expected_answer_type="comprehensive analysis",
        is_prerequisite=False
    )
    
    root_node = DependencyNode("root", root_question)
    tree.set_root(root_node)
    
    # Queue for processing nodes (breadth-first approach)
    processing_queue = [(root_node, 0)]
    question_counter = 1
    
    print(f"Building dependency tree for: {enhanced_query}")
    
    while processing_queue:
        current_node, current_depth = processing_queue.pop(0)
        
        if current_depth >= max_depth:
            continue
        
        print(f"Processing depth {current_depth}: {current_node.question.question_text[:60]}...")
        
        # Generate dependency questions for current node
        dependencies_data = generate_dependency_questions(
            current_node.question.question_text,
            model,
            max_dependencies_per_node,
            current_depth,
            max_depth
        )
        
        # Create dependency nodes
        for dep_data in dependencies_data:
            question_id = f"q_{question_counter}"
            question_counter += 1
            
            dependency_question = DependencyQuestion(
                question_id=question_id,
                question_text=dep_data.get("question_text", ""),
                question_type=QuestionType(dep_data.get("question_type", "factual")),
                complexity_level=dep_data.get("complexity_level", 1),
                priority=dep_data.get("priority", 2),
                search_keywords=dep_data.get("search_keywords", []),
                expected_answer_type=dep_data.get("expected_answer_type", ""),
                is_prerequisite=True,
                metadata={"reasoning": dep_data.get("reasoning", "")}
            )
            
            dependency_node = DependencyNode(question_id, dependency_question)
            
            # Add to tree
            if tree.add_dependency_node(dependency_node, current_node.node_id):
                # Add to processing queue for further decomposition
                processing_queue.append((dependency_node, current_depth + 1))
    
    print(f"Dependency tree built with {tree.total_questions} questions")
    leaf_questions = tree.get_leaf_questions()
    print(f"Leaf questions (start here): {len(leaf_questions)}")
    
    return tree


# Real-world example usage
if __name__ == "__main__":
    from planner.v2.load_model import load_gemini_model
    from planner.v2.query_enhancer import enhance_search_query
    
    try:
        # Real-world research scenario
        original_query = "impact of renewable energy on global economy"
        
        print("="*80)
        print("DEPENDENCY-DRIVEN RESEARCH TREE GENERATOR")
        print("="*80)
        print(f"Original Query: {original_query}")
        print()
        
        # Load actual LLM model
        print("Loading Gemini model...")
        model = load_gemini_model()
        
        if model is None:
            print("Failed to load model. Please ensure GOOGLE_API_KEY is set and langchain-google-genai is installed.")
            exit(1)
        
        print("✓ Model loaded successfully")
        print()
        
        # Enhance the query
        print("Enhancing query...")
        enhanced_query = enhance_search_query(original_query, model)
        print(f"Enhanced Query: {enhanced_query}")
        print()
        
        # Generate dependency research tree
        print("Generating dependency research tree...")
        print("This may take a few moments as we build the question hierarchy...")
        print()
        
        dependency_tree = build_dependency_research_tree(
            enhanced_query,
            model,
            max_depth=3,
            max_dependencies_per_node=4
        )
        
        print("\n" + "="*80)
        print("GENERATED DEPENDENCY RESEARCH TREE")
        print("="*80)
        
        # Display the complete tree structure
        dependency_tree.print_tree()
        
        print("\n" + "="*80)
        print("RESEARCH EXECUTION STRATEGY")
        print("="*80)
        
        # Show leaf questions (starting points)
        leaf_questions = dependency_tree.get_leaf_questions()
        print(f"\n📋 STARTING RESEARCH QUESTIONS ({len(leaf_questions)} questions):")
        print("These are the foundational questions to research first:")
        print("-" * 60)
        for i, leaf in enumerate(leaf_questions, 1):
            print(f"{i:2d}. [{leaf.question.question_type.value.upper()}] {leaf.question.question_text}")
            if leaf.question.search_keywords:
                print(f"    🔍 Keywords: {', '.join(leaf.question.search_keywords)}")
            print()
        
        # Show execution order
        print("\n📈 COMPLETE EXECUTION ORDER (Bottom-up dependency resolution):")
        print("-" * 60)
        execution_order = dependency_tree.get_execution_order()
        for i, node in enumerate(execution_order, 1):
            indent = "  " * node.depth
            status_icon = "🎯" if node.depth == 0 else "📊" if node.depth == 1 else "🔍"
            print(f"{i:2d}. {indent}{status_icon} [{node.question.question_type.value.upper()}] {node.question.question_text}")
        
        # Show tree statistics
        print("\n" + "="*80)
        print("TREE ANALYTICS")
        print("="*80)
        progress = dependency_tree.get_progress()
        print(f"📊 Total Questions Generated: {progress['total_questions']}")
        print(f"🎯 Research Starting Points: {len(leaf_questions)}")
        print(f"📈 Ready to Resolve Initially: {progress['ready_to_resolve']}")
        print(f"🏗️  Maximum Tree Depth: {dependency_tree.max_depth}")
        print(f"🌿 Average Branching Factor: {dependency_tree.max_dependencies_per_node}")
        
        # Calculate complexity distribution
        complexity_dist = {}
        for node in dependency_tree.nodes.values():
            complexity = node.question.complexity_level
            complexity_dist[complexity] = complexity_dist.get(complexity, 0) + 1
        
        print(f"\n📊 Complexity Distribution:")
        for level in sorted(complexity_dist.keys()):
            print(f"   Level {level}: {complexity_dist[level]} questions")
        
        # Show research methodology
        print("\n" + "="*80)
        print("RECOMMENDED RESEARCH METHODOLOGY")
        print("="*80)
        print("1. 🔍 START: Research all leaf questions simultaneously")
        print("2. 📊 PROGRESS: Mark questions as resolved when answered")
        print("3. 🎯 ADVANCE: Move to next level when all dependencies are resolved")
        print("4. 🏆 COMPLETE: Final question synthesizes all findings")
        print()
        print("💡 This dependency structure ensures logical research progression")
        print("   and prevents attempting complex questions without proper foundation.")
        
        # Export tree data (optional)
        tree_data = dependency_tree.to_dict()
        print(f"\n📁 Tree data structure contains {len(tree_data)} top-level keys")
        print("   Available for export/analysis: tree, execution_order, leaf_questions, progress")
        
    except Exception as e:
        print(f"❌ Error in dependency tree generation: {e}")
        import traceback
        traceback.print_exc()