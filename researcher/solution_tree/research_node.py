"""
Module for Research Node representation.
"""

from typing import List, Optional, Any

class Node:
    """
    Represents a node in the research tree.
    
    Each node corresponds to a query that needs to be resolved.
    Nodes can have children (sub-queries/gaps) and a parent.
    """
    
    def __init__(self, query: str, depth: int = 0, parent: Optional['Node'] = None):
        """
        Initialize a Research Node.

        Args:
            query (str): The research query for this node.
            depth (int): The depth of this node in the research tree.
            parent (Optional[Node]): The parent node of this node.
        """
        self.query: str = query
        self.depth: int = depth
        self.parent: Optional['Node'] = parent
        self.children: List['Node'] = []
        self.answer: Any = None  # This will be filled by the Solver
