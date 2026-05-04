# VoteFlow AI - Election Copilote📋️

VoteFlow AI is a non-political AI election copilot for India. It guides users through the voting process in a personalized, step-by-step way using age, location, voter status, and special situations such as changed city, lost voter ID, missed deadline, or missing roll entry.

The goal is not to build a generic chatbot. VoteFlow AI is a decision-driven guided workflow that always tells the user what to do next.

## Product Summary

Millions of first-time voters and moved-city voters struggle to understand:

- How to register as a voter
- Whether they are eligible to vote
- Which forms and documents they need
- How to verify their electoral roll entry
- What to do on voting day
- What fallback steps exist if something goes wrong

VoteFlow AI simplifies this into a structured journey:

1. Registration
2. Verification
3. Voting day preparation
4. Results timeline awareness

The assistant stays neutral and process-only. It does not provide political opinions, party recommendations, candidate recommendations, or campaign content.

## Core Features

- Personalized voting journey based on age, location, and voter status
- Guided input flow for first-time and confused voters
- AI plan sections:
  - Current Status
  - Step-by-step Plan
  - Important Dates
  - Required Documents
  - Next Action
- Timeline UI: `Register -> Verify -> Vote -> Result`
- Chat panel with quick questions
- Edge-case handling:
  - Changed city
  - Lost voter ID
  - Missed deadline
  - Name not found in electoral roll
- FastAPI backend with deterministic local fallback
- Optional Google Gemini integration using `GEMINI_API_KEY`
- Dockerfile included for deployment

## Tech Stack

Frontend:

- Next.js
- React
- TypeScript
- CSS
- Lucide React icons

Backend:

- FastAPI
- Pydantic
- Uvicorn
- Google GenAI SDK

Deployment target:

- Docker
- Google Cloud Run

## Project Structure

```text
.
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── styles.css
├── backend/
│   ├── ai/
│   │   └── copilot.py
│   ├── data/
│   │   └── election_rules.json
│   ├── models/
│   │   └── schemas.py
│   ├── routes/
│   │   └── copilot.py
│   ├── main.py
│   └── requirements.txt
├── Dockerfile
├── next.config.mjs
├── package.json
├── tsconfig.json
└── README.md
```

## Requirements

Install these before running locally:

- Node.js 20 or newer
- npm
- Python 3.11 or newer
- pip

This project was generated and tested locally with:

- Node.js `v25.8.0`
- npm `11.11.0`
- Python `3.14.3`

## Local Setup

Install frontend dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

## Backend Setup

From the project root:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend runs at:

```text
http://localhost:8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Environment Variables

The backend works without any environment variables by using deterministic local guidance.

Optional Gemini variables:

```bash
export GEMINI_API_KEY="your-google-gemini-api-key"
export GEMINI_MODEL="gemini-2.5-flash"
```

If `GEMINI_API_KEY` is not set, `/chat` automatically falls back to local rule-based answers.

## API Reference

### `GET /health`

Checks whether the backend is running.

Response:

```json
{
  "status": "ok"
}
```

### `POST /plan`

Creates a personalized voting journey.

Request:

```json
{
  "age": 19,
  "location": "Delhi, New Delhi",
  "voter_status": "not_sure",
  "edge_case": "none"
}
```

Allowed `voter_status` values:

- `registered`
- `not_registered`
- `not_sure`

Allowed `edge_case` values:

- `none`
- `changed_city`
- `lost_voter_id`
- `missed_deadline`
- `name_not_found`

Example:

```bash
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "age": 19,
    "location": "Delhi, New Delhi",
    "voter_status": "not_sure",
    "edge_case": "none"
  }'
```

Response shape:

```json
{
  "current_status": "Your voter status is unclear...",
  "step_by_step_plan": [
    {
      "title": "Registration",
      "detail": "Submit Form 6...",
      "action": "Fill Form 6 and track the application."
    }
  ],
  "important_dates": [
    "Registration: before the electoral roll deadline for your constituency."
  ],
  "required_documents": [
    "Age proof if registering for the first time"
  ],
  "next_action": "Search the electoral roll using name, mobile, or EPIC details.",
  "warning": null
}
```

### `POST /chat`

Answers election process questions using Gemini when configured, otherwise local fallback.

Request:

```json
{
  "message": "I lost my voter ID. Can I still vote?",
  "context": {
    "age": 21,
    "location": "Mumbai, Maharashtra",
    "voter_status": "registered",
    "edge_case": "lost_voter_id"
  }
}
```

Example:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I lost my voter ID. Can I still vote?",
    "context": {
      "age": 21,
      "location": "Mumbai, Maharashtra",
      "voter_status": "registered",
      "edge_case": "lost_voter_id"
    }
  }'
```

Response:

```json
{
  "answer": "First confirm your name is on the electoral roll..."
}
```

### `GET /timeline`

Returns the standard VoteFlow journey stages.

Example:

```bash
curl http://localhost:8000/timeline
```

Response:

```json
{
  "items": ["Register", "Verify", "Vote", "Result"]
}
```

## Build Verification

Frontend production build:

```bash
npm run build
```

Backend compile check:

```bash
python3 -m py_compile backend/main.py backend/routes/copilot.py backend/models/schemas.py backend/ai/copilot.py
```

## Docker

Build the Docker image:

```bash
docker build -t voteflow-ai .
```

Run the container:

```bash
docker run --rm -p 8080:8080 voteflow-ai
```

Open:

```text
http://localhost:8080/health
```

Current Docker behavior:

- The Dockerfile builds the Next.js frontend.
- The runtime container starts the FastAPI backend on port `8080`.

If you want one Cloud Run service to serve both the frontend and backend, add a static export or proxy setup before deploying. For a demo, the simplest approach is:

- Deploy backend to Cloud Run.
- Deploy frontend separately to Vercel, Firebase Hosting, or another Cloud Run service.

## Google Cloud Run Deployment

### 1. Install and Login

Install the Google Cloud CLI, then authenticate:

```bash
gcloud auth login
gcloud auth configure-docker
```

Set your project:

```bash
gcloud config set project YOUR_PROJECT_ID
```

Enable required services:

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 2. Create Artifact Registry Repository

Set variables:

```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="asia-south1"
export REPO="voteflow"
export SERVICE="voteflow-ai"
```

Create a Docker repository:

```bash
gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="VoteFlow AI container images"
```

### 3. Build and Push Image

Build with Cloud Build:

```bash
gcloud builds submit \
  --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE:latest"
```

### 4. Deploy to Cloud Run

Deploy without Gemini:

```bash
gcloud run deploy "$SERVICE" \
  --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE:latest" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080
```

Deploy with Gemini:

```bash
gcloud run deploy "$SERVICE" \
  --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE:latest" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars GEMINI_MODEL=gemini-2.5-flash,GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

For production, store `GEMINI_API_KEY` in Secret Manager instead of passing it directly in the command.

### 5. Test Cloud Run

After deployment, Cloud Run prints a service URL.

Test health:

```bash
curl https://YOUR_CLOUD_RUN_URL/health
```

Test plan:

```bash
curl -X POST https://YOUR_CLOUD_RUN_URL/plan \
  -H "Content-Type: application/json" \
  -d '{
    "age": 20,
    "location": "Bengaluru, Karnataka",
    "voter_status": "not_registered",
    "edge_case": "changed_city"
  }'
```

## GitHub Push

Initialize git if needed:

```bash
git init
git add .
git commit -m "Initial VoteFlow AI election copilot"
```

Create a GitHub repository, then connect and push:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/voteflow-ai.git
git push -u origin main
```

## Safety and Neutrality Rules

VoteFlow AI must:

- Stay non-political
- Avoid opinions about parties, candidates, ideologies, or campaigns
- Focus only on voting process guidance
- Ask clarifying questions when user context is missing
- Always provide a clear next action
- Remind users that final deadlines and polling schedules depend on their constituency and official election notifications

## Known Limitations

- The frontend currently uses local in-browser planning logic for the demo UI.
- The backend exposes the API but is not yet wired into the frontend fetch flow.
- Exact election dates are not hardcoded because they vary by state, constituency, and current election schedule.
- Users should verify deadlines and polling details with official Election Commission sources.

## Roadmap

- Connect the frontend plan and chat UI directly to FastAPI endpoints
- Add official election schedule data source
- Add state-specific document guidance
- Add multilingual support for Hindi and major Indian languages
- Add Secret Manager based Cloud Run deployment
- Add automated tests for edge cases

## License

Add a license before publishing if this project will be open source.
