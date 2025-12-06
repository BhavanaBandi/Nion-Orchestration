# design.md

## MVP System Design — Nion Orchestration Engine

### 1. Architecture Overview

A lightweight single-process system that preserves conceptual layers without actual service boundaries.

```
main.py
 ├── L1_orchestrator.py
 ├── L2_coordinator.py
 ├── L3_agents/
 │     ├── action_items.py
 │     ├── risks.py
 │     └── decisions.py
 ├── storage/
 │     └── db.sqlite
 └── render_map.py
```

### 2. Data Flow

1. Message is parsed from JSON.
2. L1 (Grok Cloud prompt) generates task plan.
3. L2 dispatches tasks to matching L3 agents.
4. L3 agents use Grok Cloud to extract structured information.
5. Results stored in SQLite.
6. Textual Orchestration Map rendered.

### 3. L1 Reasoning

Minimal Grok prompt generating JSON list of tasks.

### 4. L2 Coordination

Simple dictionary mapping domains to agent functions.

### 5. L3 Agents (MVP)

Each agent:

* Accepts content
* Calls Grok Cloud with a small prompt
* Returns structured Python dictionary

### 6. Storage

SQLite schema:

```
CREATE TABLE orchestration_maps (
  id INTEGER PRIMARY KEY,
  message_id TEXT,
  map_text TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

