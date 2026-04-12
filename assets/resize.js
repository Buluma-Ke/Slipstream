document.addEventListener('DOMContentLoaded', function() {
    var toggle = document.getElementById('sidebar-toggle');
    if (toggle) {
        toggle.addEventListener('click', function() {
            setTimeout(function() {
                window.dispatchEvent(new Event('resize'));
            }, 300);
        });
    }

    var observer = new MutationObserver(function() {
        window.dispatchEvent(new Event('resize'));
    });

    var sidebar = document.getElementById('sidebar');
    if (sidebar) {
        observer.observe(sidebar, { attributes: true, attributeFilter: ['class'] });
    }
});