# Quick AI

A privacy-focused AI chat application powered by Pollinations AI with a clean, modern UI similar to ChatGPT.

## Features

### Privacy-Focused
- All chat data is stored locally in your browser's localStorage
- Your conversations are not logged externally

### Customizable Settings
- Choose from various AI models like OpenAI models, Llama, Mistral, and more
- Define system instructions to guide AI behavior
- Set desired max tokens and temperature

### Markdown and Rich Responses
- Supports Markdown for formatting
- LaTeX equations rendered via KaTeX
- Syntax-highlighted code blocks using Highlight.js

### Image Generation
- Enter `/image <prompt>` to generate images using Pollinations AI

### Commands
- `/clear` → This command clears the chat
- `/title` → This command regenerates the title
- `/image` → This command generates an image

### User-Friendly Interface
- Clean and intuitive UI with a red theme (toggleable to dark mode)
- Interactive dropdown menus for settings and model selection

### Dynamic Chat History
- Saves your chat context for continuity in conversations
- Edit, reset, or initialize a brand-new chat with ease

## Setup Instructions

### Prerequisites
- Python 3.6 or higher
- Flask

### Installation

1. Clone the repository or download the files

2. Install the required dependencies:
   ```
   pip install flask requests
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Privacy Notice

At Quick AI, your privacy is a priority:
- No external logging: Chat data is only stored locally and remains on your browser
- Data isolation: Communication with Pollinations AI models is secured and occurs in real time

IMPORTANT: While Quick AI ensures local privacy, the level of privacy in AI processing depends on Pollinations AI and the external models used to generate responses. Exercise caution when sharing sensitive information.