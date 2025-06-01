# readability_helper.py
import textstat

def analyze_readability(text: str) -> dict:
    try:
        fk_score = textstat.flesch_kincaid_grade(text)
        fog_index = textstat.gunning_fog(text)
        comment = "Good for marketers." if fk_score < 9 else "Too complex for a non-technical marketer."

        return {
            "score": {
                "flesch_kincaid": fk_score,
                "gunning_fog": fog_index
            },
            "assessment": comment,
            "suggestion": "Simplify long/technical sentences, especially those above grade 9."
        }
    except Exception as e:
        return {"error": str(e)}
