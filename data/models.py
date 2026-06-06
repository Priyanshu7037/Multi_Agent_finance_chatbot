from dataclasses import dataclass
from typing import List


@dataclass
class AgentOutput:
    agent_name: str
    score: float
    confidence: float
    recommendation: str
    strengths: List[str]
    weaknesses: List[str]
    reasoning: str