# Wells Fargo Senior AI Engineer — Skills Reference

## Role Context
**Company:** Wells Fargo (via CAPCO)
**Title:** Senior Python-based AI Engineer
**Location:** Charlotte, NC | **Duration:** 12 months
**Key constraint:** Python-only stack (no Java). Regulated financial environment — auditability, compliance, and hallucination mitigation matter as much as capability.

---

## Required Skill Areas (Priority Order)

### 1. Foundation LLMs
**WF relevance:** Powers compliance Q&A, document analysis, fraud narrative generation.
Sub-topics: prompt engineering, context windows, temperature/sampling, fine-tuning vs RAG, tool use / function calling, system prompt design, few-shot patterns.

### 2. Advanced RAG / GraphRAG
**WF relevance:** Core of the role — ingesting regulatory docs, policy manuals, audit trails.
Sub-topics: chunking strategies (fixed, semantic, hierarchical), embedding models, rerankers (cross-encoders), GraphRAG (entity extraction → knowledge graph → graph traversal at query time), hybrid search (dense + sparse), citation grounding.

### 3. Embeddings at Scale
**WF relevance:** Millions of financial documents need fast semantic search.
Sub-topics: embedding models (text-embedding-3, BGE, E5), vector DBs (Pinecone, Weaviate, ChromaDB), HNSW index tuning, batch ingestion pipelines, cosine vs dot product similarity, embedding drift.

### 4. Knowledge Graphs & Ontology Extraction
**WF relevance:** Linking entities across regulatory frameworks, counterparties, risk categories.
Sub-topics: NER + relation extraction, RDF/OWL basics, SPARQL queries, Neo4j (Cypher), ontology design, connecting KGs to RAG pipelines.

### 5. Agentic AI Systems
**WF relevance:** "Autonomous/agentic AI solutions powering real AI products."
Sub-topics: ReAct loop, tool/function calling, multi-agent orchestration, LangChain agents, LlamaIndex agents, AutoGen, Claude Agent SDK, memory systems, guardrails & safety.

### 6. MCP Integrations
**WF relevance:** Explicitly listed in JD — connecting LLMs to internal tools and data.
Sub-topics: Model Context Protocol spec, writing MCP servers/clients in Python, tool schema design, authentication in MCP, connecting to internal APIs.

### 7. LLMOps / MLOps
**WF relevance:** "Production AI products" require CI/CD, monitoring, and observability.
Sub-topics: LangSmith (tracing, evaluation), Weights & Biases, prompt versioning, A/B testing prompts, latency/cost monitoring, drift detection, CI/CD for AI (GitHub Actions + model eval gates).

### 8. Scalable REST APIs
**WF relevance:** "Create scalable REST APIs" — Python-only backend.
Sub-topics: FastAPI (async, dependency injection, Pydantic v2), OpenAPI spec, rate limiting, auth (OAuth2/JWT), async Python (asyncio, httpx), API versioning.

### 9. Cloud Deployment
**WF relevance:** "Deploy AI workloads to cloud environments."
Sub-topics: AWS SageMaker (inference endpoints, batch transform), Azure ML (managed endpoints), GCP Vertex AI, containerizing AI apps (Docker + FastAPI), Lambda/Cloud Functions for serverless inference, IAM & secrets management.

### 10. Full-Stack Python
**WF relevance:** "Python-based full-stack solutions" — no Java, modern frontend.
Sub-topics: FastAPI backend + React or Angular frontend, async data loading, WebSockets for streaming LLM responses, Pydantic for schema sharing frontend↔backend, CORS, environment config.

---

## Suggested Learning Sequence

| Week | Focus |
|------|-------|
| 1-2 | Foundation LLMs + Prompt Engineering |
| 3-4 | RAG (basic → advanced chunking & reranking) |
| 5-6 | Embeddings at scale + Vector DBs |
| 7-8 | GraphRAG + Knowledge Graphs |
| 9-10 | Agentic AI Systems |
| 11   | MCP Integrations |
| 12   | LLMOps / MLOps (LangSmith, CI/CD) |
| 13-14 | Scalable REST APIs + Cloud Deployment |
| 15-16 | Full-stack integration project (end-to-end AI product) |

---

## Interview Themes to Expect

1. **Production LLM experience** — "Tell me about an LLM system you took to production. What broke?"
2. **Hallucination mitigation** — "How do you prevent hallucinations in a regulated banking context?"
3. **GraphRAG vs naive RAG** — "When would you choose GraphRAG over standard vector RAG?"
4. **Agentic safety** — "How do you prevent an agent from taking unintended actions?"
5. **LLM observability** — "How do you monitor prompt drift and output quality over time?"
6. **Scale challenges** — "How would you embed 50 million documents efficiently?"
7. **MCP specifics** — "Walk me through writing an MCP server that connects to an internal API."
8. **Cross-functional** — "Tell me about mentoring team members on AI systems."

---

## Key Libraries to Know

| Skill Area | Primary Libraries |
|------------|-------------------|
| LLMs | `anthropic`, `openai`, `litellm` |
| RAG | `llama-index`, `langchain`, `haystack` |
| Embeddings/Vector DB | `pinecone`, `weaviate-client`, `chromadb`, `sentence-transformers` |
| Knowledge Graphs | `neo4j`, `rdflib`, `spacy` (NER) |
| Agents | `anthropic` (Agent SDK), `langgraph`, `autogen` |
| LLMOps | `langsmith`, `wandb`, `mlflow` |
| APIs | `fastapi`, `pydantic`, `httpx`, `uvicorn` |
| Cloud | `boto3`, `azure-ai-ml`, `google-cloud-aiplatform` |
