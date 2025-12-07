# Nion Orchestration Engine

L1 → L2 → L3 Task Orchestration Engine powered by OpenAI/GPT-OSS-120.

<img width="1909" height="930" alt="image" src="https://github.com/user-attachments/assets/8f3457d5-15b9-4707-80fd-4cc148def07b" />


## 🔐 Authentication (Feature Branch)
This branch (`feature/authentication`) implements a secure login system.

<img width="1919" height="931" alt="image" src="https://github.com/user-attachments/assets/a76b3038-1601-4537-9f70-e16fb4d09625" />

**Default Credentials:**
- **Username:** `admin`
- **Password:** `password123`

For the `feature/rbac` branch, use the following logins (Password is `password123` for ALL users):

| Username | Role | Access Level |
|----------|------|--------------|
| `admin` | Project Manager | Full Access |
| `engineer_bob` | Engineer | Technical Details |
| `designer_sue` | Designer | Visual Focus |
| `vp_alice` | VP Engineering | Strategic Summary |
| `customer_dave`| Customer | Sanitized Summary Only |

> **Note:** Credentials are managed via `backend/auth.py`.

## 🚀 Features

- **L1 Strategic Planning**: Breaks down messages into task plans
- **L2 Domain Routing**: Routes tasks to specialized L3 agents
- **L3 Extraction Agents**: Action items, risks, decisions, Q&A, evaluation
- **React Dashboard**: Modern dark-mode UI for message processing
- **SQLite Storage**: Persistent orchestration history

## 📁 Project Structure

```
Nion-Orchestration/
├── backend/           # Python FastAPI backend
│   ├── api.py         # FastAPI server
│   ├── main.py        # CLI interface
│   ├── config.py      # Configuration
│   ├── prompts.py     # LLM prompts
│   ├── llm/           # Groq client
│   ├── models/        # Pydantic models
│   ├── orchestration/ # L1, L2, L3 orchestrators
│   ├── rendering/     # Map renderer
│   ├── storage/       # SQLite storage
│   ├── samples/       # Test message samples
│   └── tests/         # Pytest tests
├── frontend/          # React Vite frontend
│   ├── src/           # React components
│   └── package.json   # Dependencies
└── README.md
```

## 🛠️ Setup

### Backend

```bash
cd backend
pip install -r requirements.txt

# Set your Groq API key
export GROQ_API_KEY="your_api_key_here"  # Linux/Mac
$env:GROQ_API_KEY="your_api_key_here"    # Windows PowerShell

# Run API server
python api.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🔧 Usage

1. Start the backend API: `cd backend && python api.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173
4. Enter a message or load a sample
5. Click "Process Message" to generate orchestration map

## 📋 Test Cases

The project includes 7 test cases from `testio.md`:
- MSG-001: Feature request with scope change
- MSG-101: Simple status question
- MSG-102: Feasibility question
- MSG-103: Priority decision
- MSG-104: Meeting transcript (multi-issue)
- MSG-105: Urgent escalation
- MSG-106: Ambiguous request

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLaMA 3 70B | Yes |

## 📄 License

MIT
