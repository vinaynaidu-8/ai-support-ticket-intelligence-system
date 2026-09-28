# AI Support Ticket Intelligence System

An AI-powered enterprise support platform that investigates customer support tickets using authorized organizational knowledge, produces structured recommendations, and provides controlled tool and workflow capabilities for support operations.

The system is designed around a simple principle:

> **AI assists support engineers; authorization, application logic, and human roles remain in control of what the AI can access or execute.**

This project demonstrates practical implementation of **LLM integration, structured AI outputs, Retrieval-Augmented Generation (RAG), vector search, reranking, role-based access control, tool calling, controlled workflows, PostgreSQL, FastAPI, and AI application security principles**.

---

## 1. Project Overview

Enterprise support systems frequently require support engineers to combine information from:

* Customer tickets
* Internal technical documentation
* Troubleshooting procedures
* Service-health information
* Support policies
* Account information
* Previous ticket information
* Operational tools

A conventional ticket system stores this information but does not reason across it.

This project adds an AI intelligence layer that can:

1. Understand a support ticket.
2. Retrieve relevant organizational knowledge.
3. Rerank retrieved information for relevance.
4. Provide the relevant context to an LLM.
5. Generate a structured ticket analysis.
6. Produce recommended actions and customer responses.
7. Determine whether human escalation is appropriate.
8. Experiment with controlled tool calling.
9. Apply role-based authorization before protected operations.

The system deliberately uses **synthetic enterprise data and simulated operational tools** so that the architecture and security model can be demonstrated without exposing confidential company information or interacting with real production infrastructure.

---

# 2. Key Engineering Goals

The project was designed to demonstrate more than simply connecting an application to an LLM API.

The primary engineering goals are:

* Build a real backend application around an LLM.
* Keep AI output structured and machine-readable.
* Ground AI responses in authorized organizational knowledge.
* Reduce hallucination risk through RAG.
* Separate retrieval from generation.
* Use vector similarity search for semantic retrieval.
* Improve retrieval quality with reranking.
* Enforce authentication and authorization independently of the LLM.
* Prevent customers from accessing other customers' resources.
* Restrict support tools according to user roles.
* Keep AI recommendations separate from automatically executed actions.
* Demonstrate controlled tool calling.
* Demonstrate a bounded workflow rather than unrestricted autonomous behavior.
* Design the system so production hardening can be added without redesigning the core architecture.

---

# 3. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │       Client         │
                         │ Swagger / API Client │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │ Authentication/RBAC  │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             ┌────────────┐ ┌──────────────┐ ┌───────────────┐
             │ PostgreSQL │ │ Ticket Logic │ │ Authorization │
             │            │ │              │ │   Policies    │
             └─────┬──────┘ └──────┬───────┘ └───────────────┘
                   │               │
                   │               ▼
                   │       ┌───────────────────┐
                   │       │ AI Investigation  │
                   │       │    Orchestrator   │
                   │       └─────────┬─────────┘
                   │                 │
                   │       ┌─────────┴─────────┐
                   │       │                   │
                   ▼       ▼                   ▼
          ┌─────────────────────┐      ┌──────────────────┐
          │    RAG Pipeline     │      │   Gemini LLM     │
          │                     │      │                  │
          │ Chunking            │      │ Structured JSON  │
          │ Embeddings          │      │ Ticket Analysis  │
          │ Vector Search       │      └──────────────────┘
          │ Reranking           │
          │ Context Building    │
          └──────────┬──────────┘
                     │
                     ▼
             ┌───────────────┐
             │   pgvector    │
             │ Knowledge DB  │
             └───────────────┘

                     Optional / Controlled
                              │
                              ▼
                   ┌────────────────────┐
                   │    Tool Layer      │
                   │                    │
                   │ Tool Registry      │
                   │ Permissions         │
                   │ Executor            │
                   │ Simulated Actions  │
                   └────────────────────┘
```

---

# 4. End-to-End Request Flow

The main AI ticket investigation follows this flow:

```text
Customer Ticket
      │
      ▼
Authentication
      │
      ▼
Authorization
      │
      ▼
Ticket Access Validation
      │
      ▼
Build Search Query
      │
      ▼
Generate Query Embedding
      │
      ▼
Vector Similarity Search
      │
      ▼
Retrieve Candidate Knowledge
      │
      ▼
Cross-Encoder Reranking
      │
      ▼
Build Authorized Context
      │
      ▼
Gemini LLM
      │
      ▼
Structured AIAnalysis
      │
      ├── Summary
      ├── Category
      ├── Priority
      ├── Detected Issue
      ├── Recommended Action
      ├── Confidence
      ├── Human Escalation
      ├── Suggested Response
      └── Customer Response
      │
      ▼
Persist AI Analysis
      │
      ▼
Support Agent Reviews Result
```

The AI does not directly bypass the application security layer.

---

# 5. RAG Architecture

The knowledge pipeline is:

```text
Markdown Knowledge Documents
            │
            ▼
        Ingestion
            │
            ▼
         Chunking
            │
            ▼
      Sentence Embeddings
            │
            ▼
       384-D Vectors
            │
            ▼
       PostgreSQL
        + pgvector
            │
            ▼
    Cosine Similarity Search
            │
            ▼
     Candidate Documents
            │
            ▼
       Cross-Encoder
        Reranking
            │
            ▼
     Relevant Knowledge
            │
            ▼
     Context Construction
            │
            ▼
          Gemini
```

### Why RAG?

The LLM should not be expected to know company-specific:

* support procedures
* internal policies
* troubleshooting instructions
* service information
* escalation rules

RAG allows the application to retrieve relevant organizational information at request time and provide it to the model as context.

This also makes the knowledge layer independently updateable without retraining the model.

---

# 6. Knowledge Base

The project currently uses synthetic enterprise knowledge:

```text
knowledge/
├── api/
│   ├── authentication.md
│   └── rate-limiting.md
│
├── infrastructure/
│   └── service-health.md
│
└── support/
    └── escalation-policy.md
```

The knowledge includes topics such as:

* HTTP 401 authentication failures
* HTTP 429 rate limiting
* Service health
* Support troubleshooting procedures
* Escalation criteria
* Security-sensitive support practices

The knowledge base explicitly instructs support personnel not to request secrets such as API keys or passwords from customers.

---

# 7. Retrieval and Reranking

The retrieval pipeline uses two stages.

### Stage 1 — Vector Retrieval

The query is converted into an embedding using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The resulting 384-dimensional vector is compared against knowledge vectors stored in PostgreSQL using pgvector cosine distance.

The system first retrieves a larger candidate set.

Example:

```text
candidate_k = 10
```

### Stage 2 — Reranking

The retrieved candidates are then reranked using:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The system therefore separates:

```text
Broad semantic retrieval
        ↓
Candidate set
        ↓
Fine-grained relevance scoring
        ↓
Final context
```

This avoids relying exclusively on embedding similarity.

---

# 8. LLM Integration

The application uses Google's Gemini model through the Google GenAI SDK.

Current model configuration:

```text
gemini-3.6-flash
```

The model receives:

* Ticket subject
* Ticket description
* Current ticket category
* Current ticket priority
* Retrieved authorized knowledge

The model returns a structured response conforming to a Pydantic schema.

---

# 9. Structured AI Output

The AI response is validated using Pydantic.

The core structure contains:

```text
AIAnalysis
├── summary
├── suggested_category
├── suggested_priority
├── suggested_response
├── detected_issue
├── recommended_action
├── confidence
├── human_escalation
└── customer_response
```

This is important because the application does not treat an LLM response as arbitrary text.

Instead:

```text
LLM
  ↓
Structured JSON
  ↓
Schema Validation
  ↓
Application Logic
  ↓
Database
```

This makes AI output easier to validate, persist, inspect, and integrate with downstream application logic.

---

# 10. AI Safety and Control Rules

The LLM is explicitly instructed to:

* Use authorized company knowledge when relevant.
* Not invent company policies.
* Not invent technical facts.
* Not claim that it performed actions it cannot perform.
* Not invent system information.
* Not recommend unauthorized operational actions.
* Recommend human escalation when available information is insufficient.
* Avoid exposing confidential information.
* Avoid exposing internal reasoning.
* Treat retrieved knowledge as reference information rather than instructions that override application rules.
* Avoid requesting API keys or passwords from customers.

The application therefore uses **defense in depth** rather than relying on the prompt alone.

```text
Prompt Rules
     +
Structured Output Validation
     +
Application Authorization
     +
Tool Permissions
     +
Human Review
```

Prompt instructions are treated as one control layer, not as the security boundary.

---

# 11. Role-Based Access Control

The system contains four primary roles:

```text
Customer
Support Agent
Support Manager
Admin
```

## Customer

Customers can:

* Register.
* Authenticate.
* Create tickets.
* View their own tickets.
* View their own ticket conversations.
* Interact with their own tickets.

Customers cannot:

* Access other customers' tickets.
* Access internal agent endpoints.
* Assign tickets.
* Execute internal support tools.
* Manage users.

---

## Support Agent

Support agents can:

* Authenticate.
* View tickets assigned to them.
* View AI analysis for authorized tickets.
* Add ticket messages.
* Update permitted ticket state.
* Use authorized read-only support capabilities.

Support agents cannot:

* Assign tickets.
* Manage users.
* Execute manager-level operational actions.
* Access another agent's restricted tickets.

---

## Support Manager

Support managers can:

* Perform support management operations.
* Assign tickets to support agents.
* Manage operational support workflows.
* Execute authorized higher-privilege support tools.

---

## Admin

Administrators have the highest application-level privileges.

They can:

* Manage users.
* Create support agents.
* Create support managers.
* Create administrators.
* Perform administrative operations.
* Assign tickets.
* Execute authorized administrative operations.

---

# 12. Authorization Model

Authorization is enforced by the application, not by the LLM.

The conceptual model is:

```text
Request
   │
   ▼
JWT Authentication
   │
   ▼
Identify User
   │
   ▼
Identify Role
   │
   ▼
Check Resource Ownership / Assignment
   │
   ▼
Check Role Permission
   │
   ▼
Allow or Reject Operation
```

For example:

```text
Customer A
   │
   ├── Ticket A → allowed
   │
   └── Ticket B → denied

Agent A
   │
   ├── Assigned Ticket → allowed
   │
   └── Agent B Ticket → denied

Agent
   │
   └── Assign Ticket → denied

Support Manager
   │
   └── Assign Ticket → allowed
```

The system therefore combines:

* Authentication
* Role-based authorization
* Resource-level authorization
* Ticket ownership
* Ticket assignment
* Tool-level permissions

---

# 13. Tool Calling

The project includes a controlled tool-calling experiment demonstrating how an LLM can request application-defined functions.

Example tools include:

```text
get_service_health()
get_account_status()
get_database_status()
```

Controlled operational tools also exist for simulated environments:

```text
restart_test_service()
reset_test_account()
create_escalation()
```

These tools operate against a **simulated test environment**, not real infrastructure.

The important architectural principle is:

```text
LLM requests a tool
        │
        ▼
Application receives request
        │
        ▼
Tool registry validation
        │
        ▼
Role permission check
        │
        ▼
Argument validation
        │
        ▼
Tool execution
```

The LLM does not receive unrestricted access to Python functions or the operating system.

---

# 14. Tool Authorization

Tool permissions are role-dependent.

For example:

```text
                    Customer   Agent   Manager   Admin
-------------------------------------------------------
Read service health    No       Yes      Yes      Yes
Read account status    No       Yes      Yes      Yes
Read DB status        No       Yes      Yes      Yes
Restart test service   No       No       Yes      Yes
Reset test account    No       No       Yes      Yes
```

The exact permission model is implemented through the application's tool permission layer.

This demonstrates an important principle:

> **Tool availability is controlled by application authorization, not by the model's decision.**

---

# 15. Workflow Control

The project also contains a small controlled investigation workflow.

Conceptually:

```text
Ticket
  ↓
Retrieve Knowledge
  ↓
Rerank
  ↓
Generate AI Analysis
  ↓
Evaluate Escalation Requirement
  ↓
Optional Controlled Tool Operation
  ↓
Persist Analysis
```

The workflow contains a bounded tool-call limit:

```text
MAX_TOOL_CALLS = 3
```

This is intentionally a controlled workflow rather than an unrestricted autonomous agent.

A full autonomous support agent was deliberately not introduced because the project requirements do not justify uncontrolled multi-step autonomy.

---

# 16. Human-in-the-Loop Design

The AI does not automatically send its suggested response to the customer.

Instead:

```text
AI Analysis
     │
     ▼
Suggested Response
     │
     ▼
Support Agent Review
     │
     ▼
Human Decision
     │
     ▼
Customer Communication
```

Similarly, operational actions are separated from ordinary AI analysis.

This prevents an LLM generation error from automatically becoming a production action.

---

# 17. Security Design

Security considerations include:

### Authentication

JWT-based authentication is used for protected API endpoints.

Passwords are hashed rather than stored as plaintext.

### Authorization

The application verifies:

* User identity
* User role
* Resource ownership
* Ticket assignment
* Tool permissions

### Data Isolation

Customers cannot access another customer's tickets or conversations.

Agents cannot access tickets outside their authorized assignment.

### Secret Management

Sensitive configuration such as:

```text
DATABASE_URL
JWT_SECRET_KEY
GEMINI_API_KEY
```

is loaded through environment configuration.

`.env` is excluded from Git.

### AI Security Principles

The system explicitly considers:

* Prompt injection
* Unauthorized instructions inside retrieved content
* Data leakage
* Unauthorized operational actions
* Hallucinated technical information
* Insufficient knowledge
* Unsafe recommendations
* Secret exposure

Retrieved knowledge is treated as **reference context**, not as a mechanism for overriding application security rules.

---

# 18. Database Architecture

PostgreSQL is used as the primary database.

It stores application data such as:

* Users
* Tickets
* Ticket messages
* AI analyses
* Knowledge chunks

`pgvector` extends PostgreSQL with vector storage.

Knowledge chunks therefore contain:

```text
id
content
source
category
embedding
created_at
```

This allows relational application data and vector retrieval infrastructure to coexist within the same database platform.

---

# 19. Project Structure

```text
ai-support-ticket-intelligence-system/
│
├── app/
│   ├── config/
│   │   └── settings.py
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── ticket.py
│   │   ├── ticket_message.py
│   │   ├── ai_analysis.py
│   │   └── knowledge_chunk.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── ticket.py
│   │   └── ai_analysis.py
│   │
│   ├── security/
│   │   ├── auth.py
│   │   ├── jwt.py
│   │   ├── password.py
│   │   └── authorization.py
│   │
│   └── services/
│       ├── ai_analysis.py
│       ├── ai_orchestrator.py
│       │
│       ├── llm/
│       │   ├── gemini.py
│       │   ├── gemini_tools.py
│       │   └── test_gemini_tools.py
│       │
│       ├── rag/
│       │   ├── ingestion.py
│       │   ├── embedding.py
│       │   ├── index_knowledge.py
│       │   ├── search.py
│       │   ├── reranking.py
│       │   └── context.py
│       │
│       ├── tools/
│       │   ├── registry.py
│       │   ├── tool_permissions.py
│       │   ├── tool_executor.py
│       │   └── support_tools.py
│       │
│       └── workflow/
│           └── ticket_investigation.py
│
├── knowledge/
│   ├── api/
│   ├── infrastructure/
│   └── support/
│
├── requirements.txt
├── .gitignore
├── .env                 # local only, not committed
├── README.md
└── PROJECT_TROUBLESHOOTING.md
```

---

# 20. Technology Stack

| Layer             | Technology                 |
| ----------------- | -------------------------- |
| API               | FastAPI                    |
| Language          | Python                     |
| Database          | PostgreSQL                 |
| ORM               | SQLAlchemy                 |
| Vector Database   | PostgreSQL + pgvector      |
| Embeddings        | Sentence Transformers      |
| Reranking         | Cross-Encoder              |
| LLM               | Google Gemini              |
| LLM SDK           | Google GenAI SDK           |
| Validation        | Pydantic                   |
| Authentication    | JWT                        |
| Password Security | Password hashing           |
| API Testing       | Swagger / OpenAPI          |
| Environment       | Python virtual environment |
| Version Control   | Git / GitHub               |

---

# 21. Testing Performed

The implementation was tested progressively rather than only testing the final endpoint.

### Authentication

Tested:

* Valid registration
* Duplicate registration
* Valid login
* Invalid password
* Non-existent user
* Protected endpoint without JWT
* Protected endpoint with JWT

### Customer Authorization

Tested:

* Own-ticket access
* Cross-customer ticket access
* Cross-customer conversation access
* Unauthorized agent endpoints
* Unauthorized assignment

### Agent Authorization

Tested:

* Assigned-ticket access
* Unassigned-ticket restrictions
* AI analysis access
* Ticket messaging
* Ticket status updates
* Cross-agent isolation
* Unauthorized ticket assignment

### RAG

Tested:

* Document ingestion
* Chunk generation
* Embedding generation
* Vector storage
* PostgreSQL/pgvector retrieval
* Semantic similarity
* Reranking
* Context construction

### Tool Calling

Tested:

* Gemini tool selection
* Tool declaration
* Tool execution
* Tool response returned to Gemini
* Role-based tool permissions

### Workflow

Tested the controlled investigation workflow and bounded tool execution logic.

---

# 22. Example AI Investigation

For a ticket such as:

```text
Subject:
API returning HTTP 401 Unauthorized

Description:
Our application is receiving HTTP 401 Unauthorized responses
when calling the AcmeCloud API.
```

The system can retrieve relevant authentication knowledge:

```text
HTTP 401 → authentication failure
```

The retrieved knowledge is reranked and supplied to Gemini.

The resulting structured analysis can contain:

```text
Detected Issue:
API authentication failure

Recommended Action:
Verify credential validity, expiration and authentication
configuration.

Human Escalation:
false

Confidence:
0.95
```

The important distinction is that the model's response is generated using **retrieved organizational knowledge**, rather than relying only on the model's general knowledge.

---

# 23. Design Decisions

## Why PostgreSQL + pgvector?

The application already requires PostgreSQL for transactional data.

Using pgvector allows vector search to be added without introducing a separate vector database for this project's scale.

## Why RAG instead of fine-tuning?

The project requires access to changing company knowledge and policies.

RAG allows the knowledge base to be updated independently from the model.

Fine-tuning would not be the appropriate mechanism for frequently changing support documentation.

## Why reranking?

Embedding retrieval provides a useful candidate set but does not guarantee that the most relevant chunks are ordered perfectly.

A cross-encoder provides a second-stage relevance signal.

## Why structured output?

Free-form LLM text is difficult for deterministic application logic to consume safely.

Pydantic validation creates a contract between the LLM layer and the application layer.

## Why RBAC outside the LLM?

An LLM should never be the security boundary.

Authorization must be deterministic application logic.

## Why controlled tools instead of unrestricted agents?

Operational actions can have real consequences.

The project therefore demonstrates tool calling with explicit registration, permission checks and bounded execution rather than giving the model unrestricted autonomy.

---

# 24. AI Control Model

The project's AI architecture can be summarized as:

```text
                 ┌──────────────────────┐
                 │       LLM            │
                 │  Reasoning / Output  │
                 └──────────┬───────────┘
                            │
                 AI cannot bypass
                 application controls
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
      Structured Output             Tool Request
             │                             │
             ▼                             ▼
       Pydantic Validation          Permission Check
             │                             │
             ▼                             ▼
       Application Logic             Tool Executor
             │                             │
             └──────────────┬──────────────┘
                            ▼
                       Human Review
```

This separation is intentional.

The LLM can **recommend**.

The application decides whether the requested operation is **authorized**.

The human remains responsible for appropriate operational decisions where required.

---

# 25. What This Project Demonstrates

This project is intended to demonstrate practical understanding of:

* Backend API architecture
* Authentication and authorization
* RBAC
* Resource-level access control
* PostgreSQL
* SQLAlchemy
* Vector databases
* Embeddings
* Semantic search
* Reranking
* RAG
* Context construction
* Structured LLM output
* Gemini integration
* Tool calling
* Controlled workflows
* AI security principles
* Prompt injection awareness
* Data leakage prevention
* Human-in-the-loop design
* AI application architecture
* Separation of AI reasoning from application authorization

The objective is not simply:

> "Connect an LLM to an API."

The objective is to demonstrate how an LLM can be incorporated into a backend system while maintaining **data boundaries, authorization, structured interfaces, controlled execution, and human oversight**.

---

# 26. Current Scope and Deliberate Limitations

This repository is a learning and engineering demonstration rather than a production enterprise support platform.

The following are intentionally limited or deferred:

* Full production observability
* Distributed deployment
* Production-grade secret management
* Advanced rate limiting
* Comprehensive LLM evaluation pipelines
* Large-scale retrieval evaluation
* Production tool execution
* Persistent escalation-management infrastructure
* Fully autonomous support agents
* Production-grade retry/idempotency infrastructure
* High-scale caching
* Multi-region deployment

The tool actions currently operate against simulated/test environments.

These limitations are deliberate: the project focuses on demonstrating the architecture and engineering principles without introducing unnecessary infrastructure that is not required by the problem.

---

# 27. Future Production Hardening

A production implementation could add:

```text
Observability
    ↓
Metrics + Tracing + Structured Logs

Reliability
    ↓
Timeouts + Retries + Circuit Breakers
    ↓
Idempotent Tool Execution

Security
    ↓
Secrets Manager
    ↓
Advanced Prompt-Injection Detection
    ↓
Data-Loss Prevention
    ↓
Fine-Grained Authorization

AI Evaluation
    ↓
Retrieval Quality
    ↓
Reranking Quality
    ↓
Groundedness
    ↓
Response Quality
    ↓
Safety Evaluation

Scalability
    ↓
Caching
    ↓
Async Processing
    ↓
Queues
    ↓
Horizontal Scaling
```

These are extensions rather than assumptions about what the current project already implements.

---

# 28. Repository Philosophy

The architecture intentionally avoids treating every modern AI concept as a requirement.

The project distinguishes between:

```text
Learning a concept
       ≠
Experimenting with a concept
       ≠
Adding the concept to production runtime
```

A technology is added to the core system only when it has a clear engineering purpose.

For example:

* RAG → required because the AI needs organizational knowledge.
* pgvector → appropriate because vector retrieval is required.
* Reranking → useful for improving retrieval relevance.
* Structured output → required for reliable application integration.
* RBAC → required for enterprise access control.
* Tool calling → demonstrated in a controlled manner.
* Autonomous agents → not forced into the system because unrestricted autonomy is not required by the problem.

This keeps the architecture understandable and prevents unnecessary technology accumulation.

---

# 29. Running the Project

Create a Python virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure environment variables in `.env`:

```text
DATABASE_URL=...
JWT_SECRET_KEY=...
GEMINI_API_KEY=...
```

Start the FastAPI application:

```powershell
uvicorn app.main:app --reload
```

API documentation is available through FastAPI's generated Swagger/OpenAPI interface.

---

# 30. Project Status

### Core Application

* [x] FastAPI backend
* [x] PostgreSQL integration
* [x] SQLAlchemy models
* [x] JWT authentication
* [x] Password hashing
* [x] RBAC
* [x] Customer ticket isolation
* [x] Agent ticket assignment
* [x] Ticket conversations
* [x] AI analysis persistence

### LLM Engineering

* [x] Gemini integration
* [x] Structured LLM output
* [x] Pydantic validation
* [x] AI analysis pipeline
* [x] AI failure boundary

### RAG

* [x] Knowledge ingestion
* [x] Document chunking
* [x] Embeddings
* [x] PostgreSQL + pgvector
* [x] Semantic retrieval
* [x] Cross-encoder reranking
* [x] Context construction

### Controlled AI Operations

* [x] Tool registry
* [x] Tool permissions
* [x] Tool executor
* [x] Gemini tool-calling experiment
* [x] Controlled workflow experiment
* [x] Human-in-the-loop response design

### Deferred Production Work

* [ ] Full RAG evaluation
* [ ] Production observability
* [ ] Advanced reliability engineering
* [ ] Production tool execution
* [ ] Full AI evaluation pipeline
* [ ] Large-scale deployment architecture

---

# 31. Final Architecture Principle

The central design principle of this project is:

```text
                    AI
                     │
             Understand / Recommend
                     │
                     ▼
        ┌───────────────────────────┐
        │     Application Layer     │
        │                           │
        │ Authentication            │
        │ Authorization             │
        │ Validation                │
        │ Business Rules            │
        │ Tool Permissions          │
        │ Data Access Controls      │
        └─────────────┬─────────────┘
                      │
                      ▼
                 Execution
                      │
                      ▼
                Human Oversight
```

The system does not treat the LLM as the application itself.

Instead, the LLM is one component inside a controlled software architecture.

That distinction is the primary engineering focus of this project.
