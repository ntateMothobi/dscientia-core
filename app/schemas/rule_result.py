from pydantic import BaseModel

class RuleResult(BaseModel):
    rule_id: str
    passed: bool
    weight: float
    explanation: str
