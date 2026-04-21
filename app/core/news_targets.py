SUPPORTED_CATEGORIES: list[str] = [
    "world",
    "nation",
    "business",
    "technology",
    "entertainment",
    "sports",
    "science",
]

# 카테고리 영문 → 한국어 표시명
CATEGORY_KO: dict[str, str] = {
    "world":         "국제정세",
    "nation":        "정치/사회",
    "business":      "비즈니스",
    "technology":    "기술",
    "entertainment": "엔터테인먼트",
    "sports":        "스포츠",
    "science":       "과학",
}

SUPPORTED_COUNTRIES: list[str] = ["kr", "us", "jp", "gb", "tw", "ru", "de", "il"]

COUNTRY_MAX_PAGES: dict[str, int] = {
    "kr": 5,
    "us": 3,
    "jp": 2,
    "gb": 1,
    "tw": 2,
    "ru": 1,
    "de": 1,
    "il": 1,
}

# 카테고리별 최대 수집 페이지 수
CATEGORY_MAX_PAGES: dict[str, int] = {
    "world":         1,
    "nation":        5,
    "business":      2,
    "technology":    1,
    "science":       1,
    "entertainment": 1,
    "sports":        1,
}

# 국가 코드 → 언어 코드 (GNews API lang 파라미터용)
COUNTRY_LANG_MAP: dict[str, str] = {
    "us": "en",
    "gb": "en",
    "kr": "ko",
    "jp": "ja",
    "tw": "zh",
    "ru": "ru",
    "de": "de",
    "il": "he",
}
