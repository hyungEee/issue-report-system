SUPPORTED_CATEGORIES = [
    "general",
    "world",
    "nation",
    "business",
    "technology",
    "entertainment",
    "sports",
    "science",
    "health",
]

REGION_COUNTRY_MAP: dict[str, list[str]] = {
    "korea":              ["KR"],
    "north_america":      ["US"],
    "asia":               ["JP", "IN", "TW"],
    "europe":             ["GB", "DE", "FR", "RU"],
    "middle_east_africa": ["AE", "IL"],
}

COUNTRY_MAX_PAGES: dict[str, int] = {
    # Tier 1 — 2페이지 수집으로 최대 200개 확보
    "kr": 2,
    "us": 2,
}

COUNTRY_LANG_MAP = {
    "us": "en",
    "gb": "en",
    "de": "de",
    "fr": "fr",
    "ae": "ar",
    "il": "he",
    "kr": "ko",
    "jp": "ja",
    "in": "en",
    "tw": "zh",
    "ru": "ru",
}
