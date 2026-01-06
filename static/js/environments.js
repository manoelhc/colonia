// Environments page JavaScript - handles loading and displaying environments grouped by project
(function() {
    let allProjects = [];
    let selectedEnvironmentId = null;
    let availableContexts = [];

    // Initialize when DOM is ready
    function init() {
        loadEnvironments();
        initModalHandlers();
    }

    // Initialize modal event handlers
    function initModalHandlers() {
        // Close modal on backdrop click
        const modal = document.getElementById('contextAttachModal');
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeContextModal();
                }
            });
        }

        // Close modal on close button click
        const closeButtons = document.querySelectorAll('.modal-close');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', closeContextModal);
        });
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
            allProjects = data.projects;
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
                        <div class="environment-card" data-environment-id="${environment.id}" data-project-id="${project.id}">
                            <div class="environment-header">
                                <div class="environment-icon">
                                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                </div>
                                <div class="environment-info">
                                    <div class="environment-name">${escapeHtml(environment.name)}</div>
                                    <div class="environment-directory">${escapeHtml(environment.directory)}</div>
                                    <div class="environment-contexts">
                                        ${hasContexts ? environment.contexts.map(ctx => `
                                            <span class="context-badge">
                                                ${escapeHtml(ctx.name)}
                                                <button class="context-remove-btn" onclick="window.removeEnvironmentContext(${environment.id}, ${ctx.id})" title="Remove context">
                                                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="12" height="12">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                                    </svg>
                                                </button>
                                            </span>
                                        `).join('') : ''}
                                        <button class="btn-add-context" onclick="window.openEnvironmentContextModal(${environment.id}, ${project.id})" title="Add context to environment">
                                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                            </svg>
                                            Add Context
                                        </button>
                                    </div>
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

    // Open modal to attach context to environment
    async function openEnvironmentContextModal(environmentId, projectId) {
        selectedEnvironmentId = environmentId;
        
        // Expose to window for form handler
        window.selectedEnvironmentId = environmentId;
        
        // Load contexts for this project
        await loadContextsForProject(projectId);
        
        // Get already attached contexts
        const envElement = document.querySelector(`[data-environment-id="${environmentId}"]`);
        const attachedContexts = new Set();
        if (envElement) {
            envElement.querySelectorAll('.context-badge').forEach(badge => {
                const text = badge.textContent.trim().replace('×', '').trim();
                attachedContexts.add(text);
            });
        }

        // Filter out already attached contexts
        const availableToAttach = availableContexts.filter(ctx => !attachedContexts.has(ctx.name));

        // Populate modal
        document.getElementById('contextModalTitle').textContent = 'Add Context to Environment';
        const select = document.getElementById('contextSelect');
        select.innerHTML = '<option value="">Select a context...</option>';
        availableToAttach.forEach(ctx => {
            select.innerHTML += `<option value="${ctx.id}">${escapeHtml(ctx.name)}</option>`;
        });

        document.getElementById('contextAttachModal').classList.add('show');
    }

    // Load contexts for a project
    async function loadContextsForProject(projectId) {
        try {
            const response = await fetch('/api/contexts', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error('Failed to load contexts');
            }

            const data = await response.json();
            availableContexts = data.contexts.filter(ctx => ctx.project_id === projectId);
        } catch (error) {
            console.error('Error loading contexts:', error);
            availableContexts = [];
        }
    }

    // Close context modal
    function closeContextModal() {
        document.getElementById('contextAttachModal').classList.remove('show');
        selectedEnvironmentId = null;
    }

    // Remove context from environment
    async function removeEnvironmentContext(environmentId, contextId) {
        if (!confirm('Are you sure you want to remove this context from the environment?')) {
            return;
        }

        try {
            const response = await fetch(`/api/environments/${environmentId}/contexts/${contextId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to remove context');
            }

            // Reload environments to show updated contexts
            await loadEnvironments();
        } catch (error) {
            console.error('Error removing context:', error);
            alert('Failed to remove context: ' + error.message);
        }
    }

    // Expose functions to window for onclick handlers
    window.openEnvironmentContextModal = openEnvironmentContextModal;
    window.removeEnvironmentContext = removeEnvironmentContext;

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
