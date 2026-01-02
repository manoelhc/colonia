// Environments page JavaScript - handles loading and displaying environments grouped by project
(function() {
    // Initialize when DOM is ready
    function init() {
        loadEnvironments();
    }

    // Load environments via AJAX
    async function loadEnvironments() {
        try {
            const response = await fetch('/api/environments/grouped', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load environments');
            }

            const data = await response.json();
            renderEnvironments(data.projects);
        } catch (error) {
            console.error('Error loading environments:', error);
            showNoEnvironments();
        }
    }

    // Render environments list
    function renderEnvironments(projects) {
        const container = document.getElementById('environmentsList');
        if (!container) return;

        if (!projects || projects.length === 0) {
            showNoEnvironments();
            return;
        }

        let html = '';
        
        projects.forEach(project => {
            if (project.environments && project.environments.length > 0) {
                html += `
                    <div class="project-section">
                        <div class="project-header">
                            <div class="project-header-content">
                                <h4>${escapeHtml(project.name)}</h4>
                                ${project.description ? `<p class="project-description">${escapeHtml(project.description)}</p>` : ''}
                            </div>
                            ${project.repository_url ? `
                                <a href="${escapeHtml(project.repository_url)}" target="_blank" rel="noopener noreferrer" class="project-repo-link">
                                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                    </svg>
                                </a>
                            ` : ''}
                        </div>
                        <div class="environments-grid">
                `;
                
                project.environments.forEach(environment => {
                    const hasContexts = environment.contexts && environment.contexts.length > 0;
                    html += `
                        <div class="environment-card">
                            <div class="environment-header">
                                <div class="environment-icon">
                                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                </div>
                                <div class="environment-info">
                                    <div class="environment-name">${escapeHtml(environment.name)}</div>
                                    <div class="environment-directory">${escapeHtml(environment.directory)}</div>
                                    ${hasContexts ? `
                                        <div class="environment-contexts">
                                            ${environment.contexts.map(ctx => `<span class="context-badge">${escapeHtml(ctx.name)}</span>`).join('')}
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                            <div class="environment-footer">
                                <small class="text-muted">Created: ${formatDate(environment.created_at)}</small>
                            </div>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
        });

        container.innerHTML = html;
    }

    // Show no environments message
    function showNoEnvironments() {
        const container = document.getElementById('environmentsList');
        if (!container) return;
        
        container.innerHTML = '<p class="no-data" data-i18n="environments.no_environments">No environments found. Create your first environment to organize deployments.</p>';
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    // Format date for display
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
