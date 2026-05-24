# Prompt Design Document

**Project:** Bloom Aesthetics Clinic AI Support Workflow  
**Model:** LLama 3.1 8B-instant
**Author:** Pooja Puri

---

## 1. Full System Prompt

```
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
{
  "reply": "string — your message to the customer",
  "escalate": false,
  "escalation_reason": null,
  "stage": "faq | qualification | escalated | summary",
  "qualification_data": {}   // only populate during qualification stage
}

4. QUALIFICATION — after answering the customer's initial question(s), naturally
   transition to collecting lead information by asking the three qualification questions
   one at a time. Store answers as they are given.

5. TONE — warm, reassuring, concise. No jargon. Never be dismissive. Acknowledge
   feelings before giving information.

6. NEVER say "I don't know" without also offering to connect them with the team.

════════════════════════════════════
  SOP DATA (ONLY knowledge source)
════════════════════════════════════
[Full JSON contents of sop.json appended here at runtime]
```

---

## 2. Design Decisions and Rationale

### 2.1 Structured JSON Output (Every Turn)

**Decision:** The model is instructed to always return a JSON object — never free text.

**Rationale:**  
- Separates AI reasoning from application logic cleanly. The Python code can reliably extract `escalate`, `stage`, and `qualification_data` without fragile regex parsing on natural language.  
- Makes escalation detection deterministic: the field either exists and is `true`, or it doesn't — no ambiguity.  
- Enables the workflow to be multi-stage without separate API calls per stage. The `stage` field tells the application layer where in the funnel the conversation is.  
- In production, this JSON contract could be enforced with Anthropic's structured output feature or a schema validator.

---

### 2.2 Hallucination Prevention

**The core challenge:** LLMs have broad world knowledge and will naturally fill gaps by generating plausible-sounding but fabricated information — especially for prices, policies, or clinical facts.

**Mechanisms used:**

| Technique | Implementation |
|-----------|----------------|
| **SOP injection** | The full `sop.json` is appended verbatim to the system prompt. The model has no need to "guess" — all valid answers are present. |
| **Explicit prohibition** | Rule 1 states: *"Never invent prices, treatments, policies, or facts not present in the SOP."* This is direct, not implied. |
| **Honesty instruction** | *"If information is missing, say so honestly."* This gives the model a valid path that isn't fabrication. |
| **Escalation as the fallback** | When the model can't answer, it escalates — it doesn't guess. This rewires the "can't answer → make something up" pattern into "can't answer → escalate." |
| **Gap logging in summary** | The session summary explicitly asks for `"sop_gaps"` — questions the AI couldn't answer. This creates accountability and surfaces missing SOP content for improvement. |

**What we deliberately avoid:** Using retrieval (RAG) for this scope. The SOP is small enough to fit in context, and retrieval introduces failure modes (wrong chunk retrieved, partial context). Full injection is more reliable for a focused SMB SOP.

---

### 2.3 Confidence-Based Escalation

Rather than a numerical confidence score (which is unreliable from LLMs without calibration), we use **explicit flag + rule-based triggers**:

```json
{
  "escalate": true,
  "escalation_reason": "Customer asked a medical question not covered by SOP"
}
```

**Why not a confidence threshold?**  
Claude doesn't expose raw logprob confidence scores via the standard API. Asking it to self-rate confidence (e.g., "rate your certainty 0–10") produces inconsistent results that aren't reliable for safety-critical decisions.

**Our escalation triggers (defined in system prompt):**

1. **Medical/clinical questions** — any question about safety, contraindications, medications, or side effects. These require a qualified practitioner; the AI should never answer them.
2. **Negative sentiment / complaints** — frustration, anger, distress detected in language. Prioritises customer care over conversation continuation.
3. **Explicit human request** — customer says "I want to speak to someone" — always honoured immediately.
4. **Out-of-scope questions** — anything not answerable from SOP data. Single occurrence triggers escalation; we don't accumulate errors.
5. **Pricing negotiation** — discounts and negotiation are relationship decisions that require a human.

**Escalation is logged** with timestamp, reason, and partial session summary to `escalation_log.json` for review.

---

### 2.4 Tone and Persona

**Persona:** *Bloom* — a warm, knowledgeable clinic receptionist.

**Design choices:**

- **Name** gives the bot a distinct identity appropriate for an aesthetics brand (matches clinic name).
- **"Warm, reassuring, concise"** — SMB customers aren't enterprise buyers; they want to feel comfortable asking questions about personal aesthetic treatments. Clinical/corporate language would feel cold.
- **"Acknowledge feelings before giving information"** — a key customer service principle, especially important when a customer expresses concern or distress. This prevents the bot from feeling robotic.
- **"Never be dismissive"** — aesthetics clients may feel vulnerable asking about appearance-related treatments; the tone must validate their enquiry.
- **No jargon** — "hyaluronic acid" is SOP terminology; the bot should translate it to plain language when possible.

---

## 3. Workflow Architecture

```
Customer Message
      │
      ▼
[Stage: FAQ Answering]
  Answer from SOP only
  Detect escalation triggers
      │
      ├─── escalate: true ──► [Stage: Escalated]
      │                         Log reason
      │                         Connect to human message
      │                         Break loop
      ▼
[Stage: Lead Qualification]
  Ask 3 questions, one per turn
  Collect and store answers
      │
      ▼
[Session End: quit/exit]
      │
      ▼
[Stage: Summary]
  Structured session summary
  customer_intent, key_details, sop_gaps,
  escalated, recommended_next_action, sentiment
```

---

## 4. SOP Data Design

The SOP is stored as `sop.json` and extends the brief with:

| Addition | Reason |
|----------|--------|
| Skin Boosters & Chemical Peels | Realistic treatment menu; tests handling of additional services |
| FAQs section | Allows the model to answer common questions precisely |
| Escalation triggers listed explicitly | Injected into prompt for transparent grounding |
| Lead qualification questions listed | Consistent question set, easy to update |

---

## 5. Known Limitations and Trade-offs

| Limitation | Mitigation |
|------------|-----------|
| No persistent memory across sessions | Each session is self-contained; summary is saved to disk |
| JSON parsing can fail if model adds commentary | Robust parser with regex fallback in `parse_response()` |
| Confidence is rule-based, not probabilistic | More predictable than score-based thresholds for SMB use |
| SOP in system prompt grows with data | Fine for current scope; move to RAG if SOP exceeds ~10k tokens |
| No real-time sentiment NLP library | Claude's own language understanding used; more pragmatic for a demo |
| Single-threaded CLI | Appropriate for scope; production would use async + message queues |
