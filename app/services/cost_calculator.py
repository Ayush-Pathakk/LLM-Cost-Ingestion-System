from app.services.pricing_table import get_price_per_million

def calculate_cost(provider: str, model: str, tokens_used: int) -> float:
    price_per_million = get_price_per_million(provider, model)
    return round((tokens_used / 1_000_000) * price_per_million, 6)