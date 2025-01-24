from openai import OpenAI
from typing import Optional, List, Dict

class GPTResponseGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(
            api_key=api_key
        )
        if not api_key:
            raise ValueError("OpenAI API key is required")
    
    def generate_response(self, messages: List[Dict]) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"