
import React, { useState, useEffect } from 'react';

const Sidebar = ({ activeProject, onSelectProject, token }) => {
    const [projects, setProjects] = useState([]);
    const [isCreating, setIsCreating] = useState(false);
    const [newProjectName, setNewProjectName] = useState('');
    const [error, setError] = useState('');

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
                // Auto-select first project if none active and list not empty
                // (Optional behavior, maybe we want 'All Projects' view?)
                // if (!activeProject && data.length > 0) onSelectProject(data[0]);
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
                const newProj = await res.json(); // returns {id, name, success} details usually
                // Refresh list
                await fetchProjects();
                // Select new project
                // Note: The API returns {id, name, success}, but list uses {id, project_name...}
                // Let's rely on fetchProjects to get the canonical format
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
            width: '260px',
            backgroundColor: '#1e1e24', /* Darker than main bg */
            color: '#e0e0e0',
            display: 'flex',
            flexDirection: 'column',
            borderRight: '1px solid #333'
        }}>
            {/* Header */}
            <div style={{ padding: '1.5rem 1rem', borderBottom: '1px solid #333' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold', margin: 0, color: 'white' }}>Nion Workspaces</h2>
            </div>

            {/* Projects List */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 0' }}>
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

                {projects.map(proj => (
                    <div
                        key={proj.id}
                        onClick={() => onSelectProject(proj)}
                        style={{
                            padding: '8px 16px',
                            cursor: 'pointer',
                            backgroundColor: activeProject && activeProject.id === proj.id ? '#38bdf8' : 'transparent',
                            color: activeProject && activeProject.id === proj.id ? '#1e1e24' : '#ccc',
                            fontWeight: activeProject && activeProject.id === proj.id ? '600' : 'normal',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                        className="sidebar-item"
                    >
                        <span style={{ opacity: 0.7 }}>#</span> {proj.project_name}
                    </div>
                ))}

                {/* Create UI */}
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
            </div>

            {/* User Footer */}
            <div style={{ padding: '1rem', borderTop: '1px solid #333', fontSize: '0.85rem', color: '#888' }}>
                Logged in as User
            </div>
        </div>
    );
};

export default Sidebar;
