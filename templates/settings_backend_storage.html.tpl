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
                            <li><a href="/settings/backend-storage" class="active" data-i18n="nav.settings_menu.backend_storage">Backend Storage</a></li>
                            <li><a href="/settings/secrets-vault" data-i18n="nav.settings_menu.secrets_vault">Secrets Vault</a></li>
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
                    <h2 data-i18n="settings.backend_storage.title">Backend Storage</h2>
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
                        <h3>Backend Storage</h3>
                        <p>Configure S3-compatible backend storage for Terraform state files. Supports AWS S3, Minio, DigitalOcean Spaces, and other S3-compatible services.</p>
                        <div id="vaultWarning" class="alert alert-warning" style="display: none; margin-top: 15px;">
                            ⚠️ Vault must be configured before adding backend storage. Please configure Vault in <a href="/settings/secrets-vault">Settings → Secrets Vault</a>.
                        </div>
                    </div>

                    <!-- Add Backend Storage Form -->
                    <div class="activity-section">
                        <div class="activity-header">
                            <h4>Add Backend Storage</h4>
                        </div>
                        <div class="activity-content">
                            <form id="backendStorageForm">
                                <div class="form-group">
                                    <label for="storageName">Storage Name *</label>
                                    <input 
                                        type="text" 
                                        id="storageName" 
                                        name="storageName" 
                                        placeholder="Production S3 Storage"
                                        required
                                    />
                                    <small>A descriptive name for this backend storage configuration</small>
                                </div>

                                <div class="form-group">
                                    <label for="endpointUrl">Endpoint URL *</label>
                                    <input 
                                        type="text" 
                                        id="endpointUrl" 
                                        name="endpointUrl" 
                                        placeholder="https://s3.amazonaws.com or https://nyc3.digitaloceanspaces.com"
                                        required
                                    />
                                    <small>The endpoint URL for your S3-compatible service</small>
                                </div>

                                <div class="form-group">
                                    <label for="bucketName">Bucket Name *</label>
                                    <input 
                                        type="text" 
                                        id="bucketName" 
                                        name="bucketName" 
                                        placeholder="terraform-state-bucket"
                                        required
                                    />
                                    <small>The name of the bucket where state files will be stored</small>
                                </div>

                                <div class="form-group">
                                    <label for="region">Region</label>
                                    <input 
                                        type="text" 
                                        id="region" 
                                        name="region" 
                                        placeholder="us-east-1"
                                        value="us-east-1"
                                    />
                                    <small>AWS region or location for the storage service</small>
                                </div>

                                <div class="form-group">
                                    <label for="vaultPath">Vault Path *</label>
                                    <input 
                                        type="text" 
                                        id="vaultPath" 
                                        name="vaultPath" 
                                        placeholder="colonia/backend-storage/production"
                                        required
                                    />
                                    <small>Path in Vault where credentials will be stored</small>
                                </div>

                                <div class="form-group">
                                    <label for="accessKey">Access Key *</label>
                                    <input 
                                        type="text" 
                                        id="accessKey" 
                                        name="accessKey" 
                                        placeholder="Your access key ID"
                                        required
                                    />
                                    <small>AWS access key ID or equivalent</small>
                                </div>

                                <div class="form-group">
                                    <label for="secretKey">Secret Key *</label>
                                    <input 
                                        type="password" 
                                        id="secretKey" 
                                        name="secretKey" 
                                        placeholder="Your secret access key"
                                        required
                                    />
                                    <small>AWS secret access key or equivalent</small>
                                </div>

                                <div class="form-group">
                                    <label for="accessKeyField">Access Key Field Name</label>
                                    <input 
                                        type="text" 
                                        id="accessKeyField" 
                                        name="accessKeyField" 
                                        placeholder="access_key"
                                        value="access_key"
                                    />
                                    <small>Field name for access key in Vault (default: access_key)</small>
                                </div>

                                <div class="form-group">
                                    <label for="secretKeyField">Secret Key Field Name</label>
                                    <input 
                                        type="text" 
                                        id="secretKeyField" 
                                        name="secretKeyField" 
                                        placeholder="secret_key"
                                        value="secret_key"
                                    />
                                    <small>Field name for secret key in Vault (default: secret_key)</small>
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

                            <!-- Test Results -->
                            <div id="testResults" style="margin-top: 20px;"></div>
                            
                            <!-- Status Messages -->
                            <div id="statusMessage" style="margin-top: 20px;"></div>
                        </div>
                    </div>

                    <!-- Configured Backend Storages List -->
                    <div class="activity-section">
                        <div class="activity-header">
                            <h4>Configured Backend Storages</h4>
                        </div>
                        <div class="activity-content">
                            <div id="storagesList"></div>
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
        // Check if Vault is configured on page load
        document.addEventListener('DOMContentLoaded', function() {
            checkVaultConfiguration();
            loadBackendStorages();
        });

        function checkVaultConfiguration() {
            fetch('/api/vault/config')
                .then(response => response.json())
                .then(data => {
                    if (!data.url || !data.token_set) {
                        document.getElementById('vaultWarning').style.display = 'block';
                        document.getElementById('backendStorageForm').style.display = 'none';
                    } else {
                        document.getElementById('vaultWarning').style.display = 'none';
                        document.getElementById('backendStorageForm').style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Error checking vault config:', error);
                    document.getElementById('vaultWarning').style.display = 'block';
                    document.getElementById('backendStorageForm').style.display = 'none';
                });
        }

        // HTML sanitization function to prevent XSS
        function escapeHtml(unsafe) {
            if (typeof unsafe !== 'string') {
                return unsafe;
            }
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        function showMessage(message, isError = false) {
            const statusDiv = document.getElementById('statusMessage');
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert ${isError ? 'alert-error' : 'alert-success'}`;
            alertDiv.textContent = message;
            statusDiv.innerHTML = '';
            statusDiv.appendChild(alertDiv);
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 5000);
        }

        function showTestResults(results) {
            const resultsDiv = document.getElementById('testResults');
            
            let html = '<div class="card" style="margin-top: 20px;"><h4>Test Results</h4><ul style="list-style: none; padding: 0;">';
            
            results.forEach(result => {
                const icon = result.status === 'success' ? '✓' : '✗';
                const color = result.status === 'success' ? 'green' : 'red';
                const safeStep = escapeHtml(result.step);
                const safeMessage = escapeHtml(result.message);
                html += `<li style="padding: 8px; border-bottom: 1px solid var(--border-color);">
                    <span style="color: ${color}; font-weight: bold;">${icon}</span>
                    <strong>${safeStep}:</strong> ${safeMessage}
                </li>`;
            });
            
            html += '</ul></div>';
            resultsDiv.innerHTML = html;
            
            // Auto-hide after 10 seconds
            setTimeout(() => {
                resultsDiv.innerHTML = '';
            }, 10000);
        }

        // Handle test connection button
        document.getElementById('testConnectionBtn').addEventListener('click', function() {
            const endpointUrl = document.getElementById('endpointUrl').value.trim();
            const bucketName = document.getElementById('bucketName').value.trim();
            const region = document.getElementById('region').value.trim() || 'us-east-1';
            const vaultPath = document.getElementById('vaultPath').value.trim();
            const accessKeyField = document.getElementById('accessKeyField').value.trim() || 'access_key';
            const secretKeyField = document.getElementById('secretKeyField').value.trim() || 'secret_key';

            if (!endpointUrl || !bucketName || !vaultPath) {
                showMessage('Please fill in all required fields before testing', true);
                return;
            }

            const btn = this;
            btn.disabled = true;
            const originalText = btn.innerHTML;
            btn.textContent = 'Testing...';

            fetch('/api/backend-storage/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    endpoint_url: endpointUrl,
                    bucket_name: bucketName,
                    region: region,
                    vault_path: vaultPath,
                    access_key_field: accessKeyField,
                    secret_key_field: secretKeyField
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('✓ All connection tests passed!', false);
                    showTestResults(data.results);
                } else {
                    showMessage('✗ Connection test failed. Check the test results below.', true);
                    showTestResults(data.results);
                }
            })
            .catch(error => {
                showMessage('Error testing connection: ' + error.message, true);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = originalText;
            });
        });

        // Handle form submission
        document.getElementById('backendStorageForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const name = document.getElementById('storageName').value.trim();
            const endpointUrl = document.getElementById('endpointUrl').value.trim();
            const bucketName = document.getElementById('bucketName').value.trim();
            const region = document.getElementById('region').value.trim() || 'us-east-1';
            const vaultPath = document.getElementById('vaultPath').value.trim();
            const accessKey = document.getElementById('accessKey').value.trim();
            const secretKey = document.getElementById('secretKey').value.trim();
            const accessKeyField = document.getElementById('accessKeyField').value.trim() || 'access_key';
            const secretKeyField = document.getElementById('secretKeyField').value.trim() || 'secret_key';

            if (!name || !endpointUrl || !bucketName || !vaultPath || !accessKey || !secretKey) {
                showMessage('Please fill in all required fields', true);
                return;
            }

            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.textContent = 'Saving...';

            fetch('/api/backend-storage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    endpoint_url: endpointUrl,
                    bucket_name: bucketName,
                    region: region,
                    vault_path: vaultPath,
                    access_key: accessKey,
                    secret_key: secretKey,
                    access_key_field: accessKeyField,
                    secret_key_field: secretKeyField
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.id) {
                    showMessage('✓ Backend storage configured successfully!', false);
                    // Reset form
                    document.getElementById('backendStorageForm').reset();
                    document.getElementById('region').value = 'us-east-1';
                    document.getElementById('accessKeyField').value = 'access_key';
                    document.getElementById('secretKeyField').value = 'secret_key';
                    // Reload the list
                    loadBackendStorages();
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

        function loadBackendStorages() {
            fetch('/api/backend-storage')
                .then(response => response.json())
                .then(data => {
                    const listDiv = document.getElementById('storagesList');
                    if (data.storages && data.storages.length > 0) {
                        let html = '<ul style="list-style: none; padding: 0;">';
                        data.storages.forEach(storage => {
                            const safeName = escapeHtml(storage.name);
                            const safeEndpoint = escapeHtml(storage.endpoint_url);
                            const safeBucket = escapeHtml(storage.bucket_name);
                            const safeRegion = escapeHtml(storage.region);
                            const safeVaultPath = escapeHtml(storage.vault_path);
                            // Escape single quotes for onclick attribute
                            const safeNameForAttr = safeName.replace(/'/g, "\\'");
                            
                            html += `<li style="padding: 12px; border: 1px solid var(--border-color); border-radius: 6px; margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <strong>${safeName}</strong><br/>
                                        <small style="color: var(--text-secondary);">
                                            ${safeEndpoint} - Bucket: ${safeBucket} - Region: ${safeRegion}
                                        </small><br/>
                                        <small style="color: var(--text-secondary);">
                                            Vault Path: ${safeVaultPath}
                                        </small>
                                    </div>
                                    <button class="btn btn-danger" onclick="deleteStorage(${storage.id}, '${safeNameForAttr}')" style="padding: 8px 16px;">Delete</button>
                                </div>
                            </li>`;
                        });
                        html += '</ul>';
                        listDiv.innerHTML = html;
                    } else {
                        listDiv.innerHTML = '<p style="color: var(--text-secondary);">No backend storages configured yet.</p>';
                    }
                })
                .catch(error => {
                    console.error('Error loading backend storages:', error);
                    document.getElementById('storagesList').innerHTML = '<p style="color: var(--text-error);">Error loading backend storages.</p>';
                });
        }

        function deleteStorage(storageId, storageName) {
            if (!confirm(`Are you sure you want to delete "${storageName}"? This will not delete credentials from Vault.`)) {
                return;
            }

            fetch(`/api/backend-storage/${storageId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showMessage('✓ ' + data.message, false);
                    loadBackendStorages();
                } else if (data.error) {
                    showMessage('✗ ' + data.error, true);
                }
            })
            .catch(error => {
                showMessage('Error deleting backend storage: ' + error.message, true);
            });
        }
    </script>
</body>
</html>
