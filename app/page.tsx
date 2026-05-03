"use client";

import { useMemo, useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  BadgeCheck,
  CalendarDays,
  CheckCircle2,
  FileText,
  HelpCircle,
  MapPin,
  MessageCircle,
  Search,
  ShieldCheck,
  UserRound
} from "lucide-react";

type VoterStatus = "registered" | "not_registered" | "not_sure";
type EdgeCase = "none" | "changed_city" | "lost_voter_id" | "missed_deadline" | "name_not_found";

type Profile = {
  age: string;
  location: string;
  status: VoterStatus;
  edgeCase: EdgeCase;
};

type Plan = {
  currentStatus: string;
  steps: { title: string; detail: string; action: string }[];
  dates: string[];
  documents: string[];
  nextAction: string;
  warning?: string;
};

const initialProfile: Profile = {
  age: "",
  location: "",
  status: "not_sure",
  edgeCase: "none"
};

const timeline = ["Register", "Verify", "Vote", "Result"];

const quickQuestions = [
  "I changed cities. What should I do?",
  "I lost my voter ID.",
  "My name is not in the roll.",
  "What documents can I carry?"
];

function buildPlan(profile: Profile): Plan {
  const age = Number(profile.age);
  const isAgeMissing = !profile.age;
  const isUnder18 = !isAgeMissing && age < 18;
  const location = profile.location.trim() || "your constituency";

  if (isUnder18) {
    return {
      currentStatus: `You are ${age}, so you cannot vote yet. You can prepare documents and register once you turn 18.`,
      steps: [
        {
          title: "Prepare",
          detail: "Keep age proof, address proof, and a passport-size photo ready.",
          action: "Set a reminder for your 18th birthday."
        },
        {
          title: "Register",
          detail: "After turning 18, submit Form 6 as a new voter.",
          action: "Apply through the Election Commission voter services portal."
        }
      ],
      dates: [
        "Registration deadlines vary by election schedule.",
        "Check your state election schedule before each election."
      ],
      documents: ["Age proof", "Address proof", "Passport-size photo"],
      nextAction: "Wait until you are 18, then submit Form 6.",
      warning: "Only Indian citizens who are 18+ and registered in the electoral roll can vote."
    };
  }

  const baseSteps = [
    {
      title: "Registration",
      detail:
        profile.status === "registered"
          ? "You may not need a new registration, but your roll entry should still be checked."
          : "Submit Form 6 if you are a first-time voter or not currently registered.",
      action: profile.status === "registered" ? "Go to verification." : "Fill Form 6 for your current address."
    },
    {
      title: "Verification",
      detail: `Search the electoral roll for ${location} and confirm your name, EPIC number, and polling station.`,
      action: "Save your booth details and serial number."
    },
    {
      title: "Voting Day",
      detail: "Carry an accepted photo ID, reach the assigned polling booth, and follow the queue process.",
      action: "Vote only at your assigned polling station."
    }
  ];

  const edgePlans: Record<EdgeCase, Partial<Plan>> = {
    none: {},
    changed_city: {
      warning: "Changed city: your old voter entry should not be used for voting in your new city.",
      nextAction: "Apply for enrollment at your current address and track the application status."
    },
    lost_voter_id: {
      warning: "Lost voter ID: you can still vote if your name is on the roll and you carry an accepted photo ID.",
      nextAction: "Check your name in the roll, note your EPIC details, and request a replacement voter ID if needed."
    },
    missed_deadline: {
      warning: "Missed deadline: you may not be able to vote in the current election if the roll is frozen.",
      nextAction: "Check if applications are still open. If not, prepare documents and apply for the next revision."
    },
    name_not_found: {
      warning: "Name not found: do not wait until voting day to resolve it.",
      nextAction: "Search using EPIC, mobile, and name. If still missing, contact the Booth Level Officer or file the right form."
    }
  };

  return {
    currentStatus:
      profile.status === "registered"
        ? `You appear ready for verification in ${location}.`
        : profile.status === "not_registered"
          ? `You need to register before you can vote in ${location}.`
          : `Your voter status is unclear, so first confirm whether your name is on the electoral roll for ${location}.`,
    steps: baseSteps,
    dates: [
      "Registration: before the electoral roll deadline for your constituency.",
      "Verification: after your application is accepted and before polling day.",
      "Voting day: as announced by the Election Commission for your constituency.",
      "Results: on the officially announced counting date."
    ],
    documents: [
      "Age proof if registering for the first time",
      "Current address proof",
      "Passport-size photo",
      "EPIC/Voter ID if already issued",
      "Accepted photo ID for voting day"
    ],
    nextAction:
      profile.status === "registered"
        ? "Check your name in the electoral roll and save your polling booth details."
        : "Submit Form 6 for your current address, then track the application.",
    ...edgePlans[profile.edgeCase]
  };
}

function answerQuestion(question: string, plan: Plan) {
  const lower = question.toLowerCase();
  if (lower.includes("changed") || lower.includes("city")) {
    return "Use your current address. Apply for enrollment or correction for the new constituency, then verify your name in the new electoral roll before polling day.";
  }
  if (lower.includes("lost")) {
    return "A lost voter ID does not automatically stop you from voting. First confirm your name is on the roll, then carry an accepted photo ID and apply for a replacement EPIC if needed.";
  }
  if (lower.includes("name")) {
    return "Search by EPIC, mobile number, and name. If your name is still missing, contact the Booth Level Officer or submit the relevant application before the deadline.";
  }
  if (lower.includes("document") || lower.includes("id")) {
    return `Keep these ready: ${plan.documents.join(", ")}.`;
  }
  if (lower.includes("deadline") || lower.includes("date")) {
    return "Deadlines depend on your constituency and election schedule. Check the current Election Commission schedule and complete registration before the roll deadline.";
  }
  return plan.nextAction;
}

export default function Home() {
  const [profile, setProfile] = useState<Profile>(initialProfile);
  const [started, setStarted] = useState(false);
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState<{ role: "user" | "assistant"; text: string }[]>([
    { role: "assistant", text: "Share your age, location, and voter status to get a personalized plan." }
  ]);

  const plan = useMemo(() => buildPlan(profile), [profile]);
  const completion = profile.status === "registered" ? 2 : profile.status === "not_sure" ? 1 : 0;

  function updateProfile<K extends keyof Profile>(key: K, value: Profile[K]) {
    setProfile((current) => ({ ...current, [key]: value }));
  }

  function sendMessage(text = question) {
    const clean = text.trim();
    if (!clean) return;
    setChat((items) => [
      ...items,
      { role: "user", text: clean },
      { role: "assistant", text: answerQuestion(clean, plan) }
    ]);
    setQuestion("");
  }

  return (
    <main>
      <section className="hero">
        <div className="heroContent">
          <div className="eyebrow">
            <ShieldCheck size={16} />
            Process-only election guidance for India
          </div>
          <h1>VoteFlow AI</h1>
          <p>
            A guided election copilot that turns age, location, and voter status into a clear registration,
            verification, and voting-day plan.
          </p>
          <button className="primaryButton" onClick={() => setStarted(true)}>
            Start your voting journey <ArrowRight size={18} />
          </button>
        </div>
      </section>

      <section className="workspace" aria-label="Voting journey workspace">
        <div className="inputPanel">
          <div className="panelHeader">
            <h2>Your Details</h2>
            <span>Personalized plan input</span>
          </div>

          <label>
            <span><UserRound size={16} /> Age</span>
            <input
              type="number"
              min="0"
              placeholder="18"
              value={profile.age}
              onChange={(event) => updateProfile("age", event.target.value)}
              onFocus={() => setStarted(true)}
            />
          </label>

          <label>
            <span><MapPin size={16} /> State, city or district</span>
            <input
              placeholder="Example: Delhi, New Delhi"
              value={profile.location}
              onChange={(event) => updateProfile("location", event.target.value)}
              onFocus={() => setStarted(true)}
            />
          </label>

          <div className="fieldGroup">
            <span>Voter status</span>
            <div className="segmented">
              {[
                ["registered", "Registered"],
                ["not_registered", "Not registered"],
                ["not_sure", "Not sure"]
              ].map(([value, label]) => (
                <button
                  key={value}
                  className={profile.status === value ? "active" : ""}
                  onClick={() => {
                    updateProfile("status", value as VoterStatus);
                    setStarted(true);
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <label>
            <span><HelpCircle size={16} /> Special situation</span>
            <select
              value={profile.edgeCase}
              onChange={(event) => updateProfile("edgeCase", event.target.value as EdgeCase)}
              onFocus={() => setStarted(true)}
            >
              <option value="none">No special issue</option>
              <option value="changed_city">Changed city</option>
              <option value="lost_voter_id">Lost voter ID</option>
              <option value="missed_deadline">Missed deadline</option>
              <option value="name_not_found">Name not found</option>
            </select>
          </label>
        </div>

        <div className="planPanel">
          <div className="panelHeader">
            <h2>AI Plan</h2>
            <span>{started ? "Generated from your inputs" : "Ready when you start"}</span>
          </div>

          {plan.warning && (
            <div className="notice">
              <AlertCircle size={18} />
              <span>{plan.warning}</span>
            </div>
          )}

          <div className="statusBlock">
            <h3>Current Status</h3>
            <p>{plan.currentStatus}</p>
          </div>

          <div className="timeline">
            {timeline.map((item, index) => (
              <div className={index <= completion ? "timelineItem done" : "timelineItem"} key={item}>
                <span>{index <= completion ? <CheckCircle2 size={18} /> : index + 1}</span>
                <p>{item}</p>
              </div>
            ))}
          </div>

          <div className="sectionTitle">
            <FileText size={18} />
            <h3>Step-by-step Plan</h3>
          </div>
          <div className="stepGrid">
            {plan.steps.map((step) => (
              <article className="stepCard" key={step.title}>
                <h4>{step.title}</h4>
                <p>{step.detail}</p>
                <strong>{step.action}</strong>
              </article>
            ))}
          </div>

          <div className="split">
            <div>
              <div className="sectionTitle">
                <CalendarDays size={18} />
                <h3>Important Dates</h3>
              </div>
              <ul>{plan.dates.map((date) => <li key={date}>{date}</li>)}</ul>
            </div>
            <div>
              <div className="sectionTitle">
                <BadgeCheck size={18} />
                <h3>Required Documents</h3>
              </div>
              <ul>{plan.documents.map((doc) => <li key={doc}>{doc}</li>)}</ul>
            </div>
          </div>

          <div className="nextAction">
            <span>Next Action</span>
            <p>{plan.nextAction}</p>
          </div>
        </div>

        <aside className="chatPanel">
          <div className="panelHeader">
            <h2>Chat</h2>
            <span>Ask process questions</span>
          </div>
          <div className="quickGrid">
            {quickQuestions.map((item) => (
              <button key={item} onClick={() => sendMessage(item)}>
                {item}
              </button>
            ))}
          </div>
          <div className="messages">
            {chat.map((item, index) => (
              <div className={item.role === "assistant" ? "message assistant" : "message user"} key={`${item.role}-${index}`}>
                {item.text}
              </div>
            ))}
          </div>
          <div className="chatInput">
            <MessageCircle size={18} />
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") sendMessage();
              }}
              placeholder="Ask about registration, documents, deadlines..."
            />
            <button aria-label="Send question" onClick={() => sendMessage()}>
              <Search size={18} />
            </button>
          </div>
        </aside>
      </section>
    </main>
  );
}
