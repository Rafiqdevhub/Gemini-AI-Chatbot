import os
import time
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress
import requests
import json
from typing import List, Dict, Optional

load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in your .env file")

# Constants
MAX_TOKENS = 30720  # Maximum context length for Gemini Pro
RATE_LIMIT_DELAY = 1  # Delay between requests in seconds
MAX_RETRIES = 3
MODEL_NAME = "gemini-2.0-flash"  # Standard Gemini Pro model

# Initialize Rich console for better formatting
console = Console()

class Conversation:
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        
    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "text": content})
        
    def get_messages(self) -> List[Dict[str, str]]:
        return self.history
        
    def clear(self):
        self.history = []

def create_message_content(conversation: Conversation, new_message: str) -> dict:
    """Create the message content with conversation history"""
    contents = []
    
    # Add conversation history
    for msg in conversation.get_messages():
        role = msg['role']
        text = msg['text']
        contents.append({
            "role": role,
            "parts": [{"text": text}]
        })
    
    # Add new message with user role
    contents.append({
        "role": "user",
        "parts": [{"text": new_message}]
    })
    
    return {"contents": contents}

def get_response(prompt: str, conversation: Conversation, stream: bool = False) -> str:
    """Get response from Gemini API using direct REST endpoint with streaming support"""
    try:
        # Use the configured model name in the URL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key as a query parameter
        params = {
            "key": API_KEY
        }
        
        data = create_message_content(conversation, prompt)
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(url, headers=headers, params=params, json=data)
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Check for safety ratings
                    if 'promptFeedback' in response_data:
                        if response_data['promptFeedback'].get('blockReason'):
                            return "I apologize, but I cannot respond to that prompt due to safety concerns."
                    
                    if 'candidates' in response_data and len(response_data['candidates']) > 0:
                        content = response_data['candidates'][0]['content']
                        if 'parts' in content and len(content['parts']) > 0:
                            response_text = content['parts'][0]['text']
                            conversation.add_message("user", prompt)
                            conversation.add_message("model", response_text) 
                            return response_text
                    return "No response generated"
                elif response.status_code == 404:
                    return f"Error: Model '{MODEL_NAME}' not found or not available. Please check the model name."
                elif response.status_code == 429:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RATE_LIMIT_DELAY * (attempt + 1))
                        continue
                    return "Rate limit exceeded. Please try again later."
                else:
                    return f"Error: API returned status code {response.status_code}. Response: {response.text}"
                    
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RATE_LIMIT_DELAY)
                    continue
                return f"Network error: {str(e)}"
                
    except Exception as e:
        error_message = str(e)
        if "API key" in error_message:
            return "Error: Please make sure you have set up your GOOGLE_API_KEY in the .env file"
        else:
            return f"An error occurred: {error_message}"
    
    return "An unexpected error occurred"  # Fallback return for all code paths

def format_response(response: str) -> str:
    """Format the response with proper markdown rendering"""
    try:
        if isinstance(response, Markdown):
            # If it's already a Markdown object, convert it to string
            return str(response)
        elif isinstance(response, str) and ("```" in response or "#" in response or "*" in response):
            # If it's a string with markdown symbols, format and print it directly
            md = Markdown(response)
            console.print(md)
            return response
        return str(response)  # Ensure we always return a string
    except Exception as e:
        console.print(f"[red]Warning: Error formatting response: {str(e)}[/red]")
        return str(response)

def print_welcome_message():
    """Print a formatted welcome message"""
    console.print("\n[bold cyan]Welcome to Enhanced Gemini Chatbot![/bold cyan]")
    console.print(f"[cyan]Using model: {MODEL_NAME}[/cyan]")
    console.print("[cyan]Available commands:[/cyan]")
    console.print("[cyan]- 'quit' or 'exit': End conversation[/cyan]")
    console.print("[cyan]- 'clear': Clear conversation history[/cyan]")
    console.print("-" * 50)

def main():
    print_welcome_message()
    conversation = Conversation()
    
    while True:
        try:
            console.print("\n[bold green]You:[/bold green] ", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit']:
                console.print("\n[bold cyan]Goodbye![/bold cyan]")
                break
                
            if user_input.lower() == 'clear':
                conversation.clear()
                console.print("[cyan]Conversation history cleared.[/cyan]")
                continue
            
            # Check input length
            if len(user_input) > MAX_TOKENS:
                console.print("[red]Input too long. Please reduce the length of your message.[/red]")
                continue
                
            console.print("\n[bold blue]Chatbot:[/bold blue]")
            with Progress() as progress:
                task = progress.add_task("[cyan]Thinking...[/cyan]", total=None)
                response = get_response(user_input, conversation)
                progress.remove_task(task)
            
            if response:
                formatted_response = format_response(response)
                if formatted_response:
                    console.print(formatted_response)
                else:
                    console.print("[red]Error: Empty response after formatting[/red]")
            else:
                console.print("[red]Error: Empty response from model[/red]")
                
        except KeyboardInterrupt:
            console.print("\n[bold cyan]Goodbye![/bold cyan]")
            break
        except Exception as e:
            console.print(f"\n[red]An unexpected error occurred: {str(e)}[/red]")

if __name__ == "__main__":
    main()