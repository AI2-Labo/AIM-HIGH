document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat features
    initChatFeatures();
    
    // Initialize accordion items
    initAccordion();
    
    // Initialize sidebar submenu
    initSidebar();
    
    // Load chat history if needed
    if (!document.querySelector('.message.assistant')) {
        loadChatHistory();
    }
});

// Initialize the sidebar
function initSidebar() {
    const subMenuToggle = document.querySelectorAll('.submenu-toggle');
    
    subMenuToggle.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const parent = this.parentElement;
            const submenu = parent.querySelector('.submenu');
            
            if (submenu) {
                if (submenu.style.display === 'block') {
                    submenu.style.display = 'none';
                    this.textContent = '▾';
                } else {
                    submenu.style.display = 'block';
                    this.textContent = '▴';
                }
            }
        });
    });
}

// Accordion functionality
function initAccordion() {
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const parent = this.parentElement;
            const content = parent.querySelector('.accordion-content');
            const toggle = this.querySelector('.accordion-toggle');
            
            if (parent.classList.contains('active')) {
                parent.classList.remove('active');
                content.style.display = 'none';
                toggle.textContent = '▾';
            } else {
                parent.classList.add('active');
                content.style.display = 'block';
                toggle.textContent = '▴';
            }
        });
    });
}

// Chat functionality
function initChatFeatures() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    
    if (!chatInput || !sendButton) return;
    
    // Send message when button is clicked
    sendButton.addEventListener('click', function() {
        sendMessage();
    });
    
    // Send message when Enter key is pressed
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

// Function to send message
function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();
    if (message === '') return;
    
    // Add user message to UI
    addMessageToUI('user', message);
    
    // Clear input field
    chatInput.value = '';
    
    // Get CSRF token
    const csrftoken = getCookie('csrftoken');
    
    // Send message to API
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            message: message
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Add assistant message to UI
            addMessageToUI('assistant', data.message);
            
            // Scroll to bottom
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    })
    .catch(error => {
        console.error('Error sending message:', error);
    });
}

// Function to add message to UI
window.addMessageToUI = function(sender, message, animate = true) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;
    
    let senderName = sender === 'user' ? 'You:' : 'Abby:';
    
    messageElement.innerHTML = `
        <div class="message-sender">${senderName}</div>
        <div class="message-content">${formatMessage(message)}</div>
    `;
    
    if (animate) {
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        messageElement.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    }
    
    chatMessages.appendChild(messageElement);
    
    if (animate) {
        // Trigger animation
        setTimeout(() => {
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        }, 10);
    }
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
};

// Function to format message with line breaks and links
function formatMessage(message) {
    if (!message) return '';
    return message
        .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
}

// Load chat history
function loadChatHistory() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    fetch('/api/get-chat-history')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                chatMessages.innerHTML = '';
                
                data.messages.forEach(msg => {
                    addMessageToUI(msg.sender, msg.message, false);
                });
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        })
        .catch(error => {
            console.error('Error loading chat history:', error);
        });
}

// Function to update progress bar
function updateProgress(percent) {
    const progressFill = document.querySelector('.progress-fill');
    const progressPercentage = document.querySelector('.progress-percentage');
    
    if (progressFill && progressPercentage) {
        progressFill.style.width = percent + '%';
        progressPercentage.textContent = percent + '%';
    }
}

// Helper function to get cookie by name (for CSRF token)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}