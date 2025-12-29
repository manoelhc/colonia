// Teams page JavaScript - handles AJAX and modals
(function() {
    let teams = [];
    let users = [];
    let projects = [];
    let environments = [];
    let stacks = [];
    let editingTeamId = null;
    let currentTeamId = null;

    // Initialize when DOM is ready
    function init() {
        loadTeams();
        loadUsers();
        loadProjects();
        loadEnvironments();
        loadStacks();
        setupEventListeners();
    }

    // Set up event listeners
    function setupEventListeners() {
        // Add team button
        const addBtn = document.getElementById('addTeamBtn');
        if (addBtn) {
            addBtn.addEventListener('click', openCreateModal);
        }

        // Modal close buttons
        const closeButtons = document.querySelectorAll('.modal-close');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', closeModals);
        });

        // Modal backdrop clicks
        const modals = ['teamModal', 'membersModal', 'permissionsModal'];
        modals.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.addEventListener('click', function(e) {
                    if (e.target === modal) {
                        closeModals();
                    }
                });
            }
        });

        // Form submissions
        const teamForm = document.getElementById('teamForm');
        if (teamForm) {
            teamForm.addEventListener('submit', handleFormSubmit);
        }

        const addMemberForm = document.getElementById('addMemberForm');
        if (addMemberForm) {
            addMemberForm.addEventListener('submit', handleAddMember);
        }

        const addPermissionForm = document.getElementById('addPermissionForm');
        if (addPermissionForm) {
            addPermissionForm.addEventListener('submit', handleAddPermission);
        }
    }

    // Load teams via AJAX
    async function loadTeams() {
        try {
            const response = await fetch('/api/teams', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load teams');
            }

            const data = await response.json();
            teams = data.teams || [];
            renderTeams();
        } catch (error) {
            console.error('Error loading teams:', error);
            showNotification('Failed to load teams', 'error');
        }
    }

    // Load users
    async function loadUsers() {
        try {
            const response = await fetch('/api/users');
            if (response.ok) {
                const data = await response.json();
                users = data.users || [];
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    // Load projects
    async function loadProjects() {
        try {
            const response = await fetch('/api/projects');
            if (response.ok) {
                const data = await response.json();
                projects = data.projects || [];
            }
        } catch (error) {
            console.error('Error loading projects:', error);
        }
    }

    // Load environments
    async function loadEnvironments() {
        try {
            const response = await fetch('/api/environments/grouped');
            if (response.ok) {
                const data = await response.json();
                environments = [];
                data.projects.forEach(project => {
                    project.environments.forEach(env => {
                        environments.push({...env, projectName: project.name});
                    });
                });
            }
        } catch (error) {
            console.error('Error loading environments:', error);
        }
    }

    // Load stacks
    async function loadStacks() {
        try {
            const response = await fetch('/api/stacks/grouped');
            if (response.ok) {
                const data = await response.json();
                stacks = [];
                data.projects.forEach(project => {
                    project.environments.forEach(env => {
                        env.stacks.forEach(stack => {
                            stacks.push({...stack, projectName: project.name, envName: env.name});
                        });
                    });
                });
            }
        } catch (error) {
            console.error('Error loading stacks:', error);
        }
    }

    // Render teams list
    function renderTeams() {
        const container = document.getElementById('teamsList');
        if (!container) return;

        if (teams.length === 0) {
            container.innerHTML = '<p class="no-data" data-i18n="teams.no_teams">No teams found. Create teams to organize users and manage permissions.</p>';
            return;
        }

        const html = teams.map(team => `
            <div class="team-card" data-team-id="${escapeHtml(team.id)}">
                <div class="team-card-header">
                    <div class="team-info">
                        <h4>${escapeHtml(team.name)}</h4>
                        <p class="team-description">${escapeHtml(team.description || '')}</p>
                    </div>
                    <div class="team-actions">
                        <button class="btn-secondary btn-sm" onclick="teamsModule.manageMembers(${team.id})" title="Manage Members">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                            </svg>
                            Members (${team.members.length})
                        </button>
                        <button class="btn-secondary btn-sm" onclick="teamsModule.managePermissions(${team.id})" title="Manage Permissions">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                            </svg>
                            Permissions (${team.permissions.length})
                        </button>
                        <button class="btn-icon" onclick="teamsModule.editTeam(${team.id})" title="Edit">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button class="btn-icon" onclick="teamsModule.deleteTeam(${team.id})" title="Delete">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // Open create modal
    function openCreateModal() {
        editingTeamId = null;
        document.getElementById('modalTitle').textContent = 'Create Team';
        document.getElementById('teamForm').reset();
        document.getElementById('teamModal').classList.add('active');
    }

    // Open edit modal
    function editTeam(id) {
        const team = teams.find(t => t.id === id);
        if (!team) return;

        editingTeamId = id;
        document.getElementById('modalTitle').textContent = 'Edit Team';
        document.getElementById('teamName').value = team.name;
        document.getElementById('teamDescription').value = team.description || '';
        document.getElementById('teamModal').classList.add('active');
    }

    // Close all modals
    function closeModals() {
        document.getElementById('teamModal').classList.remove('active');
        document.getElementById('membersModal').classList.remove('active');
        document.getElementById('permissionsModal').classList.remove('active');
        editingTeamId = null;
        currentTeamId = null;
    }

    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();

        const formData = {
            name: document.getElementById('teamName').value.trim(),
            description: document.getElementById('teamDescription').value.trim()
        };

        try {
            const url = editingTeamId 
                ? `/api/teams/${editingTeamId}`
                : '/api/teams';
            
            const method = editingTeamId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to save team');
            }

            showNotification(
                editingTeamId ? 'Team updated successfully' : 'Team created successfully',
                'success'
            );
            closeModals();
            loadTeams();
        } catch (error) {
            console.error('Error saving team:', error);
            showNotification(error.message, 'error');
        }
    }

    // Delete team
    async function deleteTeam(id) {
        const team = teams.find(t => t.id === id);
        if (!team) return;

        if (!confirm(`Are you sure you want to delete team "${team.name}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/teams/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to delete team');
            }

            showNotification('Team deleted successfully', 'success');
            loadTeams();
        } catch (error) {
            console.error('Error deleting team:', error);
            showNotification('Failed to delete team', 'error');
        }
    }

    // Manage team members
    function manageMembers(teamId) {
        currentTeamId = teamId;
        const team = teams.find(t => t.id === teamId);
        if (!team) return;

        document.getElementById('membersModalTitle').textContent = `Manage Members - ${team.name}`;
        renderMembers(team);
        renderUserSelector();
        document.getElementById('membersModal').classList.add('active');
    }

    // Render members list
    function renderMembers(team) {
        const container = document.getElementById('membersList');
        if (!container) return;

        if (team.members.length === 0) {
            container.innerHTML = '<p class="no-data">No members in this team.</p>';
            return;
        }

        const html = team.members.map(member => `
            <div class="member-item">
                <div class="member-info">
                    <strong>${escapeHtml(member.name)}</strong>
                    <span class="member-username">@${escapeHtml(member.username)}</span>
                    <span class="member-role badge">${escapeHtml(member.role)}</span>
                </div>
                <button class="btn-icon" onclick="teamsModule.removeMember(${team.id}, ${member.id})" title="Remove">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // Render user selector
    function renderUserSelector() {
        const select = document.getElementById('userSelect');
        if (!select) return;

        const html = users.map(user => 
            `<option value="${user.id}">${escapeHtml(user.name)} (@${escapeHtml(user.username)})</option>`
        ).join('');

        select.innerHTML = '<option value="">Select a user</option>' + html;
    }

    // Handle add member
    async function handleAddMember(e) {
        e.preventDefault();

        const userId = document.getElementById('userSelect').value;
        const role = document.getElementById('memberRole').value;

        if (!userId) {
            showNotification('Please select a user', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/teams/${currentTeamId}/members`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: parseInt(userId), role: role })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to add member');
            }

            showNotification('Member added successfully', 'success');
            document.getElementById('addMemberForm').reset();
            loadTeams().then(() => {
                const team = teams.find(t => t.id === currentTeamId);
                if (team) renderMembers(team);
            });
        } catch (error) {
            console.error('Error adding member:', error);
            showNotification(error.message, 'error');
        }
    }

    // Remove member
    async function removeMember(teamId, memberId) {
        if (!confirm('Are you sure you want to remove this member?')) {
            return;
        }

        try {
            const response = await fetch(`/api/teams/${teamId}/members/${memberId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to remove member');
            }

            showNotification('Member removed successfully', 'success');
            loadTeams().then(() => {
                const team = teams.find(t => t.id === teamId);
                if (team) renderMembers(team);
            });
        } catch (error) {
            console.error('Error removing member:', error);
            showNotification('Failed to remove member', 'error');
        }
    }

    // Manage team permissions
    function managePermissions(teamId) {
        currentTeamId = teamId;
        const team = teams.find(t => t.id === teamId);
        if (!team) return;

        document.getElementById('permissionsModalTitle').textContent = `Manage Permissions - ${team.name}`;
        renderPermissions(team);
        renderResourceSelectors();
        document.getElementById('permissionsModal').classList.add('active');
    }

    // Render permissions list
    function renderPermissions(team) {
        const container = document.getElementById('permissionsList');
        if (!container) return;

        if (team.permissions.length === 0) {
            container.innerHTML = '<p class="no-data">No permissions set for this team.</p>';
            return;
        }

        const html = team.permissions.map(perm => {
            let resourceName = `${perm.resource_type} #${perm.resource_id}`;
            if (perm.resource_type === 'project') {
                const project = projects.find(p => p.id === perm.resource_id);
                if (project) resourceName = `Project: ${project.name}`;
            } else if (perm.resource_type === 'environment') {
                const env = environments.find(e => e.id === perm.resource_id);
                if (env) resourceName = `Environment: ${env.name} (${env.projectName})`;
            } else if (perm.resource_type === 'stack') {
                const stack = stacks.find(s => s.id === perm.resource_id);
                if (stack) resourceName = `Stack: ${stack.name} (${stack.projectName}/${stack.envName})`;
            }

            return `
                <div class="permission-item">
                    <div class="permission-info">
                        <strong>${escapeHtml(resourceName)}</strong>
                        <div class="permission-flags">
                            ${perm.can_view ? '<span class="badge badge-success">View</span>' : ''}
                            ${perm.can_plan ? '<span class="badge badge-info">Plan</span>' : ''}
                            ${perm.can_apply ? '<span class="badge badge-warning">Apply</span>' : ''}
                        </div>
                    </div>
                    <button class="btn-icon" onclick="teamsModule.removePermission(${team.id}, ${perm.id})" title="Remove">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    }

    // Render resource selectors
    function renderResourceSelectors() {
        const typeSelect = document.getElementById('resourceType');
        const resourceSelect = document.getElementById('resourceId');
        
        if (!typeSelect || !resourceSelect) return;

        typeSelect.addEventListener('change', function() {
            updateResourceOptions(this.value);
        });

        updateResourceOptions(typeSelect.value);
    }

    // Update resource options based on type
    function updateResourceOptions(type) {
        const resourceSelect = document.getElementById('resourceId');
        if (!resourceSelect) return;

        let options = '<option value="">Select a resource</option>';

        if (type === 'project') {
            options += projects.map(p => 
                `<option value="${p.id}">${escapeHtml(p.name)}</option>`
            ).join('');
        } else if (type === 'environment') {
            options += environments.map(e => 
                `<option value="${e.id}">${escapeHtml(e.name)} (${escapeHtml(e.projectName)})</option>`
            ).join('');
        } else if (type === 'stack') {
            options += stacks.map(s => 
                `<option value="${s.id}">${escapeHtml(s.name)} (${escapeHtml(s.projectName)}/${escapeHtml(s.envName)})</option>`
            ).join('');
        }

        resourceSelect.innerHTML = options;
    }

    // Handle add permission
    async function handleAddPermission(e) {
        e.preventDefault();

        const resourceType = document.getElementById('resourceType').value;
        const resourceId = document.getElementById('resourceId').value;
        const canView = document.getElementById('canView').checked;
        const canPlan = document.getElementById('canPlan').checked;
        const canApply = document.getElementById('canApply').checked;

        if (!resourceId) {
            showNotification('Please select a resource', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/teams/${currentTeamId}/permissions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resource_type: resourceType,
                    resource_id: parseInt(resourceId),
                    can_view: canView,
                    can_plan: canPlan,
                    can_apply: canApply
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to set permission');
            }

            showNotification('Permission set successfully', 'success');
            document.getElementById('addPermissionForm').reset();
            loadTeams().then(() => {
                const team = teams.find(t => t.id === currentTeamId);
                if (team) renderPermissions(team);
            });
        } catch (error) {
            console.error('Error setting permission:', error);
            showNotification(error.message, 'error');
        }
    }

    // Remove permission
    async function removePermission(teamId, permissionId) {
        if (!confirm('Are you sure you want to remove this permission?')) {
            return;
        }

        try {
            const response = await fetch(`/api/teams/${teamId}/permissions/${permissionId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to remove permission');
            }

            showNotification('Permission removed successfully', 'success');
            loadTeams().then(() => {
                const team = teams.find(t => t.id === teamId);
                if (team) renderPermissions(team);
            });
        } catch (error) {
            console.error('Error removing permission:', error);
            showNotification('Failed to remove permission', 'error');
        }
    }

    // Show notification
    function showNotification(message, type = 'info') {
        console.log(`${type.toUpperCase()}: ${message}`);
        alert(message);
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Export module functions
    window.teamsModule = {
        editTeam: editTeam,
        deleteTeam: deleteTeam,
        manageMembers: manageMembers,
        removeMember: removeMember,
        managePermissions: managePermissions,
        removePermission: removePermission
    };

    // Initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
