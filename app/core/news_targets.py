SUPPORTED_CATEGORIES = [
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
    "kr": 3,
    "us": 3,
}

CATEGORY_MAX_PAGES: dict[str, int] = {
    "world":         3,
    "nation":        3,
    "business":      3,
    "technology":    1,
    "science":       1,
    "entertainment": 1,
    "sports":        1,
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
