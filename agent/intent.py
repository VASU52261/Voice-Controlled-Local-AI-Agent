import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an intent classifier for a voice-controlled AI agent.
Analyze the user's text and return a JSON object.

Rules for choosing intent:
- If the user says "write", "create", "make", "generate", "give me a file", "save to file", "code for", "program for", "script for" -> use write_code
- If the user says "create a folder", "create an empty file", "make a file called" (with no code request) -> use create_file
- If the user says "summarize", "summary of", "shorten this" -> use summarize_text
- Everything else -> use general_chat

For write_code, always pick a suitable filename if the user did not mention one.
For language, detect from context. Default to "python" if not mentioned.
For content, copy the user's full request so the code generator knows what to build.

Return exactly this JSON format and nothing else:
{
  "intents": ["write_code"],
  "filename": "hello.py",
  "language": "python",
  "content": "full description of what code to write",
  "explanation": "one sentence describing what you will do"
}

Supported intents: create_file, write_code, summarize_text, general_chat
IMPORTANT: Return ONLY valid JSON. No markdown, no backticks, no extra text.
"""

def classify_intent(text: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.1
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "intents": ["general_chat"],
            "content": text,
            "explanation": "Could not parse intent, defaulting to chat"
        }
