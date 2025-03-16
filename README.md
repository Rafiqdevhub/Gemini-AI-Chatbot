# Enhanced Gemini Chatbot

A powerful command-line chatbot interface built with Google's Gemini Pro API, featuring conversation history, markdown rendering, and error handling.

## Features

- 🤖 Powered by Google's Gemini Pro API
- 💬 Maintains conversation history
- 🎨 Rich text formatting with markdown support
- ⚡ Efficient error handling and rate limiting
- 🔄 Automatic retries for failed requests
- 🛡️ Content safety checks
- 📝 Clear and intuitive command interface

## Prerequisites

- Python 3.8 or higher
- Google API Key for Gemini Pro

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Rafiqdevhub/Gemini-AI-Chatbot.git
cd Gemini-AI-Chatbot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your Google API key:
```
GOOGLE_API_KEY="your-api-key-here"
```

## Usage

Run the chatbot:
```bash
python main.py
```

### Available Commands:
- Type your message and press Enter to chat
- Type 'clear' to reset conversation history
- Type 'quit' or 'exit' to end the session

## Technical Details

- Maximum token context length: 30720
- Rate limit delay: 1 second
- Maximum retries: 3
- Model: gemini-2.0-flash

## Error Handling

The chatbot handles various scenarios including:
- Network errors
- API rate limiting
- Content safety blocks
- Invalid responses
- Input length validation

## Dependencies

- rich: For console formatting and markdown rendering
- python-dotenv: For environment variable management
- requests: For API communication

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.