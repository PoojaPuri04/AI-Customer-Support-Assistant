# Test Transcript 2 — Out-of-Scope Question
# Expected behaviour: AI acknowledges the gap and escalates rather than guessing
════════════════════════════════════════════════════════════════════════
  🌸  Bloom Aesthetics Clinic — AI Support
  Type 'quit' or 'exit' to end the session.
════════════════════════════════════════════════════════════════════════


🌸 Bloom: Hi! I'm Bloom, your virtual assistant for Bloom Aesthetics Clinic. How can I help you today?

👤 You:   Do you offer laser hair removal?

🌸 Bloom: I've checked our services, and unfortunately, we don't currently offer laser hair removal at Bloom Aesthetics Clinic. Our treatments include Botox, Dermal Fillers, Skin Boosters, and Chemical Peels. If you're interested in learning more about these options, I'd be happy to help. Alternatively, I can try to find out if we have any plans to introduce laser hair removal in the future.

────────────────────────────────────────────────────────────────────────
  ⚠️  ESCALATION TRIGGERED
  Reason: The customer asked about a treatment not listed in the SOP
────────────────────────────────────────────────────────────────────────

🌸 Bloom: I'm going to connect you with one of our team members who can help you further. They'll be in touch shortly. Is there anything else I can note down for them before I do?

👤 You:   quit

⏳ Generating session summary...

════════════════════════════════════════════════════════════════════════
  📋  SESSION SUMMARY
════════════════════════════════════════════════════════════════════════
  Customer Intent: The customer inquired about laser hair removal services.
  Key Details Collected:
        {}
  Sop Gaps:
        [
            "Laser hair removal treatment is not listed in the SOP"
        ]
  Escalated: True
  Escalation Reason: The customer asked about a treatment not listed in the SOP
  Recommended Next Action: Find out if there are plans to introduce laser hair removal in the future or provide alternative treatment options
  Sentiment: neutral
════════════════════════════════════════════════════════════════════════

  Summary saved → summary_20260524_043005.json
════════════════════════════════════════════════════════════════════════