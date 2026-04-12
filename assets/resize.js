function setupResizeObserver() {
    var sidebar = document.getElementById('sidebar');
    if (!sidebar) {
        setTimeout(setupResizeObserver, 500);
        return;
    }

    var observer = new MutationObserver(function() {
        setTimeout(function() {
            window.dispatchEvent(new Event('resize'));
        }, 300);
    });

    observer.observe(sidebar, { 
        attributes: true, 
        attributeFilter: ['class'] 
    });
}

setupResizeObserver();