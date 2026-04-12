class SessionMemory:
    def __init__(self):
        self.history = []
        self.action_log = []

    def add_turn(self, user_text, intent_data, results):
        # Add to LLM chat history
        self.history.append({"role": "user", "content": user_text})
        for r in results:
            reply = r.get("reply") or r.get("summary") or r.get("message", "")
            self.history.append({"role": "assistant", "content": reply})

        # Add to UI action log
        self.action_log.append({
            "transcription": user_text,
            "intents": intent_data.get("intents", []),
            "explanation": intent_data.get("explanation", ""),
            "results": results
        })

    def get_log_display(self):
        if not self.action_log:
            return "_No history yet_"
        lines = []
        for i, turn in enumerate(self.action_log, 1):
            intents = ", ".join(turn["intents"])
            lines.append(f"**Turn {i}** | Intents: `{intents}`")
            lines.append(f">  {turn['transcription']}")
            lines.append(f">  {turn['explanation']}")
            lines.append("---")
        return "\n\n".join(lines)