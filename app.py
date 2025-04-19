from flask import Flask, render_template, request, jsonify
import json
import requests
import os

app = Flask(__name__)

# Pollinations API endpoints
POLLINATIONS_IMAGE_API = "https://image.pollinations.ai/prompt/{}"
POLLINATIONS_TEXT_API = "https://text.pollinations.ai/{}"
POLLINATIONS_TEXT_POST_API = "https://text.pollinations.ai/"
POLLINATIONS_OPENAI_COMPATIBLE_API = "https://text.pollinations.ai/openai"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-text', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data.get('prompt')
    model = data.get('model', 'openai/gpt-3.5-turbo')
    
    # For simple requests
    if data.get('simple', False):
        response = requests.get(f"{POLLINATIONS_TEXT_API}{prompt}")
        return jsonify(response.json())
    
    # For advanced requests
    payload = {
        "prompt": prompt,
        "model": model,
        "max_tokens": data.get('max_tokens', 1000),
        "temperature": data.get('temperature', 0.7),
        "system_instructions": data.get('system_instructions', '')
    }
    
    response = requests.post(POLLINATIONS_TEXT_POST_API, json=payload)
    return jsonify(response.json())

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt')
    
    # Encode the prompt for URL
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    
    image_url = f"{POLLINATIONS_IMAGE_API}{encoded_prompt}"
    return jsonify({"image_url": image_url})

@app.route('/api/list-models', methods=['GET'])
def list_models():
    model_type = request.args.get('type', 'text')
    
    if model_type == 'text':
        response = requests.get("https://text.pollinations.ai/models")
    else:
        response = requests.get("https://image.pollinations.ai/models")
        
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
