(function() {
    function inIframe() {
        try {
            return window.self !== window.top;
        } catch (e) {
            return true;
        }
    }

    function contentOnly() {
        var urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('content_only') !== null;
    }

    function removeIfExists(el) {
        if (el) {
            el.remove();
        };
    }

    function adjustBinderLink() {
        // Binder links to .py instead of .ipynb. In an ideal world, there
        // would be a way to do it in _config.yml or you could tell Jupyter to
        // use the Notebook interface to open the .py but ?factory=Notebook
        // does not work on the mybinder.org URL only on the
        // hub.2i2c.mybinder.org URL
        var elements = document.querySelectorAll(
            'a[href^="https://mybinder.org"], a[href^="https://colab.research.google.com"]');
        elements.forEach(
            function(el) {
                el.href = el.href.replace(/python_scripts\/(.+)\.py/, "notebooks/$1.ipynb");
            }
        );
    }

    function openColabInNewTab() {
        // Every "Open in Colab" link (the badge on lesson pages, the badge at
        // the top of workbooks, the launch button of the theme) opens in a
        // new tab, so the reader keeps the book open.
        document.querySelectorAll('a[href^="https://colab.research.google.com"]').forEach(
            function(el) {
                el.target = '_blank';
                el.rel = 'noopener';
            }
        );
    }

    function addColabBadge() {
        // Lesson pages are built from python_scripts/<name>.py; the matching
        // notebook lives in notebooks/<name>.ipynb.
        var match = window.location.pathname.match(/python_scripts\/([^\/]+)\.html$/);
        var article = document.querySelector('article.bd-article') ||
            document.querySelector('#main-content');
        if (!match || !article) {
            return;
        }
        var link = document.createElement('a');
        link.href = 'https://colab.research.google.com/github/' +
            'marcinsawinski/scikit-learn-mooc/blob/main/notebooks/' +
            match[1] + '.ipynb';
        link.target = '_blank';
        link.rel = 'noopener';
        link.className = 'colab-badge remove-from-content-only';
        link.innerHTML = '<img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>';
        article.insertBefore(link, article.firstChild);
    }

    function displayContentOnly() {
        removeIfExists(document.querySelector('#site-navigation'));
        removeIfExists(document.querySelector('.topbar'));
        removeIfExists(document.querySelector('.footer'));
        // the prev/next buttons at the bottom of the page may have a different
        // class (depending on the theme version maybe?), removing both to be
        // safe.
        removeIfExists(document.querySelector('.prev-next-bottom'));
        removeIfExists(document.querySelector('.prev-next-area'));
        var elementsToRemove = document.querySelectorAll('.remove-from-content-only');
        elementsToRemove.forEach(
            function(el) {
                removeIfExists(el);
            }
        );
        document.querySelector('#main-content').querySelector('.col-md-9').className = 'col-12';

        var style = document.createElement('style');
        style.appendChild(
            document.createTextNode(
                'hypothesis-sidebar, hypothesis-notebook, hypothesis-adder{display:none!important;}'));
        document.getElementsByTagName('head')[0].appendChild(style);
    }

    function fixSidebarToggle() {
        // The page has two "toggle primary sidebar" buttons: a hidden one in
        // the header and the visible one above the article. The theme only
        // wires up the first, so the visible button does nothing. Make it
        // hide/show the left sidebar on wide screens (the choice is
        // remembered from page to page), and open the navigation drawer on
        // narrow screens as the theme intends.
        var buttons = document.querySelectorAll('.primary-toggle');
        var sidebar = document.querySelector('#pst-primary-sidebar');
        if (buttons.length < 2 || !sidebar) {
            return;
        }
        // 960px is the width below which the theme switches to its mobile
        // layout, where the sidebar is a drawer.
        var storageKey = 'mooc-sidebar-hidden';

        function setHidden(hidden) {
            sidebar.classList.toggle('pst-sidebar-hidden', hidden);
            document.body.classList.toggle('mooc-sidebar-hidden', hidden);
            try {
                window.localStorage.setItem(storageKey, hidden ? '1' : '0');
            } catch (e) {}
        }

        var remembered = null;
        try {
            remembered = window.localStorage.getItem(storageKey);
        } catch (e) {}
        if (remembered === '1' && window.matchMedia('(min-width: 960px)').matches) {
            setHidden(true);
        }

        Array.prototype.slice.call(buttons, 1).forEach(function(button) {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                if (window.matchMedia('(min-width: 960px)').matches) {
                    setHidden(!sidebar.classList.contains('pst-sidebar-hidden'));
                } else {
                    buttons[0].click();
                }
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function() {
        fixSidebarToggle();
        addColabBadge();
        if (inIframe() || contentOnly()) {
            displayContentOnly();
        }
        adjustBinderLink();
        openColabInNewTab();
    });
}());
