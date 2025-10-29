class ChatbotInterface {
    constructor() {
        this.apiUrl = 'http://127.0.0.1:8000';
        this.conversationHistory = [];
        this.initializeElements();
    this.checkApiStatus();
    }

    initializeElements() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.apiStatus = document.getElementById('apiStatus');

        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    async checkApiStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/health`, {
                mode: 'cors',
                credentials: 'omit'
            });
            if (response.ok) {
                this.setApiStatus(true);
                this.enableInput();
            } else {
                throw new Error('API not responding');
            }
        } catch (error) {
            console.error('API connection failed:', error);
            this.setApiStatus(false);
            this.enableInput(); // Enable input even if API is down so user can see the error
            this.addMessage('bot', '⚠️ Cannot connect to the API server. Please make sure:\n1. The API is running (python run.py)\n2. The API is accessible at http://127.0.0.1:8000\n3. Check the browser console for CORS errors');
        }
    }

    setApiStatus(connected) {
        this.apiStatus.textContent = connected ? 'API Connected' : 'API Disconnected';
        this.apiStatus.className = `api-status ${connected ? 'connected' : 'disconnected'}`;
    }

    enableInput() {
        this.messageInput.disabled = false;
        this.sendButton.disabled = false;
        this.messageInput.placeholder = "Type your message or select a number option...";
    }

    // Removed auto initial conversation to avoid sending 'start' that triggers refusal

    addMessage(sender, content, showNumberOptions = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);

        // Disabled number options UI to avoid random expansions

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // Add to conversation history
        this.conversationHistory.push({
            role: sender === 'user' ? 'user' : 'assistant',
            content: content,
            timestamp: new Date().toISOString()
        });
    }

    selectOption(number) {
        this.messageInput.value = number;
        this.sendMessage();
    }

    showTyping() {
        this.typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }

    hideTyping() {
        this.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Add user message
        this.addMessage('user', message);
        this.messageInput.value = '';

        // Send to bot
        await this.sendToBot(message);
    }

    async sendToBot(message) {
        this.showTyping();
        this.sendButton.disabled = true;

        try {
            const response = await fetch(`${this.apiUrl}/api/v1/chat/`, {
                method: 'POST',
                mode: 'cors',
                credentials: 'omit',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: this.conversationHistory
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Simulate typing delay
            setTimeout(() => {
                this.hideTyping();
                
                // Always render plain text without clickable options
                this.addMessage('bot', data.response, false);
                this.sendButton.disabled = false;
            }, 1000 + Math.random() * 1000); // 1-2 second delay

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTyping();
            this.addMessage('bot', 'Sorry, I encountered an error. Please try again.');
            this.sendButton.disabled = false;
        }
    }
}

// Initialize the chatbot interface when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatbotInterface();
});