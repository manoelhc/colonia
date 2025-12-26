// Dashboard page JavaScript - handles loading and displaying statistics
(function() {
    // Initialize when DOM is ready
    function init() {
        loadStats();
    }

    // Load statistics via AJAX
    async function loadStats() {
        try {
            const response = await fetch('/api/stats', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load statistics');
            }

            const stats = await response.json();
            updateStatsDisplay(stats);
        } catch (error) {
            console.error('Error loading statistics:', error);
            // Keep default values (0) on error
        }
    }

    // Update the stats display on the page
    function updateStatsDisplay(stats) {
        // Get all stat cards
        const statCards = document.querySelectorAll('.stat-card');
        
        // Map of i18n keys to their values
        const statValues = {
            'stats.projects': stats.projects,
            'stats.stacks': stats.stacks,
            'stats.environments': stats.environments,
            'stats.resources': stats.resources
        };

        // Update each stat card
        statCards.forEach(card => {
            const statHeader = card.querySelector('.stat-header span[data-i18n]');
            if (statHeader) {
                const i18nKey = statHeader.getAttribute('data-i18n');
                const valueElement = card.querySelector('.stat-value');
                
                if (valueElement && i18nKey in statValues) {
                    valueElement.textContent = statValues[i18nKey];
                }
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
