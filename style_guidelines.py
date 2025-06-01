# style_helper.py

def analyze_style(text: str) -> dict:
    try:
        passive_phrases = ["is being", "was done", "are made"]
        passive_count = sum([text.lower().count(p) for p in passive_phrases])
        action_words = ["click", "select", "go to", "enter", "choose"]
        action_count = sum([text.lower().count(a) for a in action_words])

        voice_tone = "Too passive." if passive_count > 3 else "Mostly active voice."
        action_tone = "Good use of action-oriented language." if action_count > 3 else "Lacks strong action guidance."

        return {
            "passive_phrases": passive_count,
            "action_verbs": action_count,
            "assessment": f"{voice_tone} {action_tone}",
            "suggestion": "Use active voice. Start sentences with user actions like 'Click' or 'Enter'."
        }
    except Exception as e:
        return {"error": str(e)}
