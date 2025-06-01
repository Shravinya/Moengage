import pandas as pd
import os
import json
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from api import setup_gemini_api, gemini_model
from readability import analyze_readability
from structure import analyze_structure
from completeness import analyze_completeness
from style_guidelines import analyze_style

template = """
You are a document analysis assistant.

Based on these example analyses, answer the questions for the new article.

Readability Example:
{readability}

Structure Example:
{structure}

Completeness Example:
{completeness}

Style Example:
{style}

---

Article Content:
\"\"\"{content}\"\"\"

Please provide a JSON with keys readability, structure, completeness, and style, each containing assessment and suggestions.
"""

def analyze_document_with_llm(article):
    print("🔄 Starting LLM analysis for article content...")
    examples = {
        "readability": analyze_readability(article["content"]),
        "structure": analyze_structure(article["content"]),
        "completeness": analyze_completeness(article["content"]),
        "style": analyze_style(article["content"])
    }

    prompt = PromptTemplate(
        input_variables=["readability", "structure", "completeness", "style", "content"],
        template=template
    )

    chain = LLMChain(llm=gemini_model, prompt=prompt)
    print("🤖 Running prompt through Gemini LLMChain...")
    response = chain.run(
        readability=json.dumps(examples["readability"], indent=2),
        structure=json.dumps(examples["structure"], indent=2),
        completeness=json.dumps(examples["completeness"], indent=2),
        style=json.dumps(examples["style"], indent=2),
        content=article["content"]
    )
    print("✅ LLMChain run completed.")

    try:
        parsed = json.loads(response)
        print("✅ Successfully parsed LLM JSON response.")
        return parsed
    except json.JSONDecodeError:
        print("⚠️ Failed to parse LLM JSON response; returning raw response.")
        return {"llm_response": response}

def analyze_document(article):
    print(f"\n🔍 Analyzing: {article['title']} ({article['url']})\n")
    try:
        result = analyze_document_with_llm(article)
    except Exception as e:
        print(f"⚠️ LLM analysis failed: {e}. Falling back to local analysis.")
        result = {
            "readability": analyze_readability(article["content"]),
            "structure": analyze_structure(article["content"]),
            "completeness": analyze_completeness(article["content"]),
            "style": analyze_style(article["content"]),
        }

    full_result = {
        "URL": article["url"],
        "Title": article["title"],
        **result
    }

    print("✅ Analysis Complete:")
    for k, v in full_result.items():
        print(f"\n--- {k} ---")
        print(v)

    return full_result

def main():
    print("🚀 Starting analysis with LangChain + Gemini 1.5 Flash model...")
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables.")
        return
    print("🔑 GEMINI_API_KEY loaded successfully.")

    setup_gemini_api(api_key)
    print("✅ Gemini API initialized.\n")

    try:
        df = pd.read_csv("filtered_article_links_content.csv")
        print(f"📄 Loaded {len(df)} articles from CSV.")
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        print("📋 Normalized CSV columns:", df.columns.tolist())

        results = []
        for idx, row in df.head(2).iterrows():
            article = {
                "title": row.get("title", ""),
                "url": row.get("url", ""),
                "content": row.get("body_text", "")
            }
            print(f"\n➡️ Processing article {idx + 1}: {article['title']}")
            result = analyze_document(article)
            results.append(result)

        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("\n✅ Results saved to result.json")

    except Exception as e:
        print(f"❌ Error during pipeline: {e}")

if __name__ == "__main__":
    main()
