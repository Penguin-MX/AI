document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatContainer = document.getElementById('chatContainer');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const newChatBtn = document.querySelector('.new-chat-btn');
    const chatHistory = document.getElementById('chatHistory');
    const settingsBtn = document.getElementById('settingsBtn');
    const settingsModal = document.getElementById('settingsModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    const themeToggle = document.getElementById('themeToggle');
    const typingIndicator = document.getElementById('typingIndicator');
    const temperatureSlider = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperatureValue');

    // Settings variables
    let currentSettings = {
        model: 'openai/gpt-3.5-turbo',
        maxTokens: 1000,
        temperature: 0.7,
        systemInstructions: ''
    };

    // Chat variables
    let currentChatId = null;
    let chats = {};

    // Initialize the app
    function init() {
        loadSettings();
        loadChats();
        createNewChat();
        setupEventListeners();
        applyTheme();
    }

    // Load settings from localStorage
    function loadSettings() {
        const savedSettings = localStorage.getItem('quickai_settings');
        if (savedSettings) {
            currentSettings = JSON.parse(savedSettings);
            document.getElementById('modelSelect').value = currentSettings.model;
            document.getElementById('maxTokens').value = currentSettings.maxTokens;
            document.getElementById('temperature').value = currentSettings.temperature;
            document.getElementById('temperatureValue').textContent = currentSettings.temperature;
            
            // Set system instructions - use saved value or default for the model
            const systemInstructionsField = document.getElementById('systemInstructions');
            if (currentSettings.systemInstructions) {
                systemInstructionsField.value = currentSettings.systemInstructions;
            } else if (modelSystemPrompts[currentSettings.model]) {
                systemInstructionsField.value = modelSystemPrompts[currentSettings.model];
                currentSettings.systemInstructions = modelSystemPrompts[currentSettings.model];
            }
        } else {
            // Initialize with default model system prompt
            const defaultModel = document.getElementById('modelSelect').value;
            if (modelSystemPrompts[defaultModel]) {
                document.getElementById('systemInstructions').value = modelSystemPrompts[defaultModel];
                currentSettings.systemInstructions = modelSystemPrompts[defaultModel];
            }
        }
    }

    // Save settings to localStorage
    function saveSettings() {
        currentSettings.model = document.getElementById('modelSelect').value;
        currentSettings.maxTokens = parseInt(document.getElementById('maxTokens').value);
        currentSettings.temperature = parseFloat(document.getElementById('temperature').value);
        currentSettings.systemInstructions = document.getElementById('systemInstructions').value;
        localStorage.setItem('quickai_settings', JSON.stringify(currentSettings));
    }

    // Load chats from localStorage
    function loadChats() {
        const savedChats = localStorage.getItem('quickai_chats');
        if (savedChats) {
            chats = JSON.parse(savedChats);
            updateChatHistory();
        }
    }

    // Save chats to localStorage
    function saveChats() {
        localStorage.setItem('quickai_chats', JSON.stringify(chats));
        updateChatHistory();
    }

    // Create a new chat
    function createNewChat() {
        const chatId = 'chat_' + Date.now();
        chats[chatId] = {
            title: 'New Chat',
            messages: []
        };
        currentChatId = chatId;
        clearChatContainer();
        saveChats();
        // Add welcome message
        const welcomeMessage = chatContainer.innerHTML;
        chatContainer.innerHTML = welcomeMessage;
    }

    // Update chat history sidebar
    function updateChatHistory() {
        chatHistory.innerHTML = '';
        Object.keys(chats).forEach(chatId => {
            const chat = chats[chatId];
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-item';
            chatItem.textContent = chat.title;
            chatItem.dataset.chatId = chatId;
            if (chatId === currentChatId) {
                chatItem.style.backgroundColor = 'rgba(229, 57, 53, 0.1)';
            }
            chatItem.addEventListener('click', () => loadChat(chatId));
            chatHistory.appendChild(chatItem);
        });
    }

    // Load a specific chat
    function loadChat(chatId) {
        currentChatId = chatId;
        clearChatContainer();
        const chat = chats[chatId];
        chat.messages.forEach(message => {
            addMessageToUI(message.role, message.content);
        });
        updateChatHistory();
    }

    // Clear chat container
    function clearChatContainer() {
        chatContainer.innerHTML = '';
    }

    // Add message to UI
    function addMessageToUI(role, content) {
        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container';

        const avatar = document.createElement('div');
        avatar.className = `avatar ${role === 'user' ? 'user-avatar' : 'ai-avatar'}`;
        avatar.textContent = role === 'user' ? 'You' : 'AI';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const messageHeader = document.createElement('div');
        messageHeader.className = 'message-header';
        messageHeader.textContent = role === 'user' ? 'You' : 'Quick AI';

        const message = document.createElement('div');
        message.className = `message ${role === 'user' ? 'user-message' : 'ai-message'} markdown-content`;

        // Process content based on role
        if (role === 'user') {
            message.textContent = content;
        } else {
            // Process markdown, LaTeX, and code highlighting for AI responses
            message.innerHTML = processMarkdown(content);
            renderMathInElement(message);
            highlightCode(message);
        }

        messageContent.appendChild(messageHeader);
        messageContent.appendChild(message);

        messageContainer.appendChild(avatar);
        messageContainer.appendChild(messageContent);

        chatContainer.appendChild(messageContainer);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Process markdown content
    function processMarkdown(content) {
        return marked.parse(content);
    }

    // Highlight code blocks
    function highlightCode(element) {
        element.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }

    // Model identity system prompts
    const modelSystemPrompts = {
        'openai': 'You are OpenAI GPT-4.1-nano, a helpful AI assistant with text and image understanding capabilities.',
        'openai-large': 'You are OpenAI GPT-4.1 mini, a powerful AI assistant with advanced text and image understanding capabilities.',
        'openai-reasoning': 'You are OpenAI o4-mini, an AI assistant with strong reasoning capabilities and vision abilities.',
        'qwen-coder': 'You are Qwen 2.5 Coder 32B, a specialized AI assistant for programming and code-related tasks.',
        'llama': 'You are Llama 3.3 70B, a large language model trained to be helpful, harmless, and honest.',
        'llamascout': 'You are Llama 4 Scout 17B, an AI assistant designed for exploration and information gathering.',
        'mistral': 'You are Mistral Small 3, an AI assistant with text and image understanding capabilities.',
        'unity': 'You are Unity Mistral Large, an uncensored AI assistant with text and image understanding capabilities.',
        'midijourney': 'You are Midijourney, an AI assistant specialized in music and audio-related tasks.',
        'rtist': 'You are Rtist, an AI assistant specialized in art and creative tasks.',
        'searchgpt': 'You are SearchGPT, an AI assistant with text and image understanding capabilities and search functionality.',
        'evil': 'You are Evil, an uncensored AI assistant with text and image understanding capabilities.',
        'deepseek-reasoning': 'You are DeepSeek-R1 Distill Qwen 32B, an AI assistant with advanced reasoning capabilities.',
        'deepseek-reasoning-large': 'You are DeepSeek R1 - Llama 70B, a large AI assistant with advanced reasoning capabilities.',
        'phi': 'You are Phi-4 Instruct, an AI assistant with text, image, and audio understanding capabilities.',
        'llama-vision': 'You are Llama 3.2 11B Vision, an AI assistant with text and image understanding capabilities.',
        'gemini': 'You are gemini-2.5-flash-preview-04-17, an AI assistant with text, image, and audio understanding capabilities.',
        'hormoz': 'You are Hormoz 8b, an AI assistant specialized in text understanding.',
        'hypnosis-tracy': 'You are Hypnosis Tracy 7B, an AI assistant with text and audio understanding capabilities.',
        'deepseek': 'You are DeepSeek-V3, an AI assistant specialized in text understanding.',
        'sur': 'You are Sur AI Assistant (Mistral), an AI assistant with text and image understanding capabilities.',
        'openai-audio': 'You are OpenAI GPT-4o-audio-preview, an AI assistant with text, image, and audio understanding capabilities.'
    };

    // Send message to AI
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Check for commands
        if (message.startsWith('/')) {
            handleCommand(message);
            messageInput.value = '';
            return;
        }

        // Add user message to UI and chat history
        addMessageToUI('user', message);
        if (currentChatId && chats[currentChatId]) {
            chats[currentChatId].messages.push({
                role: 'user',
                content: message
            });
        }

        // Clear input
        messageInput.value = '';

        // Show typing indicator
        typingIndicator.style.display = 'block';

        try {
            // Get system prompt based on model or use custom one
            const systemPrompt = currentSettings.systemInstructions || modelSystemPrompts[currentSettings.model] || '';
            
            // Send to API
            const response = await fetch('/api/generate-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: message,
                    model: currentSettings.model,
                    max_tokens: currentSettings.maxTokens,
                    temperature: currentSettings.temperature,
                    system_instructions: systemPrompt
                })
            });

            const data = await response.json();
            
            // Hide typing indicator
            typingIndicator.style.display = 'none';

            // Add AI response to UI and chat history
            const aiResponse = data.choices ? data.choices[0].message.content : data.text || 'Sorry, I could not generate a response.';
            addMessageToUI('assistant', aiResponse);
            
            if (currentChatId && chats[currentChatId]) {
                chats[currentChatId].messages.push({
                    role: 'assistant',
                    content: aiResponse
                });
                
                // Generate title if this is the first exchange
                if (chats[currentChatId].messages.length === 2 && chats[currentChatId].title === 'New Chat') {
                    generateTitle(message, aiResponse);
                }
            }

            // Save chats
            saveChats();
        } catch (error) {
            console.error('Error:', error);
            typingIndicator.style.display = 'none';
            addMessageToUI('assistant', 'Sorry, there was an error processing your request.');
        }
    }

    // Generate a title for the chat
    async function generateTitle(userMessage, aiResponse) {
        try {
            const response = await fetch('/api/generate-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: `Generate a short title (4-6 words) for a conversation that starts with this exchange. User: "${userMessage}" AI: "${aiResponse.substring(0, 100)}..."`,
                    model: currentSettings.model,
                    max_tokens: 20,
                    temperature: 0.7
                })
            });

            const data = await response.json();
            const title = data.choices ? data.choices[0].message.content : data.text || 'New Chat';
            chats[currentChatId].title = title.replace(/"/g, '').trim();
            saveChats();
        } catch (error) {
            console.error('Error generating title:', error);
        }
    }

    // Handle commands
    function handleCommand(command) {
        const cmd = command.toLowerCase();
        
        if (cmd === '/clear') {
            createNewChat();
        } else if (cmd === '/title') {
            if (currentChatId && chats[currentChatId] && chats[currentChatId].messages.length >= 2) {
                const userMessage = chats[currentChatId].messages[0].content;
                const aiResponse = chats[currentChatId].messages[1].content;
                generateTitle(userMessage, aiResponse);
                addMessageToUI('assistant', 'Chat title has been regenerated.');
            } else {
                addMessageToUI('assistant', 'Need at least one exchange to generate a title.');
            }
        } else if (cmd.startsWith('/image ')) {
            const prompt = command.substring(7).trim();
            if (prompt) {
                generateImage(prompt);
            } else {
                addMessageToUI('assistant', 'Please provide a prompt for the image generation.');
            }
        } else {
            addMessageToUI('assistant', `Unknown command: ${command}. Available commands: /clear, /title, /image <prompt>`);
        }
    }

    // Generate image
    async function generateImage(prompt) {
        addMessageToUI('user', `/image ${prompt}`);
        typingIndicator.style.display = 'block';

        try {
            const response = await fetch('/api/generate-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt })
            });

            const data = await response.json();
            typingIndicator.style.display = 'none';

            if (data.image_url) {
                const imageMarkdown = `![${prompt}](${data.image_url})`;
                addMessageToUI('assistant', imageMarkdown);
                
                if (currentChatId && chats[currentChatId]) {
                    chats[currentChatId].messages.push(
                        { role: 'user', content: `/image ${prompt}` },
                        { role: 'assistant', content: imageMarkdown }
                    );
                    saveChats();
                }
            } else {
                addMessageToUI('assistant', 'Sorry, there was an error generating the image.');
            }
        } catch (error) {
            console.error('Error generating image:', error);
            typingIndicator.style.display = 'none';
            addMessageToUI('assistant', 'Sorry, there was an error generating the image.');
        }
    }

    // Apply theme
    function applyTheme() {
        const isDarkMode = localStorage.getItem('quickai_dark_mode') === 'true';
        document.body.classList.toggle('dark-theme', isDarkMode);
        themeToggle.checked = isDarkMode;
    }

    // Setup event listeners
    function setupEventListeners() {
        // Send message on button click
        sendBtn.addEventListener('click', sendMessage);

        // Send message on Enter key (but allow Shift+Enter for new lines)
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = (messageInput.scrollHeight) + 'px';
        });

        // New chat button
        newChatBtn.addEventListener('click', createNewChat);

        // Settings modal
        settingsBtn.addEventListener('click', () => {
            settingsModal.style.display = 'flex';
        });

        closeModalBtn.addEventListener('click', () => {
            settingsModal.style.display = 'none';
        });

        saveSettingsBtn.addEventListener('click', () => {
            saveSettings();
            settingsModal.style.display = 'none';
        });

        // Model selection change - update system prompt
        document.getElementById('modelSelect').addEventListener('change', (e) => {
            const selectedModel = e.target.value;
            const systemPromptField = document.getElementById('systemInstructions');
            // Set the default system prompt for the selected model
            if (modelSystemPrompts[selectedModel]) {
                systemPromptField.value = modelSystemPrompts[selectedModel];
            }
        });

        // Theme toggle
        themeToggle.addEventListener('change', () => {
            localStorage.setItem('quickai_dark_mode', themeToggle.checked);
            applyTheme();
        });

        // Temperature slider
        temperatureSlider.addEventListener('input', () => {
            temperatureValue.textContent = temperatureSlider.value;
        });

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.style.display = 'none';
            }
        });

        // Render math in elements
        window.renderMathInElement = function(element) {
            if (window.katex && window.katex.renderMathInElement) {
                window.katex.renderMathInElement(element, {
                    delimiters: [
                        {left: '$$', right: '$$', display: true},
                        {left: '$', right: '$', display: false}
                    ],
                    throwOnError: false
                });
            }
        };
    }

    // Initialize the app
    init();
});