// Users page JavaScript - handles AJAX and modals
(function() {
    let users = [];
    let editingUserId = null;

    // Initialize when DOM is ready
    function init() {
        loadUsers();
        setupEventListeners();
    }

    // Set up event listeners
    function setupEventListeners() {
        // Add user button
        const addBtn = document.getElementById('addUserBtn');
        if (addBtn) {
            addBtn.addEventListener('click', openCreateModal);
        }

        // Modal close buttons
        const closeButtons = document.querySelectorAll('.modal-close');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', closeModal);
        });

        // Modal backdrop click
        const modalBackdrop = document.getElementById('userModal');
        if (modalBackdrop) {
            modalBackdrop.addEventListener('click', function(e) {
                if (e.target === modalBackdrop) {
                    closeModal();
                }
            });
        }

        // Form submission
        const userForm = document.getElementById('userForm');
        if (userForm) {
            userForm.addEventListener('submit', handleFormSubmit);
        }
    }

    // Load users via AJAX
    async function loadUsers() {
        try {
            const response = await fetch('/api/users', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load users');
            }

            const data = await response.json();
            users = data.users || [];
            renderUsers();
        } catch (error) {
            console.error('Error loading users:', error);
            showNotification('Failed to load users', 'error');
        }
    }

    // Render users list
    function renderUsers() {
        const container = document.getElementById('usersList');
        if (!container) return;

        if (users.length === 0) {
            container.innerHTML = '<p class="no-data" data-i18n="users.no_users">No users found. Invite users to collaborate on your projects.</p>';
            return;
        }

        const html = users.map(user => `
            <div class="user-card" data-user-id="${escapeHtml(user.id)}">
                <div class="user-card-header">
                    <div class="user-avatar">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="40" height="40">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                        </svg>
                    </div>
                    <div class="user-info">
                        <h4>${escapeHtml(user.name)}</h4>
                        <p class="user-username">@${escapeHtml(user.username)}</p>
                        <p class="user-email">${escapeHtml(user.email)}</p>
                    </div>
                    <div class="user-actions">
                        <button class="btn-icon" onclick="usersModule.editUser(${user.id})" title="Edit">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button class="btn-icon" onclick="usersModule.deleteUser(${user.id})" title="Delete">
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
        editingUserId = null;
        document.getElementById('modalTitle').textContent = 'Create User';
        document.getElementById('userForm').reset();
        document.getElementById('userModal').classList.add('show');
    }

    // Open edit modal
    function editUser(id) {
        const user = users.find(u => u.id === id);
        if (!user) return;

        editingUserId = id;
        document.getElementById('modalTitle').textContent = 'Edit User';
        document.getElementById('username').value = user.username;
        document.getElementById('email').value = user.email;
        document.getElementById('name').value = user.name;
        document.getElementById('userModal').classList.add('show');
    }

    // Close modal
    function closeModal() {
        document.getElementById('userModal').classList.remove('show');
        editingUserId = null;
    }

    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();

        const formData = {
            username: document.getElementById('username').value.trim(),
            email: document.getElementById('email').value.trim(),
            name: document.getElementById('name').value.trim()
        };

        try {
            const url = editingUserId 
                ? `/api/users/${editingUserId}`
                : '/api/users';
            
            const method = editingUserId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to save user');
            }

            showNotification(
                editingUserId ? 'User updated successfully' : 'User created successfully',
                'success'
            );
            closeModal();
            loadUsers();
        } catch (error) {
            console.error('Error saving user:', error);
            showNotification(error.message, 'error');
        }
    }

    // Delete user
    async function deleteUser(id) {
        const user = users.find(u => u.id === id);
        if (!user) return;

        if (!confirm(`Are you sure you want to delete user "${user.name}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/users/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to delete user');
            }

            showNotification('User deleted successfully', 'success');
            loadUsers();
        } catch (error) {
            console.error('Error deleting user:', error);
            showNotification('Failed to delete user', 'error');
        }
    }

    // Show notification
    function showNotification(message, type = 'info') {
        // Simple notification - could be enhanced with a better UI
        console.log(`${type.toUpperCase()}: ${message}`);
        alert(message);
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Export module functions
    window.usersModule = {
        editUser: editUser,
        deleteUser: deleteUser
    };

    // Initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
