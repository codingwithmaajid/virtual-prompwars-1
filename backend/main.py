from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.copilot import router as copilot_router

app = FastAPI(title="VoteFlow AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(copilot_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": "website-root-6085972"}


static_dir = Path(__file__).resolve().parent / "static"
index_file = static_dir / "index.html"

FALLBACK_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>VoteFlow AI - Election Copilot</title>
    <style>
      :root {
        --ink: #17201c;
        --muted: #64726b;
        --line: #d8e2dc;
        --green: #145234;
        --accent: #d9851f;
        --blue: #2463a6;
        --paper: #fbfcfb;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: Arial, Helvetica, sans-serif;
        color: var(--ink);
        background: var(--paper);
      }
      .hero {
        min-height: 58vh;
        display: flex;
        align-items: end;
        padding: 56px clamp(20px, 6vw, 76px);
        color: white;
        background:
          linear-gradient(90deg, rgba(18, 40, 30, .9), rgba(18, 40, 30, .48)),
          linear-gradient(135deg, #145234, #2463a6);
      }
      .hero div { max-width: 760px; }
      .eyebrow {
        display: inline-block;
        border: 1px solid rgba(255,255,255,.32);
        padding: 8px 12px;
        font-size: 14px;
      }
      h1 {
        margin: 18px 0 12px;
        font-size: clamp(46px, 9vw, 96px);
        line-height: .96;
      }
      .hero p {
        margin: 0;
        max-width: 680px;
        font-size: 20px;
        line-height: 1.55;
        color: rgba(255,255,255,.9);
      }
      main {
        width: min(1180px, calc(100% - 32px));
        margin: -34px auto 40px;
        display: grid;
        grid-template-columns: 1fr 1.4fr;
        gap: 18px;
      }
      section {
        background: white;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 18px 48px rgba(23,32,28,.1);
      }
      h2 { margin: 0 0 12px; font-size: 20px; }
      label { display: grid; gap: 7px; margin: 0 0 14px; color: var(--muted); font-size: 13px; }
      input, select {
        min-height: 44px;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0 12px;
        font: inherit;
      }
      button {
        min-height: 46px;
        border: 0;
        border-radius: 8px;
        padding: 0 16px;
        background: var(--green);
        color: white;
        font-weight: 700;
        cursor: pointer;
      }
      .notice {
        padding: 12px;
        border-radius: 8px;
        background: #fff3e5;
        color: #70460d;
        margin-bottom: 14px;
      }
      .timeline {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin: 16px 0;
      }
      .timeline span {
        display: block;
        text-align: center;
        padding: 12px 6px;
        border-radius: 8px;
        background: #eaf5ee;
        color: var(--green);
        font-weight: 700;
      }
      .card {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 14px;
        margin-top: 10px;
      }
      .card h3 { margin: 0 0 6px; color: var(--blue); }
      .card p, li { color: var(--muted); line-height: 1.5; }
      .next {
        margin-top: 14px;
        padding: 16px;
        border-radius: 8px;
        background: var(--green);
        color: white;
        font-weight: 700;
      }
      @media (max-width: 800px) {
        main, .timeline { grid-template-columns: 1fr; }
      }
    </style>
  </head>
  <body>
    <header class="hero">
      <div>
        <span class="eyebrow">Process-only election guidance for India</span>
        <h1>VoteFlow AI</h1>
        <p>A guided election copilot that turns age, location, and voter status into a clear registration, verification, and voting-day plan.</p>
      </div>
    </header>
    <main>
      <section>
        <h2>Your Details</h2>
        <label>Age <input id="age" type="number" min="0" value="18" /></label>
        <label>Location <input id="location" value="Delhi, New Delhi" /></label>
        <label>Voter status
          <select id="status">
            <option value="not_sure">Not sure</option>
            <option value="registered">Registered</option>
            <option value="not_registered">Not registered</option>
          </select>
        </label>
        <label>Special situation
          <select id="edge">
            <option value="none">No special issue</option>
            <option value="changed_city">Changed city</option>
            <option value="lost_voter_id">Lost voter ID</option>
            <option value="missed_deadline">Missed deadline</option>
            <option value="name_not_found">Name not found</option>
          </select>
        </label>
        <button onclick="makePlan()">Generate Plan</button>
      </section>
      <section>
        <h2>AI Plan</h2>
        <div class="notice" id="statusBox">Enter your details to get your voting journey.</div>
        <div class="timeline"><span>Register</span><span>Verify</span><span>Vote</span><span>Result</span></div>
        <div class="card"><h3>Step-by-step Plan</h3><p id="steps">Registration, verification, and voting day guidance will appear here.</p></div>
        <div class="card"><h3>Required Documents</h3><ul><li>Age proof</li><li>Current address proof</li><li>Passport-size photo</li><li>EPIC/Voter ID if issued</li><li>Accepted photo ID for voting day</li></ul></div>
        <div class="next" id="next">Next Action: Check your voter status.</div>
      </section>
    </main>
    <script>
      function makePlan() {
        const age = Number(document.getElementById("age").value);
        const location = document.getElementById("location").value || "your constituency";
        const status = document.getElementById("status").value;
        const edge = document.getElementById("edge").value;
        const statusBox = document.getElementById("statusBox");
        const steps = document.getElementById("steps");
        const next = document.getElementById("next");
        if (age < 18) {
          statusBox.textContent = "You are not eligible to vote yet. You can prepare documents and register after turning 18.";
          steps.textContent = "Prepare age proof, address proof, and photo. Submit Form 6 after you turn 18.";
          next.textContent = "Next Action: Set a reminder to register when you turn 18.";
          return;
        }
        if (status === "registered") {
          statusBox.textContent = "You appear ready for verification in " + location + ".";
          next.textContent = "Next Action: Check your name in the electoral roll and save your polling booth details.";
        } else {
          statusBox.textContent = "You need to confirm or complete registration for " + location + ".";
          next.textContent = "Next Action: Submit Form 6 or search the electoral roll using your details.";
        }
        if (edge === "changed_city") next.textContent = "Next Action: Apply using your current address and track the application.";
        if (edge === "lost_voter_id") next.textContent = "Next Action: Check your name in the roll and carry an accepted photo ID on voting day.";
        if (edge === "missed_deadline") next.textContent = "Next Action: Check if applications are still open. If not, prepare for the next roll revision.";
        if (edge === "name_not_found") next.textContent = "Next Action: Search by EPIC, mobile, and name, then contact the Booth Level Officer if still missing.";
        steps.textContent = "1. Register with Form 6 if needed. 2. Verify your electoral roll entry. 3. Save booth details. 4. Carry accepted photo ID on voting day.";
      }
    </script>
  </body>
</html>
"""


@app.get("/", include_in_schema=False)
def frontend_index():
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse(FALLBACK_HTML)


if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
