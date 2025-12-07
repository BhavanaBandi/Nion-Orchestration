import React, { useState } from 'react';
import './ChatBot.css'; // optional styling file

function ChatBot({ token, onClose }) {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [sources, setSources] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async () => {
        if (!question.trim()) return;
        setLoading(true);
        setError('');
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/rag/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ question, top_k: 3 }),
            });
            if (response.status === 429) {
                throw new Error("⚠️ Service is busy (Rate Limit). Please wait a few minutes.");
            }
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Chat request failed');
            }
            const data = await response.json();
            setAnswer(data.answer);
            setSources(data.sources || []);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chatbot-overlay">
            <div className="chatbot-container">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h2 className="chatbot-title" style={{ border: 'none', marginBottom: 0 }}>Project Assistant</h2>
                    <button
                        onClick={onClose}
                        style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1.2rem', padding: '0 0.5rem' }}
                    >
                        ✕
                    </button>
                </div>
                <div style={{ borderBottom: '1px solid var(--border-color)', marginBottom: '1rem', marginTop: '0.5rem' }}></div>
                <textarea
                    className="chatbot-input"
                    placeholder="Ask a question about the project..."
                    value={question}
                    onChange={e => setQuestion(e.target.value)}
                    rows={3}
                />
                <button className="chatbot-submit btn btn-primary" onClick={handleSubmit} disabled={loading}>
                    {loading ? 'Thinking…' : 'Ask'}
                </button>
                {error && <div className="chatbot-error" style={{ color: 'var(--status-error)', marginTop: '0.5rem' }}>{error}</div>}
                {answer && (
                    <div className="chatbot-response" style={{ marginTop: '1rem' }}>
                        <h3>Answer</h3>
                        <p>{answer}</p>
                        {sources.length > 0 && (
                            <div className="chatbot-sources" style={{ marginTop: '0.5rem' }}>
                                <h4>Sources</h4>
                                <ul>
                                    {sources.map((src, idx) => (
                                        <li key={idx}>{src}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export default ChatBot;
