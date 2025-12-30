// Sidebar navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get all dropdown toggles
    const dropdownToggles = document.querySelectorAll('.nav-dropdown-toggle');
    
    // Get the dropdown container
    const navDropdown = document.querySelector('.nav-dropdown');
    
    // Check if we're on a settings page to expand the menu by default
    const currentPath = window.location.pathname;
    const isSettingsPage = currentPath.startsWith('/settings/');
    
    // Expand the settings menu if we're on a settings page
    if (isSettingsPage && navDropdown) {
        const dropdownMenu = navDropdown.querySelector('.nav-dropdown-menu');
        if (dropdownMenu) {
            navDropdown.classList.add('open');
        }
    }
    
    // Add click event listeners to all dropdown toggles
    dropdownToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the parent dropdown container
            const parentDropdown = toggle.closest('.nav-dropdown');
            
            if (parentDropdown) {
                // Toggle the open class
                parentDropdown.classList.toggle('open');
            }
        });
    });
});
