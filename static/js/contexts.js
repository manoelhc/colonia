// Contexts page JavaScript - handles AJAX and modals
(function() {
    let contexts = [];
    let projects = [];
    let vaultPaths = [];
    let editingContextId = null;
    let currentContextIdForSecrets = null;

    // Initialize when DOM is ready
    function init() {
        loadProjects();
        loadContexts();
        loadVaultPaths();
        setupEventListeners();
    }

    // Set up event listeners
    function setupEventListeners() {
        // Add context button
        const addBtn = document.getElementById('addContextBtn');
        if (addBtn) {
            addBtn.addEventListener('click', openCreateModal);
        }

        // Modal close buttons
        const closeButtons = document.querySelectorAll('.modal-close');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', closeModal);
        });

        // Drawer close button
        const drawerClose = document.getElementById('drawerClose');
        if (drawerClose) {
            drawerClose.addEventListener('click', closeSecretsDrawer);
        }

        // Modal backdrop click
        const contextModal = document.getElementById('contextModal');
        if (contextModal) {
            contextModal.addEventListener('click', function(e) {
                if (e.target === contextModal) {
                    closeModal();
                }
            });
        }

        // Drawer backdrop click
        const secretsDrawer = document.getElementById('secretsDrawer');
        if (secretsDrawer) {
            secretsDrawer.addEventListener('click', function(e) {
                if (e.target === secretsDrawer) {
                    closeSecretsDrawer();
                }
            });
        }

        // Context form submission
        const contextForm = document.getElementById('contextForm');
        if (contextForm) {
            contextForm.addEventListener('submit', handleContextFormSubmit);
        }

        // Secret form submission
        const secretForm = document.getElementById('secretForm');
        if (secretForm) {
            secretForm.addEventListener('submit', handleSecretFormSubmit);
        }
    }

    // Load projects via AJAX
    async function loadProjects() {
        try {
            const response = await fetch('/api/projects', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load projects');
            }

            const data = await response.json();
            projects = data.projects || [];
            renderProjectOptions();
        } catch (error) {
            console.error('Error loading projects:', error);
        }
    }

    // Render project options in select dropdown
    function renderProjectOptions() {
        const select = document.getElementById('contextProject');
        if (!select) return;

        select.innerHTML = '<option value="">Select a project</option>';
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            select.appendChild(option);
        });
    }

    // Load Vault paths via AJAX
    async function loadVaultPaths() {
        try {
            const response = await fetch('/api/vault/secrets-engines', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load vault paths');
            }

            const data = await response.json();
            // Extract paths from secrets engines
            vaultPaths = Object.keys(data.secrets_engines || {}).map(path => path.replace(/\/$/, ''));
            renderVaultPathOptions();
        } catch (error) {
            console.error('Error loading vault paths:', error);
            // Default to some common paths if API fails
            vaultPaths = ['colonia', 'secret', 'kv'];
            renderVaultPathOptions();
        }
    }

    // Render vault path options in select dropdown
    function renderVaultPathOptions() {
        const select = document.getElementById('secretVaultPath');
        if (!select) return;

        select.innerHTML = '<option value="">Select a vault path</option>';
        vaultPaths.forEach(path => {
            const option = document.createElement('option');
            option.value = path;
            option.textContent = path;
            select.appendChild(option);
        });
    }

    // Load contexts via AJAX
    async function loadContexts() {
        try {
            const response = await fetch('/api/contexts', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load contexts');
            }

            const data = await response.json();
            contexts = data.contexts || [];
            renderContexts();
        } catch (error) {
            console.error('Error loading contexts:', error);
            showNotification('Failed to load contexts', 'error');
        }
    }

    // Render contexts list
    function renderContexts() {
        const container = document.getElementById('contextsList');
        if (!container) return;

        if (contexts.length === 0) {
            container.innerHTML = '<p class="no-data" data-i18n="contexts.no_contexts">No contexts found. Create your first context to share environment variables across stacks.</p>';
            return;
        }

        const html = contexts.map(context => `
            <div class="context-card" data-context-id="${parseInt(context.id)}">
                <div class="context-card-header">
                    <h4>${escapeHtml(context.name)}</h4>
                    <div class="context-actions">
                        <button class="btn-icon" onclick="contextsModule.openSecretsDrawer(${parseInt(context.id)})" title="Set Secrets">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                            </svg>
                        </button>
                        <button class="btn-icon" onclick="contextsModule.editContext(${parseInt(context.id)})" title="Edit">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button class="btn-icon" onclick="contextsModule.deleteContext(${parseInt(context.id)})" title="Delete">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="context-card-body">
                    ${context.description ? `<p>${escapeHtml(context.description)}</p>` : '<p class="text-muted">No description</p>'}
                    <p class="context-project"><strong>Project:</strong> ${escapeHtml(context.project_name)}</p>
                </div>
                <div class="context-card-footer">
                    <small class="text-muted">Created: ${formatDate(context.created_at)}</small>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // Open create modal
    function openCreateModal() {
        editingContextId = null;
        document.getElementById('modalTitle').textContent = 'Create New Context';
        document.getElementById('contextForm').reset();
        document.getElementById('contextModal').classList.add('show');
    }

    // Open edit modal
    function openEditModal(contextId) {
        const context = contexts.find(c => c.id === contextId);
        if (!context) return;

        editingContextId = contextId;
        document.getElementById('modalTitle').textContent = 'Edit Context';
        document.getElementById('contextName').value = context.name;
        document.getElementById('contextDescription').value = context.description || '';
        document.getElementById('contextProject').value = context.project_id;
        document.getElementById('contextModal').classList.add('show');
    }

    // Close modal
    function closeModal() {
        document.getElementById('contextModal').classList.remove('show');
        document.getElementById('contextForm').reset();
        editingContextId = null;
    }

    // Handle context form submission
    async function handleContextFormSubmit(e) {
        e.preventDefault();

        const name = document.getElementById('contextName').value.trim();
        const description = document.getElementById('contextDescription').value.trim();
        const project_id = document.getElementById('contextProject').value;

        // Client-side validation
        if (!name) {
            showNotification('Context name is required', 'error');
            return;
        }

        if (!project_id) {
            showNotification('Project is required', 'error');
            return;
        }

        if (name.length > 255) {
            showNotification('Context name is too long (max 255 characters)', 'error');
            return;
        }

        if (description && description.length > 1000) {
            showNotification('Description is too long (max 1000 characters)', 'error');
            return;
        }

        const data = {
            name: name,
            description: description || null,
            project_id: parseInt(project_id)
        };

        try {
            const url = editingContextId 
                ? `/api/contexts/${editingContextId}`
                : '/api/contexts';
            
            const method = editingContextId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to save context');
            }

            showNotification(
                editingContextId ? 'Context updated successfully' : 'Context created successfully',
                'success'
            );
            
            closeModal();
            loadContexts();
        } catch (error) {
            console.error('Error saving context:', error);
            showNotification(error.message || 'Failed to save context', 'error');
        }
    }

    // Delete context
    async function deleteContext(contextId) {
        if (!confirm('Are you sure you want to delete this context? All associated secrets will also be deleted.')) {
            return;
        }

        try {
            const response = await fetch(`/api/contexts/${contextId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const result = await response.json();
                throw new Error(result.error || 'Failed to delete context');
            }

            showNotification('Context deleted successfully', 'success');
            loadContexts();
        } catch (error) {
            console.error('Error deleting context:', error);
            showNotification(error.message || 'Failed to delete context', 'error');
        }
    }

    // Open secrets drawer
    async function openSecretsDrawer(contextId) {
        currentContextIdForSecrets = contextId;
        const context = contexts.find(c => c.id === contextId);
        
        if (!context) return;

        document.getElementById('drawerContextName').textContent = context.name;
        document.getElementById('secretsDrawer').classList.add('show');
        
        // Clear and reset the form
        document.getElementById('secretForm').reset();
        
        // Load secrets for this context
        await loadContextSecrets(contextId);
    }

    // Close secrets drawer
    function closeSecretsDrawer() {
        document.getElementById('secretsDrawer').classList.remove('show');
        document.getElementById('secretForm').reset();
        currentContextIdForSecrets = null;
    }

    // Load context secrets
    async function loadContextSecrets(contextId) {
        try {
            const response = await fetch(`/api/contexts/${contextId}/secrets`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load secrets');
            }

            const data = await response.json();
            renderContextSecrets(data.secrets || [], contextId);
        } catch (error) {
            console.error('Error loading secrets:', error);
            showNotification('Failed to load secrets', 'error');
        }
    }

    // Render context secrets
    function renderContextSecrets(secrets, contextId) {
        const container = document.getElementById('secretsList');
        if (!container) return;

        if (secrets.length === 0) {
            container.innerHTML = '<p class="no-data">No secrets configured for this context.</p>';
            return;
        }

        const html = secrets.map(secret => `
            <div class="secret-item">
                <div class="secret-info">
                    <div class="secret-key">${escapeHtml(secret.secret_key)}</div>
                    <div class="secret-path">${escapeHtml(secret.vault_path)}</div>
                </div>
                <button class="btn-icon" onclick="contextsModule.deleteSecret(${parseInt(contextId)}, ${parseInt(secret.id)})" title="Delete">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                </button>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // Handle secret form submission
    async function handleSecretFormSubmit(e) {
        e.preventDefault();

        if (!currentContextIdForSecrets) {
            showNotification('No context selected', 'error');
            return;
        }

        const secret_key = document.getElementById('secretKey').value.trim();
        const vault_path = document.getElementById('secretVaultPath').value;

        // Client-side validation
        if (!secret_key) {
            showNotification('Secret key is required', 'error');
            return;
        }

        if (!vault_path) {
            showNotification('Vault path is required', 'error');
            return;
        }

        if (secret_key.length > 255) {
            showNotification('Secret key is too long (max 255 characters)', 'error');
            return;
        }

        const data = {
            secret_key: secret_key,
            vault_path: vault_path
        };

        try {
            const response = await fetch(`/api/contexts/${currentContextIdForSecrets}/secrets`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to add secret');
            }

            showNotification('Secret added successfully', 'success');
            
            // Reset form
            document.getElementById('secretForm').reset();
            
            // Reload secrets
            await loadContextSecrets(currentContextIdForSecrets);
        } catch (error) {
            console.error('Error adding secret:', error);
            showNotification(error.message || 'Failed to add secret', 'error');
        }
    }

    // Delete secret
    async function deleteSecret(contextId, secretId) {
        if (!confirm('Are you sure you want to delete this secret?')) {
            return;
        }

        try {
            const response = await fetch(`/api/contexts/${contextId}/secrets/${secretId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const result = await response.json();
                throw new Error(result.error || 'Failed to delete secret');
            }

            showNotification('Secret deleted successfully', 'success');
            await loadContextSecrets(contextId);
        } catch (error) {
            console.error('Error deleting secret:', error);
            showNotification(error.message || 'Failed to delete secret', 'error');
        }
    }

    // Show notification
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Add to page
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
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

    // Format date
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    // Expose public methods
    window.contextsModule = {
        editContext: openEditModal,
        deleteContext: deleteContext,
        openSecretsDrawer: openSecretsDrawer,
        deleteSecret: deleteSecret
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
