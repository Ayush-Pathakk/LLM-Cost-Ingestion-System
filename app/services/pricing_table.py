# Price per 1M tokens, in USD. Hardcoded for MVP — swap for a real sync job later.
PRICING = {
    "openai": {
        "gpt-4o": 5.00,
        "gpt-4o-mini": 0.15,
        "gpt-3.5-turbo": 0.50,
    },
    "gemini": {
        "gemini-1.5-pro": 3.50,
        "gemini-1.5-flash": 0.075,
    },
}

DEFAULT_PRICE_PER_MILLION = 1.00  # fallback if model isn't in the table

def get_price_per_million(provider: str, model: str) -> float:
    provider_table = PRICING.get(provider.lower(), {})
    return provider_table.get(model.lower(), DEFAULT_PRICE_PER_MILLION)