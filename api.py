import google.generativeai as genai
from langchain.llms.base import LLM
from langchain.schema import LLMResult

DEFAULT_MODEL = "models/gemini-1.5-flash"

gemini_model = None

def setup_gemini_api(api_key):
    global gemini_model
    print("🔑 Configuring Gemini API with provided API key...")
    genai.configure(api_key=api_key)
    gemini_model = GeminiLLM()
    print(f"✅ Gemini API configured. Using model: {DEFAULT_MODEL}")

class GeminiLLM(LLM):
    @property
    def _llm_type(self):
        return "gemini-1.5-flash"

    def _call(self, prompt: str, stop=None) -> str:
        print(f"📝 Sending prompt to Gemini model ({DEFAULT_MODEL})...")
        response = genai.generate_text(model=DEFAULT_MODEL, prompt=prompt)
        print("✅ Received response from Gemini model.")
        return response.text

    def generate(self, prompts, stop=None):
        texts = []
        for prompt in prompts:
            texts.append(self._call(prompt, stop=stop))
        return LLMResult(generations=[[{"text": t}] for t in texts])
