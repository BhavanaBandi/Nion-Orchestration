
import React, { useState, useEffect } from 'react';

const Sidebar = ({ activeProject, onSelectProject, token }) => {
    const [projects, setProjects] = useState([]);
    const [isCreating, setIsCreating] = useState(false);
    const [newProjectName, setNewProjectName] = useState('');
    const [error, setError] = useState('');
    const [isCollapsed, setIsCollapsed] = useState(false);

    // Fetch projects on load
    useEffect(() => {
        fetchProjects();
    }, [token]);

    const fetchProjects = async () => {
        if (!token) return;
        try {
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/projects`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setProjects(data);
            }
        } catch (err) {
            console.error("Failed to fetch projects", err);
        }
    };

    const handleCreateProject = async (e) => {
        e.preventDefault();
        if (!newProjectName.trim()) return;

        try {
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/projects`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ name: newProjectName })
            });

            if (res.ok) {
                await fetchProjects();
                setNewProjectName('');
                setIsCreating(false);
            } else {
                setError("Failed to create project");
            }
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="sidebar" style={{
            width: isCollapsed ? '70px' : '260px',
            backgroundColor: '#1e1e24',
            color: '#e0e0e0',
            display: 'flex',
            flexDirection: 'column',
            borderRight: '1px solid #333',
            transition: 'width 0.3s ease',
            flexShrink: 0
        }}>
            {/* Header */}
            <div style={{
                padding: '1.5rem 1rem',
                borderBottom: '1px solid #333',
                display: 'flex',
                alignItems: 'center',
                justifyContent: isCollapsed ? 'center' : 'space-between',
                height: '70px'
            }}>
                {!isCollapsed && <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold', margin: 0, color: 'white', whiteSpace: 'nowrap', overflow: 'hidden' }}>Workspaces</h2>}
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: '#888',
                        cursor: 'pointer',
                        padding: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                    title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
                >
                    {isCollapsed ? '➡' : '⬅'}
                </button>
            </div>

            {/* Projects List */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 0', overflowX: 'hidden' }}>
                {!isCollapsed && (
                    <div style={{
                        padding: '0 1rem 0.5rem 1rem',
                        fontSize: '0.8rem',
                        fontWeight: 'bold',
                        textTransform: 'uppercase',
                        color: '#888',
                        letterSpacing: '0.5px'
                    }}>
                        Projects
                    </div>
                )}

                {projects.map(proj => (
                    <div
                        key={proj.id}
                        onClick={() => onSelectProject(proj)}
                        style={{
                            padding: isCollapsed ? '12px 0' : '8px 16px',
                            cursor: 'pointer',
                            backgroundColor: activeProject && activeProject.id === proj.id ? '#38bdf8' : 'transparent',
                            color: activeProject && activeProject.id === proj.id ? '#1e1e24' : '#ccc',
                            fontWeight: activeProject && activeProject.id === proj.id ? '600' : 'normal',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: isCollapsed ? 'center' : 'flex-start',
                            gap: '8px'
                        }}
                        className="sidebar-item"
                        title={isCollapsed ? proj.project_name : ''}
                    >
                        <span style={{ opacity: 0.7, fontSize: isCollapsed ? '1.2rem' : '1rem' }}>#</span>
                        {!isCollapsed && <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{proj.project_name}</span>}
                    </div>
                ))}

                {/* Create UI */}
                {!isCollapsed && (
                    <>
                        {isCreating ? (
                            <form onSubmit={handleCreateProject} style={{ padding: '8px 16px' }}>
                                <input
                                    autoFocus
                                    type="text"
                                    placeholder="Project Name..."
                                    value={newProjectName}
                                    onChange={e => setNewProjectName(e.target.value)}
                                    onBlur={() => !newProjectName && setIsCreating(false)}
                                    style={{
                                        width: '100%',
                                        padding: '4px 8px',
                                        borderRadius: '4px',
                                        border: '1px solid #38bdf8',
                                        backgroundColor: '#333',
                                        color: 'white',
                                        fontSize: '0.9rem'
                                    }}
                                />
                            </form>
                        ) : (
                            <div
                                onClick={() => setIsCreating(true)}
                                style={{
                                    padding: '8px 16px',
                                    cursor: 'pointer',
                                    color: '#888',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    marginTop: '8px'
                                }}
                                className="sidebar-item-add"
                            >
                                <span>+</span> Add Project
                            </div>
                        )}
                    </>
                )}

                {isCollapsed && (
                    <div
                        onClick={() => setIsCollapsed(false)} // Expand to add
                        style={{
                            padding: '12px 0',
                            cursor: 'pointer',
                            color: '#888',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            marginTop: '8px'
                        }}
                        title="Expand to add project"
                    >
                        <span style={{ fontSize: '1.2rem' }}>+</span>
                    </div>
                )}
            </div>

            {/* User Footer */}
            <div style={{ padding: '1rem', borderTop: '1px solid #333', fontSize: '0.85rem', color: '#888', display: 'flex', justifyContent: isCollapsed ? 'center' : 'flex-start' }}>
                {isCollapsed ? '👤' : 'Logged in as User'}
            </div>
        </div>
    );
};

export default Sidebar;
