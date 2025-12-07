# Nion Orchestration Engine

L1 → L2 → L3 Task Orchestration Engine powered by OpenAI/GPT-OSS-120.
<img width="1903" height="925" alt="image" src="https://github.com/user-attachments/assets/e748f0ee-0a1d-4d64-af0c-f73cf7607301" />


## 🔐 Authentication & RBAC

The system implements Role-Based Access Control (RBAC) with JWT authentication.

<img width="1919" height="931" alt="image" src="https://github.com/user-attachments/assets/a76b3038-1601-4537-9f70-e16fb4d09625" />

**Test Credentials:**
Password for ALL users is: `password123`

| Username | Role | Dashboard View | Permissions |
|----------|------|----------------|-------------|
| `admin` | Project Manager | Full Orchestration Map | Full Access, Create Projects |
| `engineer_bob` | Engineer | Action Items & Risks | View Technical Details, No Admin |
| `vp_alice` | VP Engineering | High-level Risks & Decisions | Strategic Overview |
| `customer_dave`| Customer | Sanitized Summary | View Final Response Only |

## 🚀 Key Features

### 1. 📂 Project Sidebar (Slack-style)
*   **Workspaces**: Organize orchestrations into distinct projects (e.g., "Alpha-Launch").
*   **Context Switching**: Easily switch between projects to view relevant history.
*   **Isolation**: New orchestrations are automatically tagged to the active project.


### 2. 📊 Role-Specific Dashboards
Instead of a generic view for everyone, the dashboard adapts to the user's role:
*   **Engineers**: See a list of action items, deadlines, and detected risks.
*   **VPs/Managers**: See high-level strategic decisions and critical risks.
*   **Customers**: See a polite, sanitized summary and final response — no internal logs.

### 3. 🧠 Mini Timeline Engine
*   **Date Normalization**: Converts relative dates ("next Friday") to absolute timestamps.
*   **Conflict Detection**: Identifies scheduling conflicts in message content.
*   **Extraction**: Automatically extracts deadlines for action items.

### 4. ⚡ L1-L3 Orchestration
*   **L1 Strategic Planner**: Breaks down complex requests into a dependency graph.
*   **L2 Router**: Dispatches tasks to specialized domains.
*   **L3 Agents**: specialized processing for Risks, Actions, Decisions, and more.

### 5. 🤖 RAG Project Assistant (Beta)
*   **Contextual Q&A**: Ask questions about the project and get answers based on documentation.
*   **Status**: 🚧 **Under Construction**. The chatbot handles basic queries but improvements to context retrieval and answer generation are ongoing.
*   **Tech**: FAISS Vector Store + Sentence Transformers + Groq LLaMA 3.
<img width="522" height="321" alt="image" src="https://github.com/user-attachments/assets/4d0fb176-ec3f-4a9b-9f6f-208671ea3fc2" />


## 📁 Project Structure

```
Nion-Orchestration/
├── backend/
│   ├── api.py           # FastAPI endpoints (Auth, Projects, Orchestrate)
│   ├── auth.py          # JWT & Password hashing
│   ├── rbac.py          # Role definitions & filtering logic
│   ├── orchestration/   # L1, L2, L3 & Timeline Engine
│   └── storage/         # SQLite DB (projects, maps, tasks)
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main Logic & Dashboard Rendering
│   │   ├── Sidebar.jsx  # Project Management UI
│   │   └── Login.jsx    # Auth UI
│   └── package.json
└── README.md
```

## 🛠️ Setup & Usage

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
# Set GROQ_API_KEY
python api.py
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Using the App
1.  **Login**: Use one of the credentials above (e.g., `admin` / `password123`).
2.  **Create Project**: Use the Sidebar to create a workspace (e.g., "Demo-Project").
3.  **Process Message**: Enter a request. The system will orchestrate it within the context of your project.
4.  **Explore Views**: Log out and log in as `engineer_bob` or `customer_dave` to see how the dashboard changes!

## 📋 Test Cases
The system is verified against 7 core scenarios (`testio.md`) covering feature requests, status checks, and ambiguity resolution.

## 📄 License
MIT
