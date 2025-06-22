#!/usr/bin/env python3
"""
Simple runner for the architecture visualizer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the visualizer
from visualize_architecture import main

if __name__ == "__main__":
    main()
