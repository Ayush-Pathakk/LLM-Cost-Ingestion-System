import tiktoken
from openai import OpenAI
import google.generativeai as genai
from app.config import settings

def estimate_tokens_openai(prompt: str, model: str) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(prompt))

def call_openai(prompt: str, model: str) -> tuple[str, int]:
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content
    tokens_used = response.usage.total_tokens
    return text, tokens_used

def call_gemini(prompt: str, model: str) -> tuple[str, int]:
    genai.configure(api_key=settings.gemini_api_key)
    gen_model = genai.GenerativeModel(model)
    response = gen_model.generate_content(prompt)
    text = response.text
    tokens_used = response.usage_metadata.total_token_count
    return text, tokens_used

def call_llm(provider: str, model: str, prompt: str) -> tuple[str, int]:
    if provider.lower() == "openai":
        return call_openai(prompt, model)
    elif provider.lower() == "gemini":
        return call_gemini(prompt, model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")