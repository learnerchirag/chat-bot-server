import openai
from typing import Optional, List, Dict

class GPTResponseGenerator:
    def __init__(self, api_key: Optional[str] = None):
        openai.api_key = api_key
        if not openai.api_key:
            raise ValueError("OpenAI API key is required")
    
    def generate_response(self, messages: List[Dict]) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"