# 🤖 AI Customer Support Assistant

An AI-powered customer support assistant designed to automate customer interactions, answer business-specific questions, qualify potential leads, detect situations requiring human assistance, and generate structured conversation summaries.

The project demonstrates how **Large Language Models (LLMs)** can be integrated with business SOPs to build a reliable and controlled customer-support workflow.

---

## 📌 Overview

The **AI Customer Support Assistant** is a Python-based conversational AI system that handles customer queries using predefined business information stored in an SOP.

Instead of allowing the LLM to answer from unrestricted knowledge, the assistant is instructed to respond using the provided SOP. This helps reduce hallucinations and keeps responses aligned with business policies.

The system also identifies situations where AI should not handle the conversation and automatically flags them for **human escalation**.

---

## 🎯 Objective

The goal of this project is to build an AI-driven customer support workflow that can:

* Answer customer FAQs using business-specific information
* Reduce hallucinations by grounding responses in an SOP
* Qualify potential customers through structured questions
* Detect complaints, medical queries, negative sentiment, and unsupported questions
* Escalate sensitive or out-of-scope conversations to a human
* Generate structured summaries of customer conversations

---

## ⚙️ Tech Stack

* **Python** – Core application development
* **LangChain** – LLM integration and workflow orchestration
* **Groq / OpenAI / Google Gemini** – LLM providers
* **JSON** – SOP storage, escalation logs, and conversation summaries
* **Prompt Engineering** – Controlling model behavior and structured responses
* **python-dotenv** – Environment variable and API key management

---

## 🧠 System Architecture

The workflow follows four main stages:

### 1. FAQ Answering

Customer questions are matched against information available in `sop.json`.

The assistant generates responses based only on the available SOP information, reducing unsupported or hallucinated answers.

### 2. Lead Qualification

The assistant naturally collects important customer information through structured questions during the conversation.

This helps identify the customer's requirements and potential interest in the available services.

### 3. Escalation Detection

The system detects conversations that require human intervention.

Escalation can be triggered by:

* Customer complaints
* Angry or negative sentiment
* Medical questions
* Pricing negotiations
* Explicit requests to speak with a human
* Questions outside the available SOP
* Multiple unanswered questions

Escalation events are stored in `escalation_log.json`.

### 4. Conversation Summary

At the end of each session, the assistant generates a structured JSON summary containing:

* Customer intent
* Important conversation details
* Lead qualification information
* SOP knowledge gaps
* Recommended next action
* Customer sentiment

---

## 🔄 Workflow

```text
Customer Query
      ↓
AI Customer Support Assistant
      ↓
Business SOP (sop.json)
      ↓
FAQ / Query Analysis
      ↓
Lead Qualification
      ↓
Escalation Detection
      ↓
AI Response
      ↓
Conversation Summary
```

---

## 📁 Project Structure

```text
AI-Customer-Support-Assistant/
│
├── main.py
├── sop.json
├── requirements.txt
├── prompt_design.md
├── README.md
├── escalation_log.json
│
├── summary_*.json
│
└── test_transcripts/
    ├── 01_in_sop_question.md
    ├── 02_out_of_scope.md
    ├── 03_escalation_angry.md
    ├── 04_lead_qualification.md
    └── 05_conversation_summary.md
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/PoojaPuri04/AI-Customer-Support-Assistant.git
cd AI-Customer-Support-Assistant
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add the API key for your selected LLM provider.

Example:

```env
GROQ_API_KEY=your_api_key
PROVIDER=groq
```

---

## ▶️ Run the Assistant

Start the interactive customer-support assistant:

```bash
python main.py
```

You can then interact with the assistant directly from the terminal.

Type:

```text
quit
```

or

```text
exit
```

to end the conversation.

A structured conversation summary will automatically be generated at the end of the session.

---

## 🧪 Testing

The project contains sample conversation transcripts covering different customer-support scenarios, including:

* FAQ questions
* Out-of-scope queries
* Angry customer escalation
* Lead qualification
* Conversation summarization

A transcript can be replayed using:

```bash
python main.py --transcript test_transcripts/01_in_sop_question.md
```

---

## 📊 Output

The system automatically generates structured output files.

### Escalation Log

```text
escalation_log.json
```

Stores conversations that require human intervention.

### Conversation Summary

```text
summary_YYYYMMDD_HHMMSS.json
```

Stores structured information about each completed customer conversation.

---

## 💡 Key Features

* AI-powered customer support
* SOP-grounded responses
* Reduced LLM hallucination
* Automated FAQ handling
* Lead qualification
* Sentiment-aware escalation
* Human escalation detection
* Multi-LLM provider support
* Structured JSON responses
* Automated conversation summarization
* Conversation logging

---

## 🔐 Reliability and Safety

The assistant uses controlled prompting and SOP-based responses rather than allowing unrestricted LLM answers.

Sensitive or unsupported requests can be escalated to a human instead of generating potentially unreliable responses.

This approach makes the workflow more suitable for customer-support applications where predictable AI behavior is important.

---

## ⚠️ Limitations

* Conversations are currently session-based
* Business knowledge is directly loaded from the SOP
* Large SOP datasets would benefit from a RAG-based retrieval system
* The current implementation uses a CLI interface
* Authentication and rate limiting are not implemented

---

## 🔮 Future Improvements

Future versions could include:

* RAG-based SOP retrieval for larger knowledge bases
* Vector database integration
* Web-based chat interface
* Persistent conversation memory
* Customer database/CRM integration
* Real-time streaming responses
* Analytics dashboard for customer interactions
* Advanced sentiment analysis

---

## 📌 Project Purpose

This project demonstrates the practical implementation of **LLMs, prompt engineering, LangChain, structured outputs, business knowledge grounding, and AI workflow automation** for building an intelligent customer-support system.
