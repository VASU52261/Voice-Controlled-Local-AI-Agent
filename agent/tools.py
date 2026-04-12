import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_file(filename: str, content: str = "") -> dict:
    safe_path = os.path.join(OUTPUT_DIR, os.path.basename(filename))
    with open(safe_path, "w") as f:
        f.write(content)
    return {"status": "success", "path": safe_path, "message": f" Created {safe_path}"}

def write_code(filename: str, language: str, user_request: str) -> dict:
    prompt = f"Write {language} code for: {user_request}. Return ONLY the code, no explanation."
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    code = response.choices[0].message.content.strip()
    if code.startswith("```"):
        code = "\n".join(code.split("\n")[1:-1])
    result = create_file(filename, code)
    result["code"] = code
    return result

def summarize_text(content: str) -> dict:
    prompt = f"Summarize this concisely:\n\n{content}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    summary = response.choices[0].message.content.strip()
    return {"status": "success", "summary": summary, "message": " Text summarized"}

def general_chat(content: str, history: list = []) -> dict:
    messages = history + [{"role": "user", "content": content}]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    reply = response.choices[0].message.content.strip()
    return {"status": "success", "reply": reply, "message": " Chat response generated"}

def execute_intent(intent_data: dict, history: list = []) -> list:
    intents = intent_data.get("intents", ["general_chat"])
    results = []

    for intent in intents:
        if intent == "create_file":
            fname = intent_data.get("filename") or "new_file.txt"
            results.append({"intent": intent, **create_file(fname)})

        elif intent == "write_code":
            fname = intent_data.get("filename") or "output_code.py"
            lang = intent_data.get("language") or "python"
            req = intent_data.get("content") or intent_data.get("explanation", "")
            results.append({"intent": intent, **write_code(fname, lang, req)})

        elif intent == "summarize_text":
            content = intent_data.get("content", "")
            r = summarize_text(content)
            if intent_data.get("filename"):
                create_file(intent_data["filename"], r["summary"])
                r["message"] += f" and saved to {intent_data['filename']}"
            results.append({"intent": intent, **r})

        elif intent == "general_chat":
            content = intent_data.get("content", "")
            results.append({"intent": intent, **general_chat(content, history)})

    return results