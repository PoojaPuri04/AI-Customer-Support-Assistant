# AI-Powered Customer Support Workflow

A Python CLI demonstrating a four-stage AI customer support workflow for **Bloom Aesthetics Clinic**.

---

## What It Does

| Stage | Description |
|-------|-------------|
| **1. FAQ Answering** | Answers inbound questions using only the SOP (`sop.json`). Never hallucinates. |
| **2. Lead Qualification** | Asks 3 structured questions naturally within the conversation. |
| **3. Escalation Detection** | Detects complaints, out-of-scope questions, angry sentiment, medical questions, pricing negotiation, and explicit human requests. Logs to `escalation_log.json`. |
| **4. Conversation Summary** | Generates a structured JSON summary at session end: intent, key details, SOP gaps, next action, sentiment. |

---

## Project Structure

```
agentic-sop-bot/
├── main.py                   # Main workflow (CLI)
├── sop.json                  # SOP data for Bloom Aesthetics Clinic
├── requirements.txt
├── prompt_design.md          # Full prompt design and reasoning
├── README.md
├── escalation_log.json       # Auto-generated on escalation
├── summary_*.json            # Auto-generated session summaries
└── test_transcripts/
    ├── 01_in_sop_question.md
    ├── 02_out_of_scope.md
    ├── 03_escalation_angry.md
    ├── 04_lead_qualification.md
    └── 05_conversation_summary.md
```

---

## Setup

### Installation

```bash
git clone https://github.com/PoojaPuri04/agentic-sop-bot
cd agentic-sop-bot
pip install -r requirements.txt
```

### Set your API key


Open .env and fill in your key. Groq is free and the easiest to get started with — grab a key at console.groq.com.
GROQ_API_KEY=gsk_...
PROVIDER=groq
```

---

## Running the Workflow

### Interactive mode (recommended)

```bash
python main.py
```

Type your messages as a customer. Type `quit` or `exit` to end the session and generate the summary.

### Replay a test transcript

```bash
python main.py --transcript test_transcripts/01_in_sop_question.md
```

This replays the user lines from the transcript file automatically, useful for regression testing.

---

## SOP Data

The AI operates **exclusively** from `sop.json`. It covers:

- **Business:** Bloom Aesthetics Clinic
- **Hours:** Mon–Sat, 9 AM–7 PM
- **Services:** Botox (from £200), Fillers (from £250), Skin Boosters (from £180), Chemical Peels (from £80), Free Consultations
- **Booking:** WhatsApp or website. 24-hour cancellation policy.
- **Escalation triggers:** complaints, medical questions, pricing negotiation, out-of-scope, 2+ unanswered questions

See `sop.json` for the full data structure.

---

## Test Transcripts

| File | Scenario | Pass Criteria |
|------|----------|---------------|
| `01_in_sop_question.md` | Customer asks about Botox pricing | Answers from SOP only; correct price |
| `02_out_of_scope.md` | Customer asks about laser hair removal | Acknowledges gap; escalates |
| `03_escalation_angry.md` | Customer complains about treatment | Sentiment detected; escalates immediately |
| `04_lead_qualification.md` | Full qualification flow | 3 questions asked; summary populated |
| `05_conversation_summary.md` | Normal session ending | Summary has all required fields |

---

## Output Files

| File | Description |
|------|-------------|
| `escalation_log.json` | Appended every time an escalation occurs |
| `summary_YYYYMMDD_HHMMSS.json` | Saved at end of every session |

---

## Design Decisions and Trade-offs

See [`prompt_design.md`](./prompt_design.md) for the full write-up. Key decisions:

**JSON-only responses from Claude** — every turn returns a structured object. This makes escalation detection deterministic and removes ambiguity from application logic.

**Full SOP injection** — the entire `sop.json` is embedded in the system prompt. For this SOP size, full injection is more reliable than RAG (no retrieval errors, no partial context).

**Rule-based escalation** — rather than using a numeric confidence score (which LLMs can't reliably self-report), escalation is triggered by explicit rule matching: sentiment, topic type, and service coverage. More predictable for safety-critical decisions.

**Known limitations:**
- No persistence across sessions (each session is self-contained; summaries are saved to JSON)
- SOP is injected in full — if the SOP grows beyond ~10k tokens, RAG would be more efficient
- No streaming — responses arrive all at once; production would use streaming for better UX
- No authentication or rate limiting — appropriate for CLI demo scope

---

## Dependencies

- langchain, langchain-groq, langchain-google-genai, langchain-openai
- python-dotenv