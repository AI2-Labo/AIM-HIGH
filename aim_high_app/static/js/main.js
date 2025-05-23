document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat features
    initChatFeatures();
    
    // Initialize accordion items
    initAccordion();
    
    // Initialize sidebar submenu
    initSidebar();
    
    // Initialize context-aware chatbot
    initContextAwareChatbot();
});

// Initialize the context-aware chatbot
function initContextAwareChatbot() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages || chatMessages.children.length > 0) return;

    // Determine current page context if not already set
    if (!window.currentPage) {
        window.currentPage = {
            name: document.body.dataset.page || 'home',
            url: window.location.pathname,
            title: document.title
        };
    }
    
    // Get current time for appropriate greeting
    const currentTime = new Date();
    let greeting = 'Hello';
    
    if (currentTime.getHours() < 12) {
        greeting = 'Good morning';
    } else if (currentTime.getHours() < 18) {
        greeting = 'Good afternoon';
    } else {
        greeting = 'Good evening';
    }
    
    // Add appropriate greeting based on the page
    let message = '';
    
    if (window.location.pathname.includes('/profile/')) {
        message = `${greeting} Dr. Kim,

I see you're viewing your profile information. Here you can update your personal and professional details that will be displayed to students. 

Need any help with your profile information? I'm happy to provide suggestions for your professional bio.`;
    } 
    else if (window.location.pathname.includes('/learning-materials/')) {
        message = `${greeting} Dr. Kim,

Welcome to the Learning Materials section. Here you can manage all your educational content for creating assignments.

You can add new materials from various sources like:
• Online textbooks (OpenStax)
• Videos
• YouTube clips
• Files (presentations, documents, PDFs)
• Online resources (blogs, websites)

Let me know if you need help adding or managing your learning materials!`;
    } 
    else if (window.location.pathname.includes('/learning-material/manage/')) {
        message = `${greeting} Dr. Kim,

I see you're adding or editing a learning material. This is where you can define the source content for your assignments.

To complete this process:
1. Add a descriptive title for your material
2. Select the appropriate source type
3. Provide the URL or link to the content
4. View a preview of the complete webpage

Let me know if you need any assistance with this process!`;
    }
    else if (window.location.pathname.includes('/assignments/causality-analysis/')) {
        message = `${greeting} Dr. Kim,

I see you're working on a causality analysis assignment. This is where you can create and analyze cause-and-effect relationships in your learning materials.

You can:
• Select a learning material to analyze
• Create reference models that show relationships between concepts
• View previous reference models by clicking on them in the log section

Need help with creating a new causality model or understanding the existing ones?`;
    }
    else if (window.location.pathname.includes('/assignments/')) {
        message = `${greeting} Dr. Kim,

Welcome to the Assignments section where you can create and manage different types of learning activities.

You can create various assignment types:
• Summarization - For content summary exercises
• Causality Analysis - For exploring cause-effect relationships
• Solution Explanation - For problem-solving tasks
• Argumentation - For developing persuasive arguments
• Creative Writing - For narrative and creative exercises

Let me know which type of assignment you'd like to create or manage!`;
    }
    else if (window.location.pathname.includes('/test/')) {
        message = `${greeting} Dr. Kim,

Welcome to the evaluation feature! This is where you can test your understanding of the learning material by writing a summary.

I'll evaluate your summary by analyzing how well it covers the key concepts in the topic. You'll receive:
• A similarity score (shown in the progress bar)
• A knowledge map showing included concepts (blue) and missing concepts (orange)
• A list of any concepts that were missing from your summary
• A quality rating and personalized feedback

Try writing a summary of the eukaryotic cells content in the text area, then click "Evaluate" to see your results!`;
    }
    else {
        // Default greeting for home page or other pages
        message = `${greeting} Dr. Kim,

How can I assist you today? I'm here to help with:
• Creating and managing learning materials
• Setting up causality analysis assignments
• Testing your students' understanding of key concepts
• Providing feedback on summaries

Let me know what you'd like to work on!`;
    }
    
    // Add the greeting to the chat
    addMessageToUI('assistant', message);
}

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
    
    // Get current page context
    const context = window.currentPage || {
        name: 'unknown',
        url: window.location.pathname,
        title: document.title
    };
    
    // Get CSRF token
    const csrftoken = getCookie('csrftoken');
    
    // Send message to API with context
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            message: message,
            context: context
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
        // Fallback response if API fails
        const fallbackResponse = getFallbackResponse(message, context);
        addMessageToUI('assistant', fallbackResponse);
    });
}

// Function to get a fallback response (for when API fails)
function getFallbackResponse(message, context) {
    // Get current time for appropriate greeting
    const currentTime = new Date();
    let greeting = 'Hello';
    
    if (currentTime.getHours() < 12) {
        greeting = 'Good morning';
    } else if (currentTime.getHours() < 18) {
        greeting = 'Good afternoon';
    } else {
        greeting = 'Good evening';
    }
    
    // Simple keyword matching for fallback responses
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('help')) {
        return `${greeting} Dr. Kim, I'd be happy to help! What specific part of the application are you having trouble with?`;
    } else if (lowerMessage.includes('thank')) {
        return "You're welcome! Let me know if you need anything else.";
    } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi ')) {
        return `${greeting} Dr. Kim! How can I assist you with your learning activities today?`;
    } else if (lowerMessage.includes('summary')) {
        return "For summarization assignments, you should focus on identifying and including all the key concepts from the learning material. Would you like some tips on writing an effective summary?";
    } else if (lowerMessage.includes('causality') || lowerMessage.includes('cause') || lowerMessage.includes('effect')) {
        return "Causality analysis involves identifying cause-and-effect relationships between key concepts. This helps students understand how different ideas connect and influence each other. Would you like help with creating a causality model?";
    } else {
        return `I understand. Is there something specific about the current page that I can help you with? I'm here to assist with any questions you have.`;
    }
}

// Function to add message to UI
window.addMessageToUI = function(sender, message, animate = true) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;
    
    let senderName = sender === 'user' ? 'You:' : 'Jordan:';
    
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