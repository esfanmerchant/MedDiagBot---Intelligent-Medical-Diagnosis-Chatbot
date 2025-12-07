let isWaitingForResponse = false;

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Initialize theme on load
initTheme();

// Toggle Sidebar for Mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
}

// Get current time
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

async function initChat() {
    document.getElementById('welcomeSection').style.display = 'none';
    document.getElementById('messagesArea').style.display = 'block';
    document.getElementById('inputContainer').style.display = 'block';
    
    // Initialize chat with backend
    try {
        const response = await fetch('/init', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            setTimeout(() => {
                addBotMessage(data.message);
            }, 600);
        }
    } catch (error) {
        console.error('Error:', error);
        addBotMessage("Hello! I'm your AI Health Assistant. 👋\n\nWhat's your name?");
    }
    
    document.getElementById('messageInput').focus();
}

function startNewChat() {
    location.reload();
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message || isWaitingForResponse) return;
    
    // Add user message
    addUserMessage(message);
    input.value = '';
    autoResize(input);
    
    // Disable input while waiting
    isWaitingForResponse = true;
    document.getElementById('sendButton').disabled = true;
    input.disabled = true;
    
    // Show typing indicator with random delay (600-1400ms)
    const thinkingDelay = Math.random() * 800 + 600;
    showTypingIndicator();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // Wait for minimum thinking animation time
        await new Promise(resolve => setTimeout(resolve, thinkingDelay));
        
        removeTypingIndicator();
        
        if (data.success) {
            if (data.is_result) {
                // Show final result
                addResultMessage(data);
            } else {
                // Show regular bot message
                addBotMessage(data.message);
            }
        } else {
            addBotMessage(data.message || 'Something went wrong. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addBotMessage('Sorry, I encountered an error. Please try again.');
    } finally {
        isWaitingForResponse = false;
        document.getElementById('sendButton').disabled = false;
        input.disabled = false;
        document.getElementById('messageInput').focus();
    }
}

function addUserMessage(message) {
    const messagesArea = document.getElementById('messagesArea');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-time">${getCurrentTime()}</div>
            <div class="message-bubble">${escapeHtml(message)}</div>
        </div>
        <div class="message-avatar">You</div>
    `;
    
    messagesArea.appendChild(messageDiv);
    scrollToBottom();
}

function addBotMessage(message) {
    const messagesArea = document.getElementById('messagesArea');
    
    // Clean up excessive line breaks
    const cleanMessage = message.replace(/\n\n+/g, '\n').trim();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-time">${getCurrentTime()}</div>
            <div class="message-bubble">${escapeHtml(cleanMessage).replace(/\n/g, '<br>')}</div>
        </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const messagesArea = document.getElementById('messagesArea');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="typing-bubble">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    
    messagesArea.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function addResultMessage(data) {
    const messagesArea = document.getElementById('messagesArea');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    
    let precautionsHtml = '';
    if (data.precautions && data.precautions.length > 0) {
        precautionsHtml = `
            <div class="info-section">
                <h4>🛡️ Recommended Precautions</h4>
                <ul class="precautions-list">
                    ${data.precautions.map(p => `<li>${escapeHtml(p)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-time">${getCurrentTime()}</div>
            <div class="message-bubble">
                Thank you for providing all the information, ${escapeHtml(data.name)}! 🎉
                <br><br>
                I've completed my analysis. Here's your comprehensive health assessment:
            </div>
            
            <div class="result-card">
                <div class="result-header">
                    <div class="result-icon">📋</div>
                    <div class="result-title">Medical Assessment Report</div>
                </div>
                
                <div class="diagnosis-box">
                    <div class="diagnosis-label">Predicted Condition</div>
                    <div class="disease-name">${escapeHtml(data.disease)}</div>
                    
                    <div class="confidence-bar">
                        <div class="confidence-label">
                            <span>AI Confidence Level</span>
                            <span class="confidence-percent">${data.confidence}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%" data-width="${data.confidence}%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="risk-box ${data.risk_class}">
                    <div class="risk-icon">⚠️</div>
                    <div class="risk-message">${escapeHtml(data.risk_message)}</div>
                </div>
                
                <div class="info-section">
                    <h4>📖 About This Condition</h4>
                    <p>${escapeHtml(data.description)}</p>
                </div>
                
                ${precautionsHtml}
                
                <div class="quote-box">
                    ${escapeHtml(data.quote)}
                </div>
            </div>
        </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    scrollToBottom();
    
    // Animate progress bar
    setTimeout(() => {
        const progressFill = messageDiv.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = progressFill.dataset.width;
        }
    }, 200);
    
    // Show disclaimer and new chat option
    setTimeout(() => {
        const disclaimerMsg = document.createElement('div');
        disclaimerMsg.className = 'message bot';
        disclaimerMsg.innerHTML = `
            <div class="message-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <div class="message-content">
                <div class="message-time">${getCurrentTime()}</div>
                <div class="message-bubble">
                    ⚕️ <strong>Important Reminder:</strong> This is an AI-based assessment for educational purposes only. 
                    <br><br>
                    Please consult a qualified healthcare professional for accurate diagnosis and treatment.
                    <br><br>
                    Would you like to start a new consultation? Click <strong>"New Consultation"</strong> in the sidebar.
                </div>
            </div>
        `;
        messagesArea.appendChild(disclaimerMsg);
        scrollToBottom();
    }, 800);
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-resize textarea
const textarea = document.getElementById('messageInput');
if (textarea) {
    textarea.addEventListener('input', function() {
        autoResize(this);
    });
}

function autoResize(element) {
    element.style.height = 'auto';
    element.style.height = Math.min(element.scrollHeight, 150) + 'px';
}

// Focus input on load
window.addEventListener('load', () => {
    const input = document.getElementById('messageInput');
    if (input) {
        input.focus();
    }
});