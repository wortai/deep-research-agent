"""
Mode types for router orchestration.

The router now orchestrates by mode (`search_mode`) rather than
intent classification. `edit` remains as a reserved path.
"""

from enum import Enum


class SearchMode(str, Enum):
    """Search modes provided by frontend."""
    
    WEBSEARCH = "websearch"
    DEEPSEARCH = "deepsearch"
    EXTREMESEARCH = "extremesearch"


class RouteMode(str, Enum):
    """Route targets supported by the main graph."""

    WEBSEARCH = "websearch"
    DEEPSEARCH = "deepsearch"
    EXTREMESEARCH = "extremesearch"
    EDIT = "edit"


def is_research_mode(mode: RouteMode) -> bool:
    """True when the mode requires a research workflow."""
    return mode in (RouteMode.WEBSEARCH, RouteMode.DEEPSEARCH, RouteMode.EXTREMESEARCH)


def requires_full_report(mode: RouteMode) -> bool:
    """True when the mode requires full report generation."""
    return mode in (RouteMode.DEEPSEARCH, RouteMode.EXTREMESEARCH)
