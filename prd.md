# PRD.md

## MVP Product Requirements Document — Nion Orchestration Engine

### 1. Purpose / Vision

A minimal working implementation of the L1 → L2 → L3 orchestration workflow described in the internship assessment. The MVP focuses on correctness and reproducibility using a simple Python+SQLite stack and Grok Cloud for reasoning.

### 2. Functional Requirements (MVP)

* Load message JSON input.
* L1: Use Grok Cloud to generate a minimal task plan.
* L2: Route tasks to appropriate L3 agent functions.
* L3: Implement basic extraction agents:

  * action_item_extraction
  * risk_extraction
  * decision_extraction
* Render final Orchestration Map text.
* Store outputs in SQLite.

### 3. Nonfunctional Requirements (MVP)

* Single-process local execution.
* Simple and readable codebase.
* No microservices, no containers, no distributed components.
* Deterministic output formatting.

### 4. Out of Scope

No CI/CD, Docker, Kubernetes, Prometheus, Grafana, Jaeger, Postgres, Kafka, Redis.

### 5. Tech Stack (Finalized)

* Python 3.10+
* Grok Cloud LLM
* SQLite
* Pydantic
* Typer (CLI)
* Pytest

