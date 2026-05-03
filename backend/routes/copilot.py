from fastapi import APIRouter

from ai.copilot import answer_with_gemini, build_local_plan
from models.schemas import ChatRequest, ChatResponse, UserContext, VotingPlan

router = APIRouter()


@router.post("/plan", response_model=VotingPlan)
def create_plan(context: UserContext) -> VotingPlan:
    return build_local_plan(context)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await answer_with_gemini(request)


@router.get("/timeline")
def timeline() -> dict[str, list[str]]:
    return {"items": ["Register", "Verify", "Vote", "Result"]}
