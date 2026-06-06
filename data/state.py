from dataclasses import dataclass
from typing import Optional

from data.models import AgentOutput


@dataclass
class InvestmentState:

    ticker: str

    fundamental_result: Optional[AgentOutput] = None

    sentiment_result: Optional[AgentOutput] = None

    quant_result: Optional[AgentOutput] = None

    risk_result: Optional[AgentOutput] = None

    devil_result: Optional[AgentOutput] = None
    
    committee_reasoning: str = ""

    committee_confidence: float = 0

    final_score: float = 0

    final_decision: Optional[str] = None
    committee_votes: dict = None

    detected_conflicts: bool = False

    risk_level: str = ""

    committee_summary: str = ""
