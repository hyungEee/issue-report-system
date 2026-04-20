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

REGION_COUNTRY_MAP: dict[str, list[str]] = {
    "korea":              ["kr"],
    "north_america":      ["us"],
    "asia":               ["jp", "in", "tw"],
    "europe":             ["gb", "de", "fr", "ru"],
    "middle_east_africa": ["ae", "il"],
}

# 국가별 최대 수집 페이지 수 (미지정 국가는 기본 1페이지)
COUNTRY_MAX_PAGES: dict[str, int] = {
    "kr": 5,
    "us": 3,
}

# 카테고리별 최대 수집 페이지 수
CATEGORY_MAX_PAGES: dict[str, int] = {
    "world":         5,
    "nation":        5,
    "business":      5,
    "technology":    1,
    "science":       1,
    "entertainment": 1,
    "sports":        1,
}

# 국가 코드 → 언어 코드 (GNews API lang 파라미터용)
COUNTRY_LANG_MAP: dict[str, str] = {
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
