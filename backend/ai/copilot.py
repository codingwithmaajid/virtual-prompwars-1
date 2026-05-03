import json
import os
from pathlib import Path

from models.schemas import ChatRequest, ChatResponse, PlanStep, UserContext, VotingPlan

RULES_PATH = Path(__file__).resolve().parents[1] / "data" / "election_rules.json"
RULES = json.loads(RULES_PATH.read_text())

SYSTEM_PROMPT = """You are VoteFlow AI, an India election copilot.
Stay non-political and unbiased. Explain only election process guidance.
Always answer with actionable next steps. Keep the language simple.
Cover registration, verification, voting day, dates, documents, and edge cases."""


def build_local_plan(context: UserContext) -> VotingPlan:
    age = context.age
    location = context.location.strip() or "your constituency"

    if age is not None and age < 18:
        return VotingPlan(
            current_status=f"You are {age}, so you cannot vote yet. You can prepare documents and register after turning 18.",
            step_by_step_plan=[
                PlanStep(title="Prepare", detail="Keep age proof, address proof, and a passport-size photo ready.", action="Set a reminder for your 18th birthday."),
                PlanStep(title="Register", detail="Submit Form 6 once you become eligible.", action="Apply through the official voter services portal."),
            ],
            important_dates=["Registration deadlines vary by election schedule.", "Check your state election schedule before each election."],
            required_documents=RULES["documents"][:3],
            next_action="Wait until you are 18, then submit Form 6.",
            warning=RULES["eligibility"],
        )

    steps = [
        PlanStep(
            title="Registration",
            detail="Submit Form 6 if you are a first-time voter or not registered at your current address.",
            action="Fill Form 6 and track the application.",
        ),
        PlanStep(
            title="Verification",
            detail=f"Search the electoral roll for {location} and confirm your name, EPIC number, and polling station.",
            action="Save your booth details and serial number.",
        ),
        PlanStep(
            title="Voting Day",
            detail="Carry an accepted photo ID and go only to your assigned polling booth.",
            action="Follow the queue process and cast your vote.",
        ),
    ]

    if context.voter_status == "registered":
        current_status = f"You appear ready for verification in {location}."
        next_action = "Check your name in the electoral roll and save your polling booth details."
    elif context.voter_status == "not_registered":
        current_status = f"You need to register before you can vote in {location}."
        next_action = "Submit Form 6 for your current address, then track the application."
    else:
        current_status = f"Your voter status is unclear. First confirm whether your name is on the electoral roll for {location}."
        next_action = "Search the electoral roll using name, mobile, or EPIC details."

    edge_guidance = {
        "changed_city": ("Changed city: use your current address and update your electoral roll entry.", "Apply for enrollment at your current address and track the application status."),
        "lost_voter_id": ("Lost voter ID: you can still vote if your name is on the roll and you carry accepted photo ID.", "Check your name in the roll, note your EPIC details, and request replacement EPIC if needed."),
        "missed_deadline": ("Missed deadline: you may not be able to vote in the current election if the roll is frozen.", "Check if applications are still open. If not, prepare for the next revision."),
        "name_not_found": ("Name not found: resolve this before voting day.", "Search by EPIC, mobile, and name. If still missing, contact the Booth Level Officer or file the relevant form."),
    }
    warning = None
    if context.edge_case in edge_guidance:
        warning, next_action = edge_guidance[context.edge_case]

    return VotingPlan(
        current_status=current_status,
        step_by_step_plan=steps,
        important_dates=[
            "Registration: before the electoral roll deadline for your constituency.",
            "Verification: after application acceptance and before polling day.",
            "Voting day: as announced by the Election Commission for your constituency.",
            "Results: on the officially announced counting date.",
        ],
        required_documents=RULES["documents"],
        next_action=next_action,
        warning=warning,
    )


def answer_locally(request: ChatRequest) -> ChatResponse:
    message = request.message.lower()
    plan = build_local_plan(request.context)
    if "political" in message or "party" in message or "candidate" in message:
        return ChatResponse(answer="I can only help with the election process, not political opinions or candidate recommendations.")
    if "city" in message or "moved" in message or "changed" in message:
        return ChatResponse(answer="Use your current address. Apply for enrollment or shifting as applicable, then verify your name in the new constituency roll.")
    if "lost" in message:
        return ChatResponse(answer="First confirm your name is on the electoral roll. If it is, carry an accepted photo ID on voting day and request a replacement EPIC separately.")
    if "deadline" in message or "date" in message:
        return ChatResponse(answer="Deadlines depend on the constituency schedule. Check whether registration is still open before the roll is frozen for that election.")
    if "document" in message or "id" in message:
        return ChatResponse(answer="Keep these ready: " + ", ".join(plan.required_documents) + ".")
    return ChatResponse(answer=plan.next_action)


async def answer_with_gemini(request: ChatRequest) -> ChatResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return answer_locally(request)

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        prompt = {
            "system": SYSTEM_PROMPT,
            "rules": RULES,
            "context": request.context.model_dump(),
            "question": request.message,
        }
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=json.dumps(prompt),
        )
        return ChatResponse(answer=response.text.strip())
    except Exception:
        return answer_locally(request)
