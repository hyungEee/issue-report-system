SUPPORTED_CATEGORIES = [
    "general",
    "world",
    "nation",
    "business",
    "technology",
    "entertainment",
    "sports",
    "science",
]

REGION_COUNTRY_MAP: dict[str, list[str]] = {
    "korea":              ["kr"],
    "north_america":      ["us"],
    "asia":               ["jp", "in", "tw"],
    "europe":             ["gb", "de", "fr", "ru"],
    "middle_east_africa": ["ae", "il"],
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

CATEGORY_WEIGHT: dict[str, float] = {
    "general":       1.0,
    "world":         1.0,
    "nation":        1.0,
    "business":      0.9,
    "technology":    0.3,
    "science":       0.3,
    "entertainment": 0.2,
    "sports":        0.2,
}
