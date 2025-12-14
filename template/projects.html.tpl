<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title data-i18n="app.title">{{ title }}</title>
    <link rel="stylesheet" href="/static/css/styles.css">
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
                        <a href="/projects" class="active">
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
                        <a href="/settings">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            <span data-i18n="nav.settings">Settings</span>
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
                    <h2 data-i18n="page.projects">Projects</h2>
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
                    <!-- Projects Overview Card -->
                    <div class="card">
                        <h3 data-i18n="projects.title">Projects</h3>
                        <p data-i18n="projects.description">Manage your infrastructure projects. Each project represents a collection of stacks and resources.</p>
                    </div>

                    <!-- Projects List -->
                    <div class="activity-section">
                        <div class="activity-header">
                            <h4 data-i18n="projects.list">Project List</h4>
                        </div>
                        <div class="activity-content">
                            <p data-i18n="projects.no_projects">No projects found. Create your first project to get started.</p>
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
</body>
</html>
