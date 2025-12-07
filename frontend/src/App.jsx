
import { useState, useEffect } from 'react'
import './App.css'
import Login from './Login';
import Sidebar from './Sidebar';
import ChatBot from './ChatBot';

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
  const [activeProject, setActiveProject] = useState(null); // [NEW] Project Context
  const [messageContent, setMessageContent] = useState('');
  const [senderName, setSenderName] = useState('');
  const [senderRole, setSenderRole] = useState('');
  const [project, setProject] = useState('');
  const [source, setSource] = useState('email');
  const [isProcessing, setIsProcessing] = useState(false);
  const [orchestrationMap, setOrchestrationMap] = useState('');
  const [customerData, setCustomerData] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [showChatBot, setShowChatBot] = useState(false);
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
    setCustomerData(null);
    setDashboardData(null);
  };

  const handleProcess = async () => {
    if (!messageContent.trim()) {
      setError('Please enter a message to process');
      return;
    }

    setIsProcessing(true);
    setError('');
    // Clear previous generic outputs
    setOrchestrationMap('');
    setCustomerData(null);
    setDashboardData(null);

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
          // If activeProject is set, send its ID; otherwise send the manual string or null
          project: activeProject ? activeProject.id.toString() : (project || null)
        })
      });

      if (response.status === 401) {
        handleLogout(); // Auto logout on invalid token
        throw new Error("Session expired. Please login again.");
      }

      if (response.status === 429) {
        throw new Error("⚠️ Service is busy (Rate Limit). Please wait a few minutes.");
      }

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Handle RBAC Views
      if (data.customer_view) {
        setCustomerData(data);
      } else {
        setOrchestrationMap(data.orchestration_map);
        // Check for dashboard data
        if (data.extra && (data.extra.risks.length > 0 || data.extra.action_items.length > 0 || data.extra.decisions.length > 0)) {
          setDashboardData(data.extra);
        }
      }

    } catch (err) {
      if (!import.meta.env.VITE_API_URL && err.message.includes("Failed to fetch")) {
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
    setCustomerData(null);
    setDashboardData(null);
    setError('');
  };

  // Handle Project Selection
  const handleSelectProject = (proj) => {
    setActiveProject(proj);
    // Clear visual state when switching contexts
    setOrchestrationMap('');
    setCustomerData(null);
    setDashboardData(null);
    setError('');
    // Auto-fill project field for visual feedback (optional, as input is disabled)
    setProject(proj.project_name);
  };

  return (
    <div className="app-layout" style={{ display: 'flex', minHeight: '100vh', flexDirection: 'row' }}>

      {/* Sidebar */}
      <Sidebar
        activeProject={activeProject}
        onSelectProject={handleSelectProject}
        token={token}
      />

      {/* Main Content Area */}
      <div className="app" style={{ flex: 1, height: '100vh', overflowY: 'auto' }}>

        {/* Header */}
        <header className="header">
          <div className="container header-content">
            <div className="logo">
              <span className="logo-icon">⚡</span>
              Nion Orchestration
              <span className="version-badge">v0.3.0</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
              {activeProject && (
                <span className="status-badge" style={{ backgroundColor: '#38bdf8', color: '#000', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span style={{ fontSize: '1.2em' }}>📁</span>
                  {activeProject.project_name}
                </span>
              )}
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
              <button
                onClick={() => setShowChatBot(!showChatBot)}
                className="btn btn-primary"
                style={{ fontSize: '0.8rem', padding: '0.2rem 0.6rem', display: 'flex', alignItems: 'center', gap: '5px' }}
              >
                <span>💬</span> Chat
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
                    <h2 className="card-title">Message Input</h2>
                    <p className="card-subtitle">
                      {activeProject ? `Orchestrating for ${activeProject.project_name}` : "Enter a message or select a project"}
                    </p>
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
                      placeholder={activeProject ? activeProject.project_name : "e.g., PRJ-ALPHA"}
                      value={activeProject ? activeProject.project_name : project}
                      onChange={(e) => !activeProject && setProject(e.target.value)}
                      disabled={!!activeProject}
                      style={{
                        opacity: activeProject ? 0.7 : 1,
                        cursor: activeProject ? 'not-allowed' : 'text',
                        borderColor: activeProject ? '#38bdf8' : 'var(--border-color)'
                      }}
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
                      <>Process Message</>
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
                    <h2 className="card-title">
                      {customerData ? "Request Status" : dashboardData ? "🛠️ Action Dashboard" : "Orchestration Map"}
                    </h2>
                    <p className="card-subtitle">
                      {customerData ? "Summary of your processed request" : dashboardData ? "Unified view of risks, actions, and decisions" : "Generated task plan and extractions"}
                    </p>
                  </div>
                  {(orchestrationMap || customerData || dashboardData) && (
                    <span className="status-badge status-success">Generated</span>
                  )}
                </div>

                {/* Views */}
                {customerData ? (
                  /* CUSTOMER VIEW */
                  <div className="customer-view fade-in" style={{ padding: '1rem' }}>
                    <div style={{
                      backgroundColor: 'rgba(56, 189, 248, 0.1)',
                      border: '1px solid rgba(56, 189, 248, 0.2)',
                      borderRadius: '8px',
                      padding: '1.5rem',
                      marginBottom: '1.5rem'
                    }}>
                      <h3 style={{ color: '#38bdf8', marginBottom: '0.5rem', fontSize: '1.1rem' }}>✅ {customerData.summary || "Request Processed"}</h3>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                        Message ID: <span style={{ fontFamily: 'monospace' }}>{customerData.message_id}</span>
                      </p>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                      <label className="input-label" style={{ color: 'var(--text-primary)' }}>Final Response</label>
                      <div style={{
                        backgroundColor: 'var(--bg-secondary)',
                        padding: '1rem',
                        borderRadius: '6px',
                        lineHeight: '1.6',
                        fontSize: '0.95rem',
                        borderLeft: '3px solid var(--accent-primary)'
                      }}>
                        {customerData.final_response}
                      </div>
                    </div>

                    <div style={{ marginTop: '2rem', textAlign: 'center', opacity: 0.6, fontSize: '0.8rem' }}>
                      <p>Detailed technical logs are restricted for Customer accounts.</p>
                    </div>
                  </div>
                ) : dashboardData ? (
                  /* DASHBOARD VIEW */
                  <div className="dashboard-content fade-in" style={{ padding: '0 1rem 1rem 1rem' }}>

                    {/* Risks */}
                    {dashboardData.risks && dashboardData.risks.length > 0 && (
                      <div style={{ marginBottom: '2rem' }}>
                        <h3 style={{ color: '#ef4444', marginBottom: '0.8rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          ⚠️ Detected Risks
                          <span className="status-badge status-error" style={{ fontSize: '0.7rem' }}>{dashboardData.risks.length}</span>
                        </h3>
                        <div className="data-grid">
                          {dashboardData.risks.map((risk, i) => (
                            <div key={i} className="data-card" style={{ borderLeft: '3px solid #ef4444' }}>
                              <div style={{ fontWeight: '500', marginBottom: '4px' }}>{risk.risk_description || "No description available"}</div>
                              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', gap: '8px', alignItems: 'center' }}>
                                <span style={{
                                  color: (risk.severity && risk.severity.toLowerCase() === 'high') ? '#ef4444' : 'var(--text-primary)',
                                  fontWeight: 'bold'
                                }}>
                                  {risk.severity ? risk.severity.toUpperCase() : "UNKNOWN"}
                                </span>
                                {risk.probability && risk.probability !== "?" && (
                                  <span className="status-badge" style={{ fontSize: '0.7rem' }}>Prob: {risk.probability}</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Action Items */}
                    {dashboardData.action_items && dashboardData.action_items.length > 0 && (
                      <div style={{ marginBottom: '2rem' }}>
                        <h3 style={{ color: '#38bdf8', marginBottom: '0.8rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          Action Items
                          <span className="status-badge" style={{ fontSize: '0.7rem', backgroundColor: 'var(--accent-primary)' }}>{dashboardData.action_items.length}</span>
                        </h3>
                        <div className="data-list" style={{ display: 'grid', gap: '10px' }}>
                          {dashboardData.action_items.map((item, i) => (
                            <div key={i} style={{
                              backgroundColor: 'var(--bg-secondary)',
                              padding: '12px',
                              borderRadius: '6px',
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              borderLeft: item.priority === 'high' ? '3px solid #f97316' : '3px solid transparent'
                            }}>
                              <div>
                                <div style={{ marginBottom: '4px', fontWeight: '500' }}>{item.description}</div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', gap: '12px' }}>
                                  <span title="Owner">
                                    👤 {item.owner && item.owner !== "?" ? item.owner : "Unassigned"}
                                  </span>
                                  {item.deadline && item.deadline !== "?" && (
                                    <span title="Deadline"> {item.deadline}</span>
                                  )}
                                </div>
                              </div>
                              <span className={`status-badge ${item.priority === 'high' ? 'status-error' : 'status-success'}`}>
                                {item.priority || "Normal"}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Decisions */}
                    {dashboardData.decisions && dashboardData.decisions.length > 0 && (
                      <div style={{ marginBottom: '2rem' }}>
                        <h3 style={{ color: '#a855f7', marginBottom: '0.8rem' }}> Strategic Decisions</h3>
                        <div style={{
                          display: 'grid',
                          gap: '10px',
                          backgroundColor: 'var(--bg-secondary)',
                          padding: '1rem',
                          borderRadius: '8px'
                        }}>
                          {dashboardData.decisions.map((d, i) => (
                            <div key={i} style={{
                              borderBottom: i < dashboardData.decisions.length - 1 ? '1px solid var(--border-color)' : 'none',
                              paddingBottom: i < dashboardData.decisions.length - 1 ? '10px' : '0'
                            }}>
                              <div style={{ color: '#a855f7', fontWeight: 'bold', fontSize: '0.9rem', marginBottom: '2px' }}>
                                {d.topic && d.topic !== "?" && d.topic.trim() ? d.topic : "General Decision"}
                              </div>
                              <div style={{ color: 'var(--text-primary)', marginBottom: '4px' }}>{d.decision}</div>
                              {d.confidence_score && (
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Confidence: {d.confidence_score}</div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Full Map Toggle */}
                    {orchestrationMap && !orchestrationMap.includes("REDACTED") && (
                      <div style={{ marginTop: '2rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                        <details>
                          <summary style={{ cursor: 'pointer', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            View Full Orchestration Map (Technical Log)
                          </summary>
                          <div className="map-display fade-in" style={{ marginTop: '1rem', maxHeight: '400px', overflowY: 'auto' }}>
                            {orchestrationMap}
                          </div>
                        </details>
                      </div>
                    )}
                  </div>
                ) : orchestrationMap ? (
                  /* STANDARD MAP VIEW */
                  <div className="map-display fade-in">
                    {orchestrationMap}
                  </div>
                ) : (
                  /* EMPTY STATE */
                  <div className="empty-state">
                    <div className="empty-state-icon">📋</div>
                    <p>No results generated yet.</p>
                    <p style={{ fontSize: '0.85rem', marginTop: 'var(--space-sm)' }}>
                      Enter a message and click "Process Message".
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
      {showChatBot && <ChatBot token={token} onClose={() => setShowChatBot(false)} />}
    </div>
  )
}

export default App
