"""
Terminal display for streaming progress visualization.

Renders multi-agent progress bars in the terminal for 
development testing without a frontend UI.
"""

import sys
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentDisplayState:
    """Visual state for one research agent progress bar."""

    query_num: int
    query: str
    percentage: int = 0
    phase: str = "starting"
    current_step: str = ""


class TerminalDisplay:
    """
    Terminal-based progress display for parallel research agents.
    
    Renders a box with progress bars for each active agent,
    similar to the reference multi-agent progress UI.
    """
    
    BOX_WIDTH = 70
    PROGRESS_BAR_WIDTH = 20
    
    def __init__(self):
        """Initialize display with empty agent states."""
        self._agents: Dict[int, AgentDisplayState] = {}
        self._current_phase: str = "initializing"
        self._total_queries: int = 0
        self._completed_queries: int = 0
        self._last_render_lines: int = 0
        self._start_time: datetime = datetime.now()
    
    def set_phase(self, phase: str) -> None:
        """Update the current workflow phase."""
        self._current_phase = phase.upper()
        self._render()
    
    def set_total_queries(self, count: int) -> None:
        """Set total number of research queries."""
        self._total_queries = count
    
    def update_agent(
        self,
        query_num: int,
        query: str,
        percentage: int,
        phase: str = "",
        current_step: str = ""
    ) -> None:
        """
        Update progress for a specific agent.
        
        Args:
            query_num: Agent/query identifier.
            query: Research query text.
            percentage: Progress 0-100.
            phase: Current agent phase.
            current_step: Description of current activity.
        """
        if query_num not in self._agents:
            self._agents[query_num] = AgentDisplayState(
                query_num=query_num,
                query=query
            )
        
        agent = self._agents[query_num]
        agent.percentage = min(100, max(0, percentage))
        agent.phase = phase or agent.phase
        agent.current_step = current_step or agent.current_step
        
        if percentage >= 100:
            self._completed_queries = sum(
                1 for a in self._agents.values() if a.percentage >= 100
            )
        
        self._render()
    
    def complete_agent(self, query_num: int) -> None:
        """Mark an agent as complete."""
        if query_num in self._agents:
            self._agents[query_num].percentage = 100
            self._agents[query_num].phase = "complete"
            self._completed_queries = sum(
                1 for a in self._agents.values() if a.percentage >= 100
            )
            self._render()
    
    def _create_progress_bar(self, percentage: int) -> str:
        """Generate ASCII progress bar."""
        filled = int(self.PROGRESS_BAR_WIDTH * percentage / 100)
        empty = self.PROGRESS_BAR_WIDTH - filled
        return f"[{'█' * filled}{'░' * empty}]"
    
    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text with ellipsis if needed."""
        if len(text) <= max_len:
            return text
        return text[:max_len - 3] + "..."
    
    def _clear_previous(self) -> None:
        """Clear previous render output."""
        if self._last_render_lines > 0:
            sys.stdout.write(f"\033[{self._last_render_lines}A")
            sys.stdout.write("\033[J")
            sys.stdout.flush()
    
    def _render(self) -> None:
        """Render the progress display to terminal."""
        self._clear_previous()
        
        lines = []
        
        top_border = "┌" + "─" * (self.BOX_WIDTH - 2) + "┐"
        lines.append(top_border)
        
        title = "DEEP RESEARCH AGENT - Progress Monitor"
        title_line = f"│ {title:<{self.BOX_WIDTH - 4}} │"
        lines.append(title_line)
        
        separator = "├" + "─" * (self.BOX_WIDTH - 2) + "┤"
        lines.append(separator)
        
        elapsed = datetime.now() - self._start_time
        elapsed_str = f"{int(elapsed.total_seconds())}s"
        phase_line = f"│ Phase: {self._current_phase:<20} Elapsed: {elapsed_str:<15} │"
        lines.append(phase_line)
        
        lines.append(f"│{' ' * (self.BOX_WIDTH - 2)}│")
        
        if not self._agents:
            waiting = "Waiting for agents to start..."
            lines.append(f"│ {waiting:<{self.BOX_WIDTH - 4}} │")
        else:
            sorted_agents = sorted(self._agents.values(), key=lambda a: a.query_num)
            for agent in sorted_agents:
                query_display = self._truncate(agent.query, 30)
                progress_bar = self._create_progress_bar(agent.percentage)
                
                agent_line = f"AGENT {agent.query_num + 1}: {query_display}"
                agent_line = f"{agent_line:<42} {progress_bar} {agent.percentage:>3}%"
                agent_line = f"│ {agent_line:<{self.BOX_WIDTH - 4}} │"
                lines.append(agent_line)
                
                if agent.current_step and agent.percentage < 100:
                    step_display = self._truncate(agent.current_step, self.BOX_WIDTH - 10)
                    step_line = f"│   └─ {step_display:<{self.BOX_WIDTH - 10}} │"
                    lines.append(step_line)
        
        lines.append(f"│{' ' * (self.BOX_WIDTH - 2)}│")
        
        overall = f"Overall: {self._completed_queries}/{self._total_queries or len(self._agents)} queries complete"
        lines.append(f"│ {overall:<{self.BOX_WIDTH - 4}} │")
        
        bottom_border = "└" + "─" * (self.BOX_WIDTH - 2) + "┘"
        lines.append(bottom_border)
        
        output = "\n".join(lines)
        print(output)
        sys.stdout.flush()
        
        self._last_render_lines = len(lines)
    
    def finish(self, message: str = "Complete!") -> None:
        """Display completion message and stop updates."""
        self._current_phase = "COMPLETE"
        self._render()
        print(f"\n✅ {message}\n")
