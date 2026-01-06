// Stacks page JavaScript - handles loading and displaying stacks grouped by project and environment
(function() {
    let allProjects = [];
    let selectedStackId = null;
    let selectedEnvironmentId = null;
    let availableContexts = [];

    // Initialize when DOM is ready
    function init() {
        loadStacks();
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

    // Load stacks via AJAX
    async function loadStacks() {
        try {
            const response = await fetch('/api/stacks/grouped', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load stacks');
            }

            const data = await response.json();
            allProjects = data.projects;
            renderStacks(data.projects);
        } catch (error) {
            console.error('Error loading stacks:', error);
            showNoStacks();
        }
    }

    // Build dependency tree for stacks
    function buildDependencyTree(stacks) {
        // Create a map of stack_id to stack object
        const stacksById = {};
        stacks.forEach(stack => {
            if (stack.stack_id) {
                stacksById[stack.stack_id] = {...stack, dependents: []};
            }
        });

        // Find root stacks (those with no dependencies or dependencies not in this environment)
        const rootStacks = [];
        
        stacks.forEach(stack => {
            const hasDependencies = Array.isArray(stack.depends_on) && stack.depends_on.length > 0;
            
            if (!hasDependencies) {
                // No dependencies - this is a root stack
                rootStacks.push(stack);
            } else {
                // Check if all dependencies are in this environment
                const allDepsPresent = stack.depends_on.every(depId => stacksById[depId]);
                
                if (!allDepsPresent) {
                    // Some dependencies missing - treat as root
                    rootStacks.push(stack);
                } else {
                    // Add this stack as a dependent to each of its dependencies
                    stack.depends_on.forEach(depId => {
                        if (stacksById[depId]) {
                            stacksById[depId].dependents.push(stack);
                        }
                    });
                }
            }
        });

        return {stacksById, rootStacks};
    }

    // Render a stack card with its dependents nested inside
    function renderStackCard(stack, stacksById, depth = 0) {
        const stackObj = stacksById[stack.stack_id] || stack;
        const hasDependents = stackObj.dependents && stackObj.dependents.length > 0;
        const hasContexts = stack.contexts && stack.contexts.length > 0;
        
        let html = `
            <div class="stack-card ${hasDependents ? 'has-dependents' : ''}" style="margin-left: ${depth * 1.5}rem;" data-stack-id="${stack.id}">
                <div class="stack-card-header">
                    <div class="stack-icon">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                        </svg>
                    </div>
                    <div class="stack-info">
                        <div class="stack-name">${escapeHtml(stack.name)}</div>
                        ${stack.stack_id ? `<div class="stack-id">${escapeHtml(stack.stack_id)}</div>` : ''}
                        <div class="stack-contexts">
                            ${hasContexts ? stack.contexts.map(ctx => `
                                <span class="context-badge">
                                    ${escapeHtml(ctx.name)}
                                    <button class="context-remove-btn" onclick="window.removeStackContext(${stack.id}, ${ctx.id})" title="Remove context">
                                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="12" height="12">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                        </svg>
                                    </button>
                                </span>
                            `).join('') : ''}
                            <button class="btn-add-context" onclick="window.openStackContextModal(${stack.id})" title="Add context to stack">
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                </svg>
                                Add Context
                            </button>
                        </div>
                    </div>
                </div>
        `;

        // Render dependents nested inside
        if (hasDependents) {
            html += '<div class="stack-dependents">';
            stackObj.dependents.forEach(dependent => {
                html += renderStackCard(dependent, stacksById, depth + 1);
            });
            html += '</div>';
        }

        html += '</div>';
        return html;
    }

    // Render stacks list
    function renderStacks(projects) {
        const container = document.getElementById('stacksList');
        if (!container) return;

        if (!projects || projects.length === 0) {
            showNoStacks();
            return;
        }

        let html = '<div class="stacks-hierarchy">';

        projects.forEach(project => {
            // Skip projects with no environments or stacks
            if (!project.environments || project.environments.length === 0) {
                return;
            }

            html += `
                <div class="project-group">
                    <div class="project-header">
                        <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                        </svg>
                        <h3>${escapeHtml(project.name)}</h3>
                    </div>
                    <div class="environments-list">
            `;

            project.environments.forEach(environment => {
                // Skip environments with no stacks
                if (!environment.stacks || environment.stacks.length === 0) {
                    return;
                }

                const hasEnvContexts = environment.contexts && environment.contexts.length > 0;

                html += `
                    <div class="environment-group">
                        <div class="environment-header">
                            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <div class="environment-header-content">
                                <h4>${escapeHtml(environment.name)}</h4>
                                ${hasEnvContexts ? `
                                    <div class="environment-contexts">
                                        <span class="contexts-label">Shared Contexts:</span>
                                        ${environment.contexts.map(ctx => `<span class="context-badge environment-context">${escapeHtml(ctx.name)}</span>`).join('')}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        <div class="stacks-tree">
                `;

                // Build dependency tree
                const {stacksById, rootStacks} = buildDependencyTree(environment.stacks);

                // Render root stacks and their dependents
                rootStacks.forEach(rootStack => {
                    html += renderStackCard(rootStack, stacksById, 0);
                });

                html += `
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
    }

    // Show no stacks message
    function showNoStacks() {
        const container = document.getElementById('stacksList');
        if (!container) return;

        container.innerHTML = '<p class="no-data" data-i18n="stacks.no_stacks">No stacks found. Create your first stack to begin managing infrastructure.</p>';
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

    // Open modal to attach context to stack
    async function openStackContextModal(stackId) {
        selectedStackId = stackId;
        selectedEnvironmentId = null;
        
        // Expose to window for form handler
        window.selectedStackId = stackId;
        window.selectedEnvironmentId = null;
        
        // Find the stack to get project_id
        let projectId = null;
        for (const project of allProjects) {
            for (const env of project.environments || []) {
                const stack = (env.stacks || []).find(s => s.id === stackId);
                if (stack) {
                    projectId = project.id;
                    break;
                }
            }
            if (projectId) break;
        }

        if (!projectId) {
            alert('Error: Could not find stack project');
            return;
        }

        // Load contexts for this project
        await loadContextsForProject(projectId);
        
        // Get already attached contexts
        const stackElement = document.querySelector(`[data-stack-id="${stackId}"]`);
        const attachedContexts = new Set();
        if (stackElement) {
            stackElement.querySelectorAll('.context-badge').forEach(badge => {
                const text = badge.textContent.trim().replace('×', '').trim();
                attachedContexts.add(text);
            });
        }

        // Filter out already attached contexts
        const availableToAttach = availableContexts.filter(ctx => !attachedContexts.has(ctx.name));

        // Populate modal
        document.getElementById('contextModalTitle').textContent = 'Add Context to Stack';
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
        selectedStackId = null;
        selectedEnvironmentId = null;
    }

    // Handle attach context form submission
    async function handleAttachContext(e) {
        e.preventDefault();
        
        const contextId = document.getElementById('contextSelect').value;
        if (!contextId) {
            alert('Please select a context');
            return;
        }

        try {
            const url = selectedStackId 
                ? `/api/stacks/${selectedStackId}/contexts`
                : `/api/environments/${selectedEnvironmentId}/contexts`;

            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ context_id: parseInt(contextId) })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to attach context');
            }

            // Reload stacks to show updated contexts
            await loadStacks();
            closeContextModal();
        } catch (error) {
            console.error('Error attaching context:', error);
            alert('Failed to attach context: ' + error.message);
        }
    }

    // Remove context from stack
    async function removeStackContext(stackId, contextId) {
        if (!confirm('Are you sure you want to remove this context from the stack?')) {
            return;
        }

        try {
            const response = await fetch(`/api/stacks/${stackId}/contexts/${contextId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to remove context');
            }

            // Reload stacks to show updated contexts
            await loadStacks();
        } catch (error) {
            console.error('Error removing context:', error);
            alert('Failed to remove context: ' + error.message);
        }
    }

    // Expose functions to window for onclick handlers
    window.openStackContextModal = openStackContextModal;
    window.removeStackContext = removeStackContext;

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
