import json
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from api import setup_gemini_api, gemini_model  # your existing Gemini API setup

# Prompt template for revision focusing on readability and style suggestions
revision_template = """
You are an expert technical writer tasked with revising a documentation article.

Original Article Content:
\"\"\"{content}\"\"\"

Based on these suggestions, improve the article to enhance readability and style.

Readability Suggestions:
{readability_suggestions}

Style Suggestions:
{style_suggestions}

Do not change the factual content or structure. Focus on making the text clearer, more readable, and consistent with style guidelines.

Please provide the full revised article text only, without additional commentary.
"""

def revise_document(original_content, suggestions):
    readability_suggestions = suggestions.get("readability", {}).get("suggestions", "No specific readability suggestions provided.")
    style_suggestions = suggestions.get("style", {}).get("suggestions", "No specific style suggestions provided.")

    prompt = PromptTemplate(
        input_variables=["content", "readability_suggestions", "style_suggestions"],
        template=revision_template
    )

    chain = LLMChain(llm=gemini_model, prompt=prompt)
    revised_content = chain.run(
        content=original_content,
        readability_suggestions=readability_suggestions,
        style_suggestions=style_suggestions
    )

    return revised_content

def main():
    print("🚀 Starting Documentation Revision Agent...")
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables.")
        return

    setup_gemini_api(api_key)
    print("✅ Gemini API initialized.\n")

    try:
        # Load analyzed articles with suggestions from your first agent
        with open("revised.json", "r", encoding="utf-8") as f:
            analyzed_articles = json.load(f)

        revised_results = []
        for idx, article_data in enumerate(analyzed_articles):
            print(f"\n➡️ Revising article {idx + 1}: {article_data.get('Title', 'Untitled')}")

            original_content = article_data.get("content", "")
            if not original_content.strip():
                print("⚠️ No content found. Skipping...")
                continue

            # Revise article content using suggestions
            revised_text = revise_document(original_content, article_data)

            # Save revised content along with metadata
            revised_results.append({
                "URL": article_data.get("URL"),
                "Title": article_data.get("Title"),
                "OriginalContent": original_content,
                "RevisedContent": revised_text,
                "Suggestions": {
                    "Readability": article_data.get("readability"),
                    "Style": article_data.get("style"),
                    "Structure": article_data.get("structure"),
                    "Completeness": article_data.get("completeness")
                }
            })

        # Save all revised articles to JSON
        with open("revised_articles_with_edits.json", "w", encoding="utf-8") as f_out:
            json.dump(revised_results, f_out, indent=2, ensure_ascii=False)

        print("\n✅ Revision process completed successfully. Output saved to revised_articles_with_edits.json")

    except Exception as e:
        print(f"❌ Error during revision process: {e}")

if __name__ == "__main__":
    main()
