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
        
        // Map of stat types to their values
        const statValues = {
            'Projects': stats.projects,
            'Stacks': stats.stacks,
            'Runs': stats.runs,
            'Resources': stats.resources
        };

        // Update each stat card
        statCards.forEach(card => {
            const statHeader = card.querySelector('.stat-header span');
            if (statHeader) {
                const statName = statHeader.textContent;
                const valueElement = card.querySelector('.stat-value');
                
                if (valueElement && statValues.hasOwnProperty(statName)) {
                    valueElement.textContent = statValues[statName];
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
