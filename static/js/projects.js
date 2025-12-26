// Projects page JavaScript - handles AJAX and modals
(function() {
    let projects = [];
    let editingProjectId = null;

    // Initialize when DOM is ready
    function init() {
        loadProjects();
        setupEventListeners();
    }

    // Set up event listeners
    function setupEventListeners() {
        // Add project button
        const addBtn = document.getElementById('addProjectBtn');
        if (addBtn) {
            addBtn.addEventListener('click', openCreateModal);
        }

        // Modal close buttons
        const closeButtons = document.querySelectorAll('.modal-close');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', closeModal);
        });

        // Modal backdrop click
        const modalBackdrop = document.getElementById('projectModal');
        if (modalBackdrop) {
            modalBackdrop.addEventListener('click', function(e) {
                if (e.target === modalBackdrop) {
                    closeModal();
                }
            });
        }

        // Form submission
        const projectForm = document.getElementById('projectForm');
        if (projectForm) {
            projectForm.addEventListener('submit', handleFormSubmit);
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
            renderProjects();
        } catch (error) {
            console.error('Error loading projects:', error);
            showNotification('Failed to load projects', 'error');
        }
    }

    // Render projects list
    function renderProjects() {
        const container = document.getElementById('projectsList');
        if (!container) return;

        if (projects.length === 0) {
            container.innerHTML = '<p class="no-data" data-i18n="projects.no_projects">No projects found. Create your first project to get started.</p>';
            return;
        }

        const html = projects.map(project => `
            <div class="project-card" data-project-id="${escapeHtml(project.id)}">
                <div class="project-card-header">
                    <h4>${escapeHtml(project.name)}</h4>
                    <div class="project-actions">
                        ${project.repository_url ? `
                        <button class="btn-icon" onclick="projectsModule.refreshProject(${project.id})" title="Refresh from repository">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                            </svg>
                        </button>
                        ` : ''}
                        <button class="btn-icon" onclick="projectsModule.editProject(${project.id})" title="Edit">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button class="btn-icon" onclick="projectsModule.deleteProject(${project.id})" title="Delete">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="project-card-body">
                    ${project.description ? `<p>${escapeHtml(project.description)}</p>` : '<p class="text-muted">No description</p>'}
                    ${project.repository_url ? `<p class="project-url"><a href="${escapeHtml(project.repository_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(project.repository_url)}</a></p>` : ''}
                </div>
                <div class="project-card-footer">
                    <small class="text-muted">Created: ${formatDate(project.created_at)}</small>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // Open create modal
    function openCreateModal() {
        editingProjectId = null;
        document.getElementById('modalTitle').textContent = 'Create New Project';
        document.getElementById('projectForm').reset();
        document.getElementById('projectModal').classList.add('show');
    }

    // Open edit modal
    function openEditModal(projectId) {
        const project = projects.find(p => p.id === projectId);
        if (!project) return;

        editingProjectId = projectId;
        document.getElementById('modalTitle').textContent = 'Edit Project';
        document.getElementById('projectName').value = project.name;
        document.getElementById('projectDescription').value = project.description || '';
        document.getElementById('projectRepository').value = project.repository_url || '';
        document.getElementById('projectModal').classList.add('show');
    }

    // Close modal
    function closeModal() {
        document.getElementById('projectModal').classList.remove('show');
        document.getElementById('projectForm').reset();
        editingProjectId = null;
    }

    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();

        const name = document.getElementById('projectName').value.trim();
        const description = document.getElementById('projectDescription').value.trim();
        const repository_url = document.getElementById('projectRepository').value.trim();

        // Client-side validation
        if (!name) {
            showNotification('Project name is required', 'error');
            return;
        }

        if (name.length > 255) {
            showNotification('Project name is too long (max 255 characters)', 'error');
            return;
        }

        if (description && description.length > 1000) {
            showNotification('Description is too long (max 1000 characters)', 'error');
            return;
        }

        const data = {
            name: name,
            description: description || null,
            repository_url: repository_url || null
        };

        try {
            const url = editingProjectId 
                ? `/api/projects/${editingProjectId}`
                : '/api/projects';
            
            const method = editingProjectId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to save project');
            }

            showNotification(
                editingProjectId ? 'Project updated successfully' : 'Project created successfully',
                'success'
            );
            
            closeModal();
            loadProjects();
        } catch (error) {
            console.error('Error saving project:', error);
            showNotification(error.message || 'Failed to save project', 'error');
        }
    }

    // Delete project
    async function deleteProject(projectId) {
        if (!confirm('Are you sure you want to delete this project?')) {
            return;
        }

        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const result = await response.json();
                throw new Error(result.error || 'Failed to delete project');
            }

            showNotification('Project deleted successfully', 'success');
            loadProjects();
        } catch (error) {
            console.error('Error deleting project:', error);
            showNotification(error.message || 'Failed to delete project', 'error');
        }
    }

    // Refresh project from repository
    async function refreshProject(projectId) {
        try {
            showNotification('Triggering repository scan...', 'info');
            
            const response = await fetch(`/api/projects/${projectId}/scan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to trigger repository scan');
            }

            showNotification('Repository scan triggered successfully! Resources will be updated shortly.', 'success');
        } catch (error) {
            console.error('Error refreshing project:', error);
            showNotification(error.message || 'Failed to trigger repository scan', 'error');
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
    window.projectsModule = {
        editProject: openEditModal,
        deleteProject: deleteProject,
        refreshProject: refreshProject
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
