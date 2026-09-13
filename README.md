# Oak & Ember Interiors — AI Sales Agent

## 1. Project Overview

An end-to-end AI furniture sales assistant for Oak & Ember Interiors. It accepts customer queries through Streamlit chat or Gmail, understands customer requirements, retrieves and ranks relevant products, validates recommendations, and returns a formatted response.

## 2. Architecture

```text
Customer
   │
   ├── Streamlit Chat
   │
   └── Gmail
        │
        ▼
     Guardrail
        │
        ▼
   Intent Detection
        │
        ▼
   Customer Needs
        │
        ▼
   Needs Validation
      │      │
      │      └── Clarify
      │
      ▼
   Product Retrieval
        │
        ▼
   Product Filtering
        │
        ▼
   Product Ranking
        │
        ▼
   Recommendation
        │
        ▼
   Recommendation Validation
        │
        ▼
   Final Response
      │      │
      ▼      ▼
 Streamlit  Gmail
```

## 3. Technology Stack

- **Python**
- **LangGraph** – agent workflow orchestration
- **LangChain** – LLM and tool integration
- **OpenAI** – LLM
- **FAISS** – vector database
- **Pandas** – product filtering and processing
- **Pydantic** – structured data validation
- **Streamlit** – chat UI
- **Gmail API** – email integration
- **Langfuse** – observability and tracing
- **LangSmith / Evaluation framework** – evaluation support

## 4. Agent Workflow

The LangGraph workflow contains:

1. Input guardrail
2. Intent classification
3. Customer needs extraction
4. Needs validation and clarification
5. Product retrieval
6. Product filtering
7. Product ranking
8. Recommendation generation
9. Recommendation validation
10. Final response generation

## 5. RAG Pipeline

```text
Customer Query
      │
      ▼
FAISS Similarity Search
      │
      ▼
Relevant Products
      │
      ▼
Category / Budget / Feature Filtering
      │
      ▼
Product Ranking
      │
      ▼
Eligible Products
      │
      ▼
LLM Recommendation
```

## 6. Guardrails

The input guardrail uses:

- Regex-based prompt-injection detection
- LLM-based classification
- Categories:
  - `safe`
  - `prompt_injection`
  - `unsafe`
  - `off_topic`

Blocked requests are routed to a dedicated response node.

## 7. Evaluation

A golden dataset of customer queries is used to evaluate the agent.

### Evaluation Metrics

- Correctness
- Relevance
- Hallucination
- Groundedness

Individual evaluation scores are recorded for each golden-dataset query and aggregated for overall evaluation results.

## 8. Observability

Langfuse is used to monitor the application, including:

- Agent workflow traces
- Important workflow spans
- LLM generations
- Guardrail results
- Retrieval information
- Evaluation scores
- Latency
- Token usage
- Model/cost information

## 9. Gmail Integration

The Gmail flow is:

```text
Customer Email
      │
      ▼
Gmail Processor
      │
      ▼
Extract Customer Query
      │
      ▼
Same Sales Agent Graph
      │
      ▼
Product Recommendation
      │
      ▼
Formatted Email Response
      │
      ▼
Customer
```

No human approval step is used.

## 10. Running the Application

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file containing the required OpenAI and Langfuse credentials.

### Start Streamlit

```bash
streamlit start_app.py
```

### Start Gmail Processing

```bash
python gmail_processor.py
```

The Streamlit interface handles chat-based queries, while the Gmail processor handles incoming customer emails.
