# structure_helper.py

def analyze_structure(text: str) -> dict:
    try:
        headings = text.count('\n#') + text.count('\n##')
        bullets = text.count('- ') + text.count('* ')
        long_paragraphs = sum([1 for p in text.split('\n\n') if len(p.split()) > 100])

        return {
            "headings": headings,
            "bullet_points": bullets,
            "long_paragraphs": long_paragraphs,
            "assessment": "Logical structure but may need better scannability." if long_paragraphs > 2 else "Good structure.",
            "suggestion": "Use more headings or break up long paragraphs into smaller chunks."
        }
    except Exception as e:
        return {"error": str(e)}
