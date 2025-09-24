import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version = '2024-12-01-preview',
  azure_endpoint = 'https://aia-chat.openai.azure.com/'
)
CHAT_MODEL = "gpt-4o-mini"

def chat(messages):
    try:
        result = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0
        )
        return result.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
    
def chat_structured(messages):
    try:
        result = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(result.choices[0].message.content)
    except Exception as e:
        return f"Error: {str(e)}"
    