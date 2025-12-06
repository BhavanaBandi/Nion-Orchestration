# overview.md

## Overview — MVP Orchestration Engine

### What This MVP Does

Takes a message JSON → runs minimal L1→L2→L3 orchestration using Grok Cloud → outputs Orchestration Map text.

### How to Run

```
python main.py --input samples/MSG-001.json
```

Output stored in:

```
output/MSG-001_orchestration.txt
```

### Project Structure

```
.
├── main.py
├── L1_orchestrator.py
├── L2_coordinator.py
├── L3_agents/
├── storage/db.sqlite
└── docs/
```

### Extending the MVP

* Add more L3 agents
* Add minimal FastAPI wrapper if needed
* Later replace SQLite or add caching
