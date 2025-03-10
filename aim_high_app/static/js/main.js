// aim_high_app/static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initAccordion();
    initChatFeatures();
    initSummaryFeatures();
    
    // Load initial chat history
    loadChatHistory();
    
    // Check if there's an active summary session
    checkActiveSession();
});

// Accordion functionality
function initAccordion() {
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const parent = this.parentElement;
            parent.classList.toggle('active');
        });
    });
    
    // By default, open the first section
    if (accordionHeaders.length > 0) {
        accordionHeaders[0].parentElement.classList.add('active');
    }
}

// Chat functionality
function initChatFeatures() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');
    
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
    
    // Function to send message
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message === '') return;
        
        // Add user message to UI
        addMessageToUI('user', message);
        
        // Clear input field
        chatInput.value = '';
        
        // Get CSRF token from cookie
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
                scrollChatToBottom();
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
        });
    }
    
    // Function to add message to UI
    window.addMessageToUI = function(sender, message, animate = true) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        
        let senderName = sender === 'user' ? 'You' : 'Jordan';
        
        messageElement.innerHTML = `
            <div class="message-sender">${senderName}:</div>
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
        
        scrollChatToBottom();
    }
    
    // Function to format message with line breaks and links
    function formatMessage(message) {
        return message
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    }
    
    // Function to scroll chat to bottom
    function scrollChatToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Load chat history
function loadChatHistory() {
    fetch('/api/get-chat-history')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const chatMessages = document.getElementById('chat-messages');
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

// Summary features
function initSummaryFeatures() {
    // Learning Material Section
    const materialUrlInput = document.getElementById('material-url');
    const materialContentInput = document.getElementById('material-content');
    const submitMaterialBtn = document.getElementById('submit-material');
    const materialInputForm = document.getElementById('material-input-form');
    const materialPreview = document.getElementById('material-preview');
    const materialContentPreview = document.getElementById('material-content-preview');
    const editMaterialBtn = document.getElementById('edit-material');
    const confirmMaterialBtn = document.getElementById('confirm-material');
    
    // Write Summary Section
    const writeSummarySection = document.getElementById('write-summary-section');
    const summaryContent = document.getElementById('summary-content');
    const generateSummaryBtn = document.getElementById('generate-summary');
    const saveSummaryBtn = document.getElementById('save-summary');
    
    // Feedback Section
    const feedbackSection = document.getElementById('feedback-section');
    const progressFill = document.querySelector('.progress-fill');
    const progressPercentage = document.querySelector('.progress-percentage');
    
    // Submit material
    if (submitMaterialBtn) {
        submitMaterialBtn.addEventListener('click', function() {
            const url = materialUrlInput.value.trim();
            const content = materialContentInput.value.trim();
            
            if (url === '' && content === '') {
                alert('Please provide either a URL or content to proceed.');
                return;
            }
            
            // Get CSRF token from cookie
            const csrftoken = getCookie('csrftoken');
            
            // Send data to API
            fetch('/api/learning-material', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    url: url,
                    manual_content: content,
                    title: '3.4 Unique Characteristics of Eukaryotic Cells'
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    materialContentPreview.textContent = data.content_preview;
                    materialInputForm.classList.add('hidden');
                    materialPreview.classList.remove('hidden');
                    
                    // Update progress
                    updateProgress(7);
                    
                    // Reload chat history
                    loadChatHistory();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error submitting material:', error);
            });
        });
    }
    
    // Edit material
    if (editMaterialBtn) {
        editMaterialBtn.addEventListener('click', function() {
            materialPreview.classList.add('hidden');
            materialInputForm.classList.remove('hidden');
        });
    }
    
    // Confirm material
    if (confirmMaterialBtn) {
        confirmMaterialBtn.addEventListener('click', function() {
            // Open the next section
            writeSummarySection.classList.add('active');
            
            // Get CSRF token from cookie
            const csrftoken = getCookie('csrftoken');
            
            // Generate initial summary suggestion
            fetch('/api/generate-summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Populate summary textarea
                    summaryContent.value = data.summary_text;
                    
                    // Update progress
                    updateProgress(40);
                    
                    // Reload chat history
                    loadChatHistory();
                }
            })
            .catch(error => {
                console.error('Error generating summary:', error);
            });
        });
    }
    
    // Generate summary
    if (generateSummaryBtn) {
        generateSummaryBtn.addEventListener('click', function() {
            // Get CSRF token from cookie
            const csrftoken = getCookie('csrftoken');
            
            fetch('/api/generate-summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Populate summary textarea
                    summaryContent.value = data.summary_text;
                }
            })
            .catch(error => {
                console.error('Error generating summary:', error);
            });
        });
    }
    
    // Save summary
    if (saveSummaryBtn) {
        saveSummaryBtn.addEventListener('click', function() {
            const summary = summaryContent.value.trim();
            
            if (summary === '') {
                alert('Please write or generate a summary before saving.');
                return;
            }
            
            // Get CSRF token from cookie
            const csrftoken = getCookie('csrftoken');
            
            fetch('/api/update-summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    summary_text: summary
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Open feedback section
                    feedbackSection.classList.add('active');
                    
                    // Update progress
                    updateProgress(70);
                    
                    // Get feedback
                    getFeedback();
                    
                    // Reload chat history
                    loadChatHistory();
                }
            })
            .catch(error => {
                console.error('Error saving summary:', error);
            });
        });
    }
    
    // Function to get feedback
    window.getFeedback = function() {
        // Get CSRF token from cookie
        const csrftoken = getCookie('csrftoken');
        
        fetch('/api/evaluate-summary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update knowledge map
                updateKnowledgeMap(data.evaluation.concepts, data.evaluation.relationships);
                
                // Update missing concepts
                updateMissingConcepts(data.evaluation.missing_concepts);
                
                // Update progress
                updateProgress(100);
                
                // Reload chat history
                loadChatHistory();
            }
        })
        .catch(error => {
            console.error('Error getting feedback:', error);
            // If there's an error, still show a sample knowledge map
            updateKnowledgeMap([], []);
        });
    }
    
    // Function to update progress
    window.updateProgress = function(percent) {
        if (progressFill && progressPercentage) {
            progressFill.style.width = percent + '%';
            progressPercentage.textContent = percent + '%';
        }
    }
    
    // Function to update knowledge map
    window.updateKnowledgeMap = function(concepts, relationships) {
        const knowledgeMapContainer = document.getElementById('knowledge-map');
        
        // aim_high_app/static/js/main.js (continued)
        // Check if the container exists
        if (!knowledgeMapContainer) {
            console.error('Knowledge map container not found');
            return;
        }
        
        // Set dimensions
        const width = knowledgeMapContainer.clientWidth || 600;
        const height = 300;
        
        // Clear previous SVG
        knowledgeMapContainer.innerHTML = '';
        
        // Create SVG
        const svg = d3.select('#knowledge-map')
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('style', 'border: 1px solid #eee; border-radius: 4px;');
        
        // Sample data if none is provided
        if (!concepts || concepts.length === 0) {
            concepts = ['mRNA transcript', 'transcription', 'DNA', 'gene', 'RNA polymerase', 'promoter sequence', 'termination', 'initiation', 'elongation'];
        }
        
        if (!relationships || relationships.length === 0) {
            relationships = [
                { source: 'DNA', target: 'gene', type: 'contains' },
                { source: 'gene', target: 'transcription', type: 'undergoes' },
                { source: 'transcription', target: 'mRNA transcript', type: 'produces' },
                { source: 'RNA polymerase', target: 'transcription', type: 'catalyzes' },
                { source: 'promoter sequence', target: 'initiation', type: 'triggers' },
                { source: 'initiation', target: 'elongation', type: 'followed by' },
                { source: 'elongation', target: 'termination', type: 'followed by' }
            ];
        }
        
        // Prepare nodes and links for D3
        const nodes = concepts.map(concept => ({
            id: concept,
            name: concept
        }));
        
        const links = relationships.map(rel => ({
            source: rel.source,
            target: rel.target,
            type: rel.type || 'related'
        }));
        
        // Create a force simulation
        const simulation = d3.forceSimulation(nodes)
            .force('charge', d3.forceManyBody().strength(-150))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
            .force('collision', d3.forceCollide().radius(30));
        
        // Create the links
        const link = svg.append("g")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke-width", 1);
        
        // Create the nodes
        const node = svg.append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("g")
            .data(nodes)
            .join("g");
        
        // Add circles to nodes
        node.append("circle")
            .attr("r", 8)
            .attr("fill", "#f2994a");
        
        // Add text labels
        node.append("text")
            .attr("x", 12)
            .attr("y", ".31em")
            .text(d => d.name)
            .attr("font-size", "12px")
            .attr("font-family", "sans-serif");
        
        // Add title for tooltips
        node.append("title")
            .text(d => d.name);
        
        // Update positions on tick
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
                
            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });
        
        // Add drag functionality
        node.call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
        
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }
        
        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }
        
        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
        
        console.log("Knowledge map updated with", nodes.length, "concepts and", links.length, "relationships");
    }
    
    // Function to update missing concepts
    window.updateMissingConcepts = function(missingConcepts) {
        const grid = document.getElementById('missing-concepts-grid');
        if (!grid) return;
        
        grid.innerHTML = '';
        
        missingConcepts = missingConcepts || [];
        
        if (missingConcepts.length === 0) {
            // Sample concepts if none provided
            missingConcepts = ['DNA', 'Initiation', 'Termination', 'Elongation', 'Gene', 'Promoter Sequence', 'RNA Polymerase', 'mRNA Transcript'];
        }
        
        missingConcepts.forEach(concept => {
            const conceptElement = document.createElement('div');
            conceptElement.className = 'concept-item';
            conceptElement.textContent = concept;
            grid.appendChild(conceptElement);
        });
    }
}

// Check if there's an active session
function checkActiveSession() {
    fetch('/api/get-summary-data')
        .then(response => {
            if (!response.ok) {
                throw new Error('No active session');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Populate UI with existing data
                populateUIFromSession(data);
            }
        })
        .catch(error => {
            console.log('No active session found:', error);
        });
}

// Populate UI from session data
function populateUIFromSession(data) {
    const summary = data.summary;
    
    // Learning Material Section
    if (summary.content) {
        const materialContentPreview = document.getElementById('material-content-preview');
        const materialInputForm = document.getElementById('material-input-form');
        const materialPreview = document.getElementById('material-preview');
        const learningSectionEl = document.getElementById('learning-material-section');
        
        if (materialContentPreview) {
            materialContentPreview.textContent = summary.content.substring(0, 200) + '...';
        }
        
        if (materialInputForm) {
            materialInputForm.classList.add('hidden');
        }
        
        if (materialPreview) {
            materialPreview.classList.remove('hidden');
        }
        
        if (learningSectionEl) {
            learningSectionEl.classList.add('active');
        }
    }
    
    // Write Summary Section
    if (summary.summary_text) {
        const summaryContent = document.getElementById('summary-content');
        const writeSummarySection = document.getElementById('write-summary-section');
        
        if (summaryContent) {
            summaryContent.value = summary.summary_text;
        }
        
        if (writeSummarySection) {
            writeSummarySection.classList.add('active');
        }
    }
    
    // Feedback Section
    if (summary.progress >= 70) {
        const feedbackSection = document.getElementById('feedback-section');
        
        if (feedbackSection) {
            feedbackSection.classList.add('active');
        }
        
        // Update progress
        updateProgress(summary.progress);
        
        // Update knowledge map if concepts and relationships exist
        if (data.concepts && data.concepts.length > 0 && data.relationships && data.relationships.length > 0) {
            const concepts = data.concepts.map(c => c.name);
            updateKnowledgeMap(concepts, data.relationships);
        } else {
            // Use sample data if none available
            updateKnowledgeMap([], []);
        }
        
        // Update missing concepts
        if (data.concepts) {
            const missingConcepts = data.concepts.filter(c => c.is_missing).map(c => c.name);
            updateMissingConcepts(missingConcepts);
        } else {
            updateMissingConcepts([]);
        }
    }
}

// Utility function to get CSRF token from cookies
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