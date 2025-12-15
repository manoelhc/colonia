// Internationalization (i18n) management
(function() {
    let translations = {};
    let currentLanguage = 'en';

    // Get language from localStorage or browser
    function getLanguage() {
        const stored = localStorage.getItem('language');
        if (stored) {
            return stored;
        }
        // Get browser language
        const browserLang = navigator.language || navigator.userLanguage;
        const lang = browserLang.split('-')[0]; // Get just the language code
        return ['en', 'pt', 'es'].includes(lang) ? lang : 'en';
    }

    // Load translations
    async function loadTranslations(lang) {
        try {
            const response = await fetch(`/static/locales/${lang}.json`);
            if (!response.ok) {
                console.warn(`Could not load translations for ${lang}, falling back to English`);
                if (lang !== 'en') {
                    return loadTranslations('en');
                }
                return {};
            }
            const data = await response.json();
            // Cache translations in localStorage for instant access on next load
            try {
                localStorage.setItem(`translations_${lang}`, JSON.stringify(data));
            } catch (e) {
                console.warn('Could not cache translations:', e);
            }
            return data;
        } catch (error) {
            console.error('Error loading translations:', error);
            return {};
        }
    }

    // Apply translations to the page
    function applyTranslations() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = getNestedTranslation(translations, key);
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

    // Get nested translation by key (e.g., "app.title")
    function getNestedTranslation(obj, key) {
        return key.split('.').reduce((o, k) => (o || {})[k], obj);
    }

    // Change language
    async function changeLanguage(lang) {
        currentLanguage = lang;
        translations = await loadTranslations(lang);
        applyTranslations();
        localStorage.setItem('language', lang);
        
        // Update selector
        const selector = document.getElementById('languageSelector');
        if (selector) {
            selector.value = lang;
        }

        // Update HTML lang attribute
        document.documentElement.lang = lang;
    }

    // Initialize
    async function init() {
        const lang = getLanguage();
        await changeLanguage(lang);

        // Add event listener to language selector
        const selector = document.getElementById('languageSelector');
        if (selector) {
            selector.addEventListener('change', (e) => {
                changeLanguage(e.target.value);
            });
        }
    }

    // Run initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
