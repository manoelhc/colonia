<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title data-i18n="app.title">{{ title }}</title>
    <link rel="stylesheet" href="/static/css/styles.css">
    <script>
        // Apply theme immediately to prevent flash
        (function() {
            const theme = localStorage.getItem('theme') || 
                         (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            if (theme === 'dark') {
                document.documentElement.classList.add('dark');
            }
        })();
    </script>
    <script>
        // Apply cached translations immediately to prevent flash
        (function() {
            const browserLang = (navigator.language || navigator.userLanguage || 'en-US');
            const lang = localStorage.getItem('language') || browserLang.split('-')[0];
            const cachedLang = ['en', 'pt', 'es'].includes(lang) ? lang : 'en';
            const cachedTranslations = localStorage.getItem('translations_' + cachedLang);
            
            if (cachedTranslations) {
                try {
                    const translations = JSON.parse(cachedTranslations);
                    document.documentElement.lang = cachedLang;
                    
                    // Apply translations after DOM is ready but before rendering
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', function() {
                            applyTranslationsSync(translations);
                        });
                    } else {
                        applyTranslationsSync(translations);
                    }
                    
                    function applyTranslationsSync(trans) {
                        document.querySelectorAll('[data-i18n]').forEach(function(element) {
                            const key = element.getAttribute('data-i18n');
                            const translation = key.split('.').reduce(function(o, k) { 
                                return (o || {})[k]; 
                            }, trans);
                            
                            if (translation) {
                                const tagName = element.tagName.toUpperCase();
                                if (tagName === 'INPUT' || tagName === 'TEXTAREA') {
                                    element.placeholder = translation;
                                } else {
                                    element.textContent = translation;
                                }
                            }
                        });
                    }
                } catch (e) {
                    console.warn('Could not apply cached translations:', e);
                }
            }
        })();
    </script>
</head>
<body>
    <div class="dashboard-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <h1 data-i18n="app.title">Colonia</h1>
                <p data-i18n="app.subtitle">Open Source Alternative to Spacelift</p>
            </div>
            <nav class="sidebar-nav">
                <ul>
                    <li>
                        <a href="/">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                            </svg>
                            <span data-i18n="nav.dashboard">Dashboard</span>
                        </a>
                    </li>
                    <li>
                        <a href="/projects">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                            </svg>
                            <span data-i18n="nav.projects">Projects</span>
                        </a>
                    </li>
                    <li>
                        <a href="/stacks">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                            </svg>
                            <span data-i18n="nav.stacks">Stacks</span>
                        </a>
                    </li>
                    <li>
                        <a href="/environments">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <span data-i18n="nav.environments">Environments</span>
                        </a>
                    </li>
                    <li>
                        <a href="/contexts">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>
                            </svg>
                            <span data-i18n="nav.contexts">Contexts</span>
                        </a>
                    </li>
                    <li class="nav-dropdown">
                        <a href="#" class="nav-dropdown-toggle">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            <span data-i18n="nav.settings">Settings</span>
                            <svg class="dropdown-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                        </a>
                        <ul class="nav-dropdown-menu">
                            <li><a href="/settings/ai-integration" data-i18n="nav.settings_menu.ai_integration">AI Integration</a></li>
                            <li><a href="/settings/infracost" data-i18n="nav.settings_menu.infracost">Infracost</a></li>
                            <li><a href="/settings/backend-storage" data-i18n="nav.settings_menu.backend_storage">Backend Storage</a></li>
                            <li><a href="/settings/secrets-vault" class="active" data-i18n="nav.settings_menu.secrets_vault">Secrets Vault</a></li>
                            <li><a href="/settings/container-registry" data-i18n="nav.settings_menu.container_registry">Container Registry</a></li>
                            <li><a href="/settings/database-integration" data-i18n="nav.settings_menu.database_integration">Database Integration</a></li>
                            <li><a href="/settings/rabbitmq-integration" data-i18n="nav.settings_menu.rabbitmq_integration">RabbitMQ Integration</a></li>
                            <li><a href="/settings/redis-integration" data-i18n="nav.settings_menu.redis_integration">Redis Integration</a></li>
                            <li><a href="/settings/github-integration" data-i18n="nav.settings_menu.github_integration">GitHub Integration</a></li>
                            <li><a href="/settings/gitlab-integration" data-i18n="nav.settings_menu.gitlab_integration">GitLab Integration</a></li>
                        </ul>
                    </li>
                    <li>
                        <a href="/users">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                            </svg>
                            <span data-i18n="nav.users">Users</span>
                        </a>
                    </li>
                    <li>
                        <a href="/teams">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                            </svg>
                            <span data-i18n="nav.teams">Teams</span>
                        </a>
                    </li>
                </ul>
            </nav>
        </aside>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Top Navbar -->
            <header class="top-navbar">
                <div class="navbar-inner">
                    <h2 data-i18n="settings.secrets_vault.title">Secrets Vault</h2>
                    <div class="navbar-actions">
                        <!-- Language Selector -->
                        <select id="languageSelector">
                            <option value="en">English</option>
                            <option value="pt">Português</option>
                            <option value="es">Español</option>
                        </select>
                        
                        <!-- Theme Toggle -->
                        <button id="themeToggle">
                            <svg id="themeIconLight" class="hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                            </svg>
                            <svg id="themeIconDark" class="hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                            </svg>
                        </button>

                        <!-- User Menu -->
                        <button>
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </header>

            <!-- Content Area -->
            <main class="content-area">
                <div class="content-wrapper">
                    <!-- Settings Card -->
                    <div class="card">
                        <h3 data-i18n="settings.secrets_vault.title">Secrets Vault</h3>
                        <p data-i18n="settings.secrets_vault.description">Configure your HashiCorp Vault integration for secure secret management.</p>
                    </div>

                    <!-- Settings Form -->
                    <div class="activity-section">
                        <div class="activity-header">
                            <h4 data-i18n="settings.secrets_vault.configuration">Configuration</h4>
                        </div>
                        <div class="activity-content">
                            <form id="vaultConfigForm">
                                <div class="form-group">
                                    <label for="vaultUrl">Vault URL *</label>
                                    <input 
                                        type="text" 
                                        id="vaultUrl" 
                                        name="vaultUrl" 
                                        placeholder="http://localhost:8200"
                                        required
                                    />
                                    <small>The URL of your HashiCorp Vault server (e.g., http://localhost:8200)</small>
                                </div>

                                <div class="form-group">
                                    <label for="vaultToken">Vault Token *</label>
                                    <input 
                                        type="password" 
                                        id="vaultToken" 
                                        name="vaultToken" 
                                        placeholder="Enter your Vault token"
                                        required
                                    />
                                    <small>Authentication token for accessing Vault</small>
                                </div>

                                <div class="form-group">
                                    <label for="vaultNamespace">Vault Namespace (Optional)</label>
                                    <input 
                                        type="text" 
                                        id="vaultNamespace" 
                                        name="vaultNamespace" 
                                        placeholder="Leave empty for non-enterprise Vault"
                                    />
                                    <small>Namespace for Vault Enterprise (leave empty for open source Vault)</small>
                                </div>

                                <div class="form-actions">
                                    <button type="button" id="testConnectionBtn" class="btn btn-secondary">
                                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width: 20px; height: 20px; display: inline-block; margin-right: 8px;">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        Test Connection
                                    </button>
                                    <button type="submit" class="btn btn-primary">
                                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width: 20px; height: 20px; display: inline-block; margin-right: 8px;">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
                                        </svg>
                                        Save Configuration
                                    </button>
                                </div>
                            </form>

                            <!-- Status Messages -->
                            <div id="statusMessage" style="margin-top: 20px;"></div>
                        </div>
                    </div>

                    <!-- Secrets Engine Configuration Section -->
                    <div class="activity-section">
                        <div class="activity-header">
                            <h4>Secrets Engine Configuration</h4>
                        </div>
                        <div class="activity-content">
                            <p>Configure the secrets engine path for Colonia projects. This path will be used to create contexts that can be attached to stacks and environments.</p>
                            
                            <form id="secretsEngineForm">
                                <div class="form-group">
                                    <label for="secretsEngineType">Secrets Engine Type *</label>
                                    <select id="secretsEngineType" name="secretsEngineType" required>
                                        <option value="">Select secrets engine type</option>
                                        <option value="kv">KV (Key-Value) - Version 1</option>
                                        <option value="kv-v2">KV (Key-Value) - Version 2</option>
                                    </select>
                                    <small>Select the type of secrets engine to use</small>
                                </div>

                                <div class="form-group">
                                    <label for="secretsEnginePath">Secrets Engine Path *</label>
                                    <input 
                                        type="text" 
                                        id="secretsEnginePath" 
                                        name="secretsEnginePath" 
                                        placeholder="colonia"
                                        required
                                    />
                                    <small>Path where the secrets engine will be mounted (e.g., colonia, projects, secrets)</small>
                                </div>

                                <div class="form-group" id="maxVersionsGroup" style="display: none;">
                                    <label for="maxVersions">Maximum Number of Versions</label>
                                    <input 
                                        type="number" 
                                        id="maxVersions" 
                                        name="maxVersions" 
                                        placeholder="10"
                                        min="1"
                                        max="100"
                                        value="10"
                                    />
                                    <small>Maximum number of secret versions to keep (KV v2 only, default: 10)</small>
                                </div>

                                <div class="form-actions">
                                    <button type="submit" class="btn btn-primary">
                                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width: 20px; height: 20px; display: inline-block; margin-right: 8px;">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                        </svg>
                                        Enable Secrets Engine
                                    </button>
                                </div>
                            </form>

                            <!-- Secrets Engine Status -->
                            <div id="secretsEngineStatus" style="margin-top: 20px;"></div>

                            <!-- List of Configured Secrets Engines -->
                            <div id="secretsEnginesList" style="margin-top: 20px;"></div>
                        </div>
                    </div>
                </div>
            </main>

            <!-- Footer -->
            <footer class="footer">
                <div class="footer-content">
                    <div class="footer-links">
                        <span>&copy; 2024 Colonia</span>
                        <a href="#" data-i18n="footer.terms">Terms</a>
                        <a href="#" data-i18n="footer.privacy">Privacy</a>
                        <a href="#" data-i18n="footer.cookies">Cookies</a>
                    </div>
                    <div>
                        <span data-i18n="footer.version">Version</span> 0.1.0
                    </div>
                </div>
            </footer>
        </div>
    </div>

    <!-- JavaScript -->
    <script src="/static/js/theme.js"></script>
    <script src="/static/js/i18n.js"></script>
    <script src="/static/js/sidebar.js"></script>
    <script>
        // Load current configuration on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadVaultConfig();
        });

        function loadVaultConfig() {
            fetch('/api/vault/config')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('vaultUrl').value = data.url || '';
                    document.getElementById('vaultNamespace').value = data.namespace || '';
                    // Don't populate the token field for security reasons
                    if (data.token_set) {
                        document.getElementById('vaultToken').placeholder = '••••••••••••••••';
                    }
                })
                .catch(error => {
                    console.error('Error loading vault config:', error);
                });
        }

        function showMessage(message, isError = false) {
            const statusDiv = document.getElementById('statusMessage');
            statusDiv.innerHTML = `
                <div class="alert ${isError ? 'alert-error' : 'alert-success'}">
                    ${message}
                </div>
            `;
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 5000);
        }

        // Handle test connection button
        document.getElementById('testConnectionBtn').addEventListener('click', function() {
            const url = document.getElementById('vaultUrl').value.trim();
            const token = document.getElementById('vaultToken').value.trim();
            const namespace = document.getElementById('vaultNamespace').value.trim();

            if (!url) {
                showMessage('Please enter a Vault URL', true);
                return;
            }

            if (!token) {
                showMessage('Please enter a Vault token', true);
                return;
            }

            const btn = this;
            btn.disabled = true;
            btn.textContent = 'Testing...';

            fetch('/api/vault/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    token: token,
                    namespace: namespace || null
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('✓ ' + data.message, false);
                } else {
                    showMessage('✗ ' + data.message, true);
                }
            })
            .catch(error => {
                showMessage('Error testing connection: ' + error.message, true);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = `
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width: 20px; height: 20px; display: inline-block; margin-right: 8px;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Test Connection
                `;
            });
        });

        // Handle form submission
        document.getElementById('vaultConfigForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const url = document.getElementById('vaultUrl').value.trim();
            const token = document.getElementById('vaultToken').value.trim();
            const namespace = document.getElementById('vaultNamespace').value.trim();

            if (!url) {
                showMessage('Please enter a Vault URL', true);
                return;
            }

            if (!token) {
                showMessage('Please enter a Vault token', true);
                return;
            }

            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.textContent = 'Saving...';

            fetch('/api/vault/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    token: token,
                    namespace: namespace || null
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showMessage('✓ ' + data.message, false);
                    // Clear the token field for security
                    document.getElementById('vaultToken').value = '';
                    document.getElementById('vaultToken').placeholder = '••••••••••••••••';
                } else if (data.error) {
                    showMessage('✗ ' + data.error, true);
                }
            })
            .catch(error => {
                showMessage('Error saving configuration: ' + error.message, true);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });

        // Show/hide max versions field based on secrets engine type
        document.getElementById('secretsEngineType').addEventListener('change', function() {
            const maxVersionsGroup = document.getElementById('maxVersionsGroup');
            if (this.value === 'kv-v2') {
                maxVersionsGroup.style.display = 'block';
            } else {
                maxVersionsGroup.style.display = 'none';
            }
        });

        // Handle secrets engine form submission
        document.getElementById('secretsEngineForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const engineType = document.getElementById('secretsEngineType').value;
            const enginePath = document.getElementById('secretsEnginePath').value.trim();
            const maxVersions = document.getElementById('maxVersions').value;

            if (!engineType) {
                showSecretsEngineMessage('Please select a secrets engine type', true);
                return;
            }

            if (!enginePath) {
                showSecretsEngineMessage('Please enter a secrets engine path', true);
                return;
            }

            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.textContent = 'Enabling...';

            const requestData = {
                engine_type: engineType,
                path: enginePath
            };

            if (engineType === 'kv-v2' && maxVersions) {
                const parsedMaxVersions = parseInt(maxVersions, 10);
                if (!isNaN(parsedMaxVersions) && parsedMaxVersions > 0) {
                    requestData.max_versions = parsedMaxVersions;
                }
            }

            fetch('/api/vault/secrets-engine', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showSecretsEngineMessage('✓ ' + data.message, false);
                    // Reload the list of secrets engines
                    loadSecretsEngines();
                    // Reset form
                    document.getElementById('secretsEngineForm').reset();
                    document.getElementById('maxVersionsGroup').style.display = 'none';
                } else if (data.error) {
                    showSecretsEngineMessage('✗ ' + data.error, true);
                }
            })
            .catch(error => {
                showSecretsEngineMessage('Error enabling secrets engine: ' + error.message, true);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });

        function showSecretsEngineMessage(message, isError = false) {
            const statusDiv = document.getElementById('secretsEngineStatus');
            statusDiv.innerHTML = `
                <div class="alert ${isError ? 'alert-error' : 'alert-success'}">
                    ${message}
                </div>
            `;
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 5000);
        }

        function loadSecretsEngines() {
            fetch('/api/vault/secrets-engines')
                .then(response => response.json())
                .then(data => {
                    const listDiv = document.getElementById('secretsEnginesList');
                    if (data.engines && data.engines.length > 0) {
                        let html = '<h5>Configured Secrets Engines:</h5><ul style="list-style: none; padding: 0;">';
                        data.engines.forEach(engine => {
                            html += `<li style="padding: 8px; border-bottom: 1px solid var(--border-color);">
                                <strong>${engine.path}</strong> - ${engine.type}
                                ${engine.description ? ` (${engine.description})` : ''}
                            </li>`;
                        });
                        html += '</ul>';
                        listDiv.innerHTML = html;
                    } else {
                        listDiv.innerHTML = '<p style="color: var(--text-secondary);">No secrets engines configured yet.</p>';
                    }
                })
                .catch(error => {
                    console.error('Error loading secrets engines:', error);
                });
        }

        // Load secrets engines on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadSecretsEngines();
        });
    </script>
</body>
</html>
