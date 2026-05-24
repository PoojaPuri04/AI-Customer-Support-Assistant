"""
AI Customer Support Workflow  
==================================================================
"""

import argparse
import json
import os
import re
import textwrap
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()                          

# ── LangChain imports ─────────────────────────────────────────────────────────
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel

# ── Config ────────────────────────────────────────────────────────────────────
SOP_PATH  = Path(__file__).parent / "sop.json"
LOG_PATH  = Path(__file__).parent / "escalation_log.json"

with open(SOP_PATH) as f:
    SOP_TEXT = json.dumps(json.load(f), indent=2)

SYSTEM_PROMPT = f"""
You are Bloom, a friendly and professional customer support assistant for Bloom Aesthetics Clinic.
You speak with warmth, clarity, and professionalism — as a knowledgeable receptionist would.

════════════════════════════════════
  OPERATING RULES (follow exactly)
════════════════════════════════════

1. ONLY use the SOP data below to answer questions. Never invent prices, treatments,
   policies, or facts not present in the SOP. If information is missing, say so honestly.

2. ESCALATION — you MUST set "escalate": true and provide an "escalation_reason" in your
   JSON output whenever ANY of the following occur:
   • The customer asks a medical or clinical question (e.g. "is this safe if I'm pregnant?")
   • The customer expresses frustration, anger, a complaint, or distress
   • The customer explicitly asks to speak to a human or manager
   • The customer asks something you cannot answer from the SOP
   • You have already been unable to answer 2 or more questions in this conversation
   • The customer asks to negotiate pricing or requests a discount

3. RESPONSE FORMAT — every response MUST be valid JSON matching this schema:
{{
  "reply": "string — your message to the customer",
  "escalate": false,
  "escalation_reason": null,
  "stage": "faq | qualification | escalated | summary",
  "qualification_data": {{}}
}}

4. QUALIFICATION — after answering the customer's initial question(s), naturally
   transition to collecting lead information by asking 3 questions ONE AT A TIME:
   (a) Which treatment are you most interested in?
   (b) Have you had aesthetic treatments before?
   (c) Are you booking for yourself or someone else?

5. TONE — warm, reassuring, concise. Acknowledge feelings before giving information.

6. NEVER say "I don't know" without offering to connect them with the team.

════════════════════════════════════
  SOP DATA (your ONLY knowledge source)
════════════════════════════════════
{SOP_TEXT}
""".strip()


# ── Provider factory ──────────────────────────────────────────────────────────
def build_llm(provider: str) -> BaseChatModel:
    """
    Return a LangChain chat model.
    """
    provider = provider.lower()

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1024,
        )

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            max_output_tokens=1024,
        )
    elif provider == "openrouter":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="meta-llama/llama-3.3-70b-instruct:free",
            temperature=0.3,
            max_tokens=1024,
            openai_api_key=os.environ["OPENROUTER_API_KEY"],
            openai_api_base="https://openrouter.ai/api/v1",
        )

    else:
        raise ValueError(f"Unknown provider '{provider}'. Choose: groq, gemini, openrouter")


# ── LangChain message history helpers ────────────────────────────────────────
def build_lc_messages(history: list[dict]) -> list:
    """Convert our simple {role, content} dicts to LangChain message objects."""
    lc = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in history:
        if msg["role"] == "user":
            lc.append(HumanMessage(content=msg["content"]))
        else:
            lc.append(AIMessage(content=msg["content"]))
    return lc


def call_llm(llm: BaseChatModel, history: list[dict]) -> str:
    """Invoke the LangChain model and return the raw text response."""
    messages = build_lc_messages(history)
    response = llm.invoke(messages)
    return response.content


# ── Parse JSON from model reply ───────────────────────────────────────────────
def parse_response(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {
        "reply": raw,
        "escalate": False,
        "escalation_reason": None,
        "stage": "faq",
        "qualification_data": {},
    }


# ── Escalation logger ─────────────────────────────────────────────────────────
def log_escalation(reason: str, history: list[dict], extra: dict):
    log = []
    if LOG_PATH.exists():
        try:
            log = json.loads(LOG_PATH.read_text())
        except Exception:
            log = []
    log.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "reason": reason,
        "conversation_length": len(history),
        **extra,
    })
    LOG_PATH.write_text(json.dumps(log, indent=2))


# ── Session summary ───────────────────────────────────────────────────────────
def generate_summary(
    llm: BaseChatModel,
    history: list[dict],
    qualification_data: dict,
    escalated: bool,
    escalation_reason: str | None,
) -> dict:
    prompt = f"""
The customer support session has ended. Produce a structured summary as valid JSON:
{{
  "customer_intent": "one sentence",
  "key_details_collected": {{}},
  "sop_gaps": [],
  "escalated": {str(escalated).lower()},
  "escalation_reason": {json.dumps(escalation_reason)},
  "recommended_next_action": "string",
  "sentiment": "positive | neutral | negative"
}}

Qualification data: {json.dumps(qualification_data)}
Conversation: {json.dumps(history, indent=2)}
""".strip()

    raw = llm.invoke([HumanMessage(content=prompt)]).content
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return {"raw_summary": raw}


# ── UI helpers ────────────────────────────────────────────────────────────────
W = 72

def hr(c="─"): print(c * W)

def print_bot(text):    print(f"\n🌸 Bloom: {text}\n")
def print_user(text):   print(f"👤 You:   {text}")

def print_banner(provider):
    hr("═")
    print(f"  🌸  Bloom Aesthetics Clinic — AI Support")
    print("  Type 'quit' or 'exit' to end the session.")
    hr("═"); print()

def print_escalation(reason):
    hr(); print("  ⚠️  ESCALATION TRIGGERED"); print(f"  Reason: {reason}"); hr()

def print_summary(summary):
    hr("═"); print("  📋  SESSION SUMMARY"); hr("═")
    for k, v in summary.items():
        label = k.replace("_", " ").title()
        if isinstance(v, (dict, list)):
            v = textwrap.indent(json.dumps(v, indent=4), "        ")
            print(f"  {label}:\n{v}")
        else:
            print(f"  {label}: {v}")
    hr("═")


# ── Core conversation loop ────────────────────────────────────────────────────
def run_conversation(llm: BaseChatModel, provider: str, input_lines: list[str] | None = None):
    print_banner(provider)
    print_bot("Hi! I'm Bloom, your virtual assistant for Bloom Aesthetics Clinic. How can I help you today?")

    history: list[dict] = []
    qualification_data: dict = {}
    escalated = False
    escalation_reason: str | None = None
    idx = 0

    while True:
        # ── Input ─────────────────────────────────────────────────────────────
        if input_lines is not None:
            user_text = input_lines[idx].strip() if idx < len(input_lines) else "quit"
            idx += 1
            print_user(user_text)
        else:
            try:
                user_text = input("👤 You:   ").strip()
            except (EOFError, KeyboardInterrupt):
                user_text = "quit"

        if not user_text:
            continue
        if user_text.lower() in ("quit", "exit", "bye", "goodbye"):
            print_bot("Thank you for contacting Bloom Aesthetics Clinic. Have a wonderful day! 🌸")
            break

        # ── Call LLM via LangChain ────────────────────────────────────────────
        history.append({"role": "user", "content": user_text})
        raw    = call_llm(llm, history)
        parsed = parse_response(raw)

        reply          = parsed.get("reply", raw)
        should_escalate = parsed.get("escalate", False)
        esc_reason     = parsed.get("escalation_reason")
        q_data         = parsed.get("qualification_data", {})

        if isinstance(q_data, dict):
            qualification_data.update({k: v for k, v in q_data.items() if v})

        history.append({"role": "assistant", "content": raw})
        print_bot(reply)

        # ── Escalation ────────────────────────────────────────────────────────
        if should_escalate and not escalated:
            escalated = True
            escalation_reason = esc_reason or "Unspecified"
            print_escalation(escalation_reason)
            log_escalation(escalation_reason, history, {"qualification_data": qualification_data})
            print_bot(
                "I'm going to connect you with one of our team members who can help "
                "you further. They'll be in touch shortly. Is there anything else I "
                "can note down for them before I do?"
            )
            # One last user message before closing
            if input_lines is not None:
                if idx < len(input_lines):
                    last = input_lines[idx].strip(); idx += 1
                    print_user(last)
                    if last.lower() not in ("quit", "exit", "no", "nope", ""):
                        history.append({"role": "user", "content": last})
            else:
                try:
                    last = input("👤 You:   ").strip()
                    if last.lower() not in ("quit", "exit", "no", "nope", ""):
                        history.append({"role": "user", "content": last})
                except (EOFError, KeyboardInterrupt):
                    pass
            break

    # ── Summary ───────────────────────────────────────────────────────────────
    if history:
        print("\n⏳ Generating session summary...\n")
        summary = generate_summary(llm, history, qualification_data, escalated, escalation_reason)
        print_summary(summary)
        out = Path(__file__).parent / f"summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        out.write_text(json.dumps(summary, indent=2))
        print(f"\n  Summary saved → {out.name}")
    hr("═")


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Closira – LangChain edition")
    parser.add_argument(
        "--provider",
        default=os.getenv("PROVIDER", "groq"),   # falls back to .env value
        choices=["groq", "gemini", "openrouter"],
        help="LLM provider (default: value of PROVIDER in .env, else groq)",
    )
    parser.add_argument("--transcript", metavar="FILE", help="Replay a transcript file")
    args = parser.parse_args()

    print(f"\n  Loading provider: {args.provider} …")
    llm = build_llm(args.provider)
    print(f"  ✅  Ready.\n")

    if args.transcript:
        raw_lines = Path(args.transcript).read_text().splitlines()
        lines = []
        for line in raw_lines:
            if not line.strip() or line.strip().startswith("#"):
                continue
            for prefix in ("You:", "Customer:", "User:", "👤"):
                if line.strip().startswith(prefix):
                    line = line.split(":", 1)[-1].strip()
                    break
            lines.append(line)
        run_conversation(llm, args.provider, input_lines=lines)
    else:
        run_conversation(llm, args.provider)


if __name__ == "__main__":
    main()