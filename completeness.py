# completeness_helper.py

def analyze_completeness(text: str) -> dict:
    try:
        keyword_count = sum([text.lower().count(k) for k in ["example", "e.g.", "step", "demo"]])
        has_examples = keyword_count > 1

        return {
            "examples_found": keyword_count,
            "assessment": "Contains examples." if has_examples else "Lacks sufficient examples.",
            "suggestion": "Add step-by-step examples or case uses where appropriate."
        }
    except Exception as e:
        return {"error": str(e)}
