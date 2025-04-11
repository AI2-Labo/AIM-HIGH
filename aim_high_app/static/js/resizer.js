document.addEventListener('DOMContentLoaded', function() {
    initResizer();
});

function initResizer() {
    const resizer = document.getElementById('panel-resizer');
    const mainContent = document.querySelector('.main-content');
    const chatPanel = document.querySelector('.chat-panel');
    
    if (!resizer || !mainContent || !chatPanel) return;
    
    // Store original flex values to use as a reset reference
    const originalMainFlex = window.getComputedStyle(mainContent).getPropertyValue('flex');
    const originalChatFlex = window.getComputedStyle(chatPanel).getPropertyValue('flex');
    
    // Initial total width of both panels
    let initialTotalWidth;
    
    // Remember whether we're currently resizing
    let isResizing = false;
    
    // Add event listeners
    resizer.addEventListener('mousedown', startResize);
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
    
    // Touch support
    resizer.addEventListener('touchstart', startResizeTouch);
    document.addEventListener('touchmove', resizeTouch);
    document.addEventListener('touchend', stopResize);
    
    // Start the resize operation
    function startResize(e) {
        isResizing = true;
        initialTotalWidth = mainContent.clientWidth + chatPanel.clientWidth;
        resizer.classList.add('dragging');
        
        // Disable selection during resize
        document.body.style.userSelect = 'none';
        document.body.style.cursor = 'col-resize';
        
        // Prevent default to avoid text selection during drag
        e.preventDefault();
    }
    
    // Touch version of startResize
    function startResizeTouch(e) {
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent('mousedown', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        startResize(mouseEvent);
    }
    
    // Handle the resize operation
    function resize(e) {
        if (!isResizing) return;
        
        // Calculate the container's width and position
        const contentWrapper = document.querySelector('.content-wrapper');
        const containerRect = contentWrapper.getBoundingClientRect();
        
        // Calculate mouse position relative to container
        const mousePosition = e.clientX - containerRect.left;
        
        // Calculate the percentage of the container width
        const leftPercentage = (mousePosition / containerRect.width) * 100;
        
        // Ensure we stay within min/max bounds (30%-70%)
        const boundedLeftPercentage = Math.min(Math.max(leftPercentage, 30), 70);
        const rightPercentage = 100 - boundedLeftPercentage;
        
        // Set flex values based on percentages
        mainContent.style.flex = `0 0 ${boundedLeftPercentage}%`;
        chatPanel.style.flex = `0 0 ${rightPercentage}%`;
        
        // Prevent elements from shrinking too small
        if (mainContent.clientWidth < containerRect.width * 0.3) {
            mainContent.style.flex = `0 0 30%`;
            chatPanel.style.flex = `0 0 70%`;
        } else if (chatPanel.clientWidth < containerRect.width * 0.3) {
            mainContent.style.flex = `0 0 70%`;
            chatPanel.style.flex = `0 0 30%`;
        }
    }
    
    // Touch version of resize
    function resizeTouch(e) {
        if (!isResizing) return;
        
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent('mousemove', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        resize(mouseEvent);
        
        // Prevent scrolling while resizing
        e.preventDefault();
    }
    
    // End the resize operation
    function stopResize() {
        if (!isResizing) return;
        
        isResizing = false;
        resizer.classList.remove('dragging');
        
        // Re-enable selection
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
        
        // Store the new sizes in local storage for persistence
        const mainContentWidth = mainContent.clientWidth;
        const chatPanelWidth = chatPanel.clientWidth;
        const totalWidth = mainContentWidth + chatPanelWidth;
        
        try {
            localStorage.setItem('mainContentPercentage', (mainContentWidth / totalWidth * 100).toString());
            localStorage.setItem('chatPanelPercentage', (chatPanelWidth / totalWidth * 100).toString());
        } catch (e) {
            console.warn('Could not save panel sizes to localStorage', e);
        }
    }
    
    // Apply saved sizes if available
    try {
        const mainContentPercentage = localStorage.getItem('mainContentPercentage');
        const chatPanelPercentage = localStorage.getItem('chatPanelPercentage');
        
        if (mainContentPercentage && chatPanelPercentage) {
            mainContent.style.flex = `0 0 ${mainContentPercentage}%`;
            chatPanel.style.flex = `0 0 ${chatPanelPercentage}%`;
        }
    } catch (e) {
        console.warn('Could not load saved panel sizes', e);
    }
    
    // Double click to reset to original sizes
    resizer.addEventListener('dblclick', function() {
        mainContent.style.flex = originalMainFlex;
        chatPanel.style.flex = originalChatFlex;
        
        // Clear saved sizes
        try {
            localStorage.removeItem('mainContentPercentage');
            localStorage.removeItem('chatPanelPercentage');
        } catch (e) {
            console.warn('Could not clear saved panel sizes', e);
        }
    });
}