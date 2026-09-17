"""
multi_agent_system.agents
=========================
Module tập hợp 4 Agent chính của hệ thống Multi-Agent Code Generation:
- BaseAgent: Agent cơ sở
- PlannerAgent: Lập kế hoạch kiến trúc đa tệp, tích hợp GraphRAG & Language Detector
- CoderAgent: Sinh mã nguồn từng tệp tin theo thứ tự Topo (Python, Java, C)
- TesterAgent: Sinh mã nguồn kiểm thử đa tệp (Test Harness)
- ReviewerAgent: Thẩm định lỗi, phân định người sai: Planner (Global), Coder (Local), Tester (Testcase)
"""

from .base_agent import BaseAgent
from .planner_agent import PlannerAgent
from .coder_agent import CoderAgent
from .tester_agent import TesterAgent
from .reviewer_agent import ReviewerAgent

__all__ = [
    "BaseAgent",
    "PlannerAgent",
    "CoderAgent",
    "TesterAgent",
    "ReviewerAgent"
]
