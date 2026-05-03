from typing import Literal

from pydantic import BaseModel, Field

VoterStatus = Literal["registered", "not_registered", "not_sure"]
EdgeCase = Literal["none", "changed_city", "lost_voter_id", "missed_deadline", "name_not_found"]


class UserContext(BaseModel):
    age: int | None = Field(default=None, ge=0, le=130)
    location: str = Field(default="", max_length=120)
    voter_status: VoterStatus = "not_sure"
    edge_case: EdgeCase = "none"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    context: UserContext


class PlanStep(BaseModel):
    title: str
    detail: str
    action: str


class VotingPlan(BaseModel):
    current_status: str
    step_by_step_plan: list[PlanStep]
    important_dates: list[str]
    required_documents: list[str]
    next_action: str
    warning: str | None = None


class ChatResponse(BaseModel):
    answer: str
