import { useState, useEffect } from 'react'
import './App.css'
import Login from './Login';

// Sample test messages from testio.md
const SAMPLE_MESSAGES = [
  {
    message_id: "MSG-001",
    source: "email",
    sender: { name: "Sarah Chen", role: "Product Manager" },
    content: "The customer demo went great! They loved it but asked if we could add real-time notifications and a dashboard export feature. They're willing to pay 20% more and need it in the same timeline. Can we make this work?",
    project: "PRJ-ALPHA"
  },
  {
    message_id: "MSG-101",
    source: "slack",
    sender: { name: "John Doe", role: "Engineering Manager" },
    content: "What's the status of the authentication feature?",
    project: "PRJ-BETA"
  },
  {
    message_id: "MSG-102",
    source: "email",
    sender: { name: "Sarah Chen", role: "Product Manager" },
    content: "Can we add SSO integration before the December release?",
    project: "PRJ-ALPHA"
  },
  {
    message_id: "MSG-103",
    source: "email",
    sender: { name: "Mike Johnson", role: "VP Engineering" },
    content: "Should we prioritize security fixes or the new dashboard?",
    project: "PRJ-GAMMA"
  },
  {
    message_id: "MSG-104",
    source: "meeting",
    sender: { name: "System", role: "Meeting Bot" },
    content: "Dev: I'm blocked on API integration, staging is down. QA: Found 3 critical bugs in payment flow. Designer: Mobile mockups ready by Thursday. Tech Lead: We might need to refactor the auth module.",
    project: "PRJ-ALPHA"
  },
  {
    message_id: "MSG-105",
    source: "email",
    sender: { name: "Lisa Wong", role: "Customer Success Manager" },
    content: "The client is asking why feature X promised for Q3 is still not delivered. They're threatening to escalate to legal. What happened?",
    project: "PRJ-DELTA"
  },
  {
    message_id: "MSG-106",
    source: "slack",
    sender: { name: "Random User", role: "Unknown" },
    content: "We need to speed things up",
    project: null
  }
];

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Auth State Management
  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  // Main App State
  const [messageContent, setMessageContent] = useState('');
  const [senderName, setSenderName] = useState('');
  const [senderRole, setSenderRole] = useState('');
  const [project, setProject] = useState('');
  const [source, setSource] = useState('email');
  const [isProcessing, setIsProcessing] = useState(false);
  const [orchestrationMap, setOrchestrationMap] = useState('');
  const [error, setError] = useState('');

  // If not logged in, show Login screen
  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  const loadSample = (sample) => {
    setMessageContent(sample.content);
    setSenderName(sample.sender.name);
    setSenderRole(sample.sender.role);
    setProject(sample.project);
    setSource(sample.source);
    setError('');
    setOrchestrationMap('');
  };

  const handleProcess = async () => {
    if (!messageContent.trim()) {
      setError('Please enter a message to process');
      return;
    }

    setIsProcessing(true);
    setError('');
    setOrchestrationMap('');

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/orchestrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` // Include Token
        },
        body: JSON.stringify({
          message_id: `MSG-${Date.now()}`,
          source: source,
          sender: {
            name: senderName || 'Unknown',
            role: senderRole || 'Unknown'
          },
          content: messageContent,
          project: project || null
        })
      });

      if (response.status === 401) {
        handleLogout(); // Auto logout on invalid token
        throw new Error("Session expired. Please login again.");
      }

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setOrchestrationMap(data.orchestration_map);
    } catch (err) {
      // For demo mode without backend, show a sample output
      if (!import.meta.env.VITE_API_URL && err.message.includes("Failed to fetch")) {
        // Fallback code removed for brevity, keeping error handling clean
        setError(`Connection Error: ${err.message}. Ensure backend is running.`);
      } else {
        setError(err.message);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClear = () => {
    setMessageContent('');
    setSenderName('');
    setSenderRole('');
    setProject('');
    setSource('email');
    setOrchestrationMap('');
    setError('');
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container header-content">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            Nion Orchestration
            <span className="version-badge">v0.3.0</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
            <span className="status-badge status-success">
              ● Protected
            </span>
            <button
              onClick={handleLogout}
              className="btn btn-secondary"
              style={{ fontSize: '0.8rem', padding: '0.2rem 0.6rem' }}
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Hero */}
          <section className="hero">
            <h1 className="hero-title">L1 → L2 → L3 Orchestration</h1>
            <p className="hero-subtitle">
              Transform messages into structured task plans, extract action items,
              risks, decisions, and generate intelligent responses.
            </p>
          </section>

          {/* Dashboard Grid */}
          <div className="dashboard-grid">
            {/* Input Panel */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h2 className="card-title">📩 Message Input</h2>
                  <p className="card-subtitle">Enter a message to orchestrate</p>
                </div>
              </div>

              {/* Quick Load Samples */}
              <div style={{ marginBottom: 'var(--space-lg)' }}>
                <label className="input-label">Quick Load Sample:</label>
                <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
                  {SAMPLE_MESSAGES.map((sample, idx) => (
                    <button
                      key={idx}
                      className="btn btn-secondary"
                      onClick={() => loadSample(sample)}
                    >
                      {sample.message_id}
                    </button>
                  ))}
                </div>
              </div>

              {/* Input Fields */}
              <div className="input-row">
                <div className="input-group">
                  <label className="input-label">Sender Name</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g., Sarah Chen"
                    value={senderName}
                    onChange={(e) => setSenderName(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <label className="input-label">Sender Role</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g., Product Manager"
                    value={senderRole}
                    onChange={(e) => setSenderRole(e.target.value)}
                  />
                </div>
              </div>

              <div className="input-row">
                <div className="input-group">
                  <label className="input-label">Project</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g., PRJ-ALPHA"
                    value={project}
                    onChange={(e) => setProject(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <label className="input-label">Source</label>
                  <select
                    className="input"
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                  >
                    <option value="email">Email</option>
                    <option value="slack">Slack</option>
                    <option value="meeting">Meeting</option>
                  </select>
                </div>
              </div>

              <div className="input-group">
                <label className="input-label">Message Content</label>
                <textarea
                  className="textarea"
                  placeholder="Enter the message content to process..."
                  value={messageContent}
                  onChange={(e) => setMessageContent(e.target.value)}
                />
              </div>

              {error && (
                <div style={{ color: 'var(--status-error)', marginBottom: 'var(--space-md)', fontSize: '0.9rem' }}>
                  ⚠️ {error}
                </div>
              )}

              <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                <button
                  className="btn btn-primary btn-lg"
                  onClick={handleProcess}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <span className="spinner"></span>
                      Processing...
                    </>
                  ) : (
                    <>🚀 Process Message</>
                  )}
                </button>
                <button
                  className="btn btn-secondary btn-lg"
                  onClick={handleClear}
                  disabled={isProcessing}
                >
                  Clear
                </button>
              </div>
            </div>

            {/* Output Panel */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h2 className="card-title">🗺️ Orchestration Map</h2>
                  <p className="card-subtitle">Generated task plan and extractions</p>
                </div>
                {orchestrationMap && (
                  <span className="status-badge status-success">Generated</span>
                )}
              </div>

              {orchestrationMap ? (
                <div className="map-display fade-in">
                  {orchestrationMap}
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-state-icon">📋</div>
                  <p>No orchestration map generated yet.</p>
                  <p style={{ fontSize: '0.85rem', marginTop: 'var(--space-sm)' }}>
                    Enter a message and click "Process Message" to generate.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          Nion Orchestration Engine • Python + SQLite + OpenAI/GPT-OSS-120
        </div>
      </footer>
    </div>
  )
}

export default App
