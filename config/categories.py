CATEGORIES = {
    "AI News": {
        "keywords": ["artificial intelligence", "ChatGPT", "OpenAI", "Google Gemini", "AI model", "Anthropic Claude", "large language model", "AI research"],
        "color": "#7c3aed",
        "feeds": []
    },
    "Tech News": {
        "keywords": ["technology news", "software update", "Apple", "Google", "Microsoft", "Meta", "developer tools", "programming"],
        "color": "#2563eb",
        "feeds": [
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://www.wired.com/feed/rss",
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://venturebeat.com/feed/",
            "https://www.technologyreview.com/feed/",
            "http://feeds.bbci.co.uk/news/technology/rss.xml",
            "https://economictimes.indiatimes.com/tech/rss.cms",
            "https://www.indiatoday.in/rss/1206578",
            "https://www.hindustantimes.com/feeds/rss/technology/rssfeed.xml"
        ]
    },
    "AI App Building": {
        "keywords": ["AI app development", "build with AI", "AI agent", "LLM development", "no code AI", "AI automation"],
        "color": "#4338ca",
        "feeds": []
    },
    "Cybersecurity": {
        "keywords": ["cybersecurity", "data breach", "hacking", "security vulnerability", "ransomware", "privacy"],
        "color": "#dc2626",
        "feeds": []
    },
    "Startup and Entrepreneur": {
        "keywords": ["startup funding", "venture capital", "new startup", "founder", "startup India"],
        "color": "#ea580c",
        "feeds": []
    },
    "Science and Research": {
        "keywords": ["science discovery", "research breakthrough", "NASA", "ISRO", "scientific study"],
        "color": "#16a34a",
        "feeds": [
            "https://www.thehindu.com/sci-tech/feeder/default.rss"
        ]
    },
    "Space and Astronomy": {
        "keywords": ["space news", "NASA mission", "ISRO", "satellite launch", "space exploration"],
        "color": "#1e3a5f",
        "feeds": []
    },
    "Finance and Economy": {
        "keywords": ["economy India", "RBI", "financial news", "stock market India", "budget India", "inflation"],
        "color": "#ca8a04",
        "feeds": []
    },
    "Health and Medical Tech": {
        "keywords": ["health technology", "medical AI", "healthcare news", "biotech", "pharma"],
        "color": "#0d9488",
        "feeds": []
    },
    "Custom": {
        "keywords": [],
        "color": "#4b5563",
        "feeds": []
    }
}

# Regional mappings for Google News RSS
REGION_MAP = {
    "IN": {"hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
    "US": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
    "Global": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
}

# Language mappings for Google News RSS
LANGUAGE_MAP = {
    "en": {"hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
    "hi": {"hl": "hi-IN", "gl": "IN", "ceid": "IN:hi"},
}

import urllib.parse

def get_google_news_rss(keyword, region="IN", language="en"):
    """
    Construct Google News RSS URL for a specific keyword based on region and language preferences.
    """
    # Normalize inputs
    region_key = "IN" if region == "India only" or region == "IN" else ("US" if region == "USA only" or region == "US" else "Global")
    lang_key = "hi" if language == "hi" or "hindi" in language.lower() else "en"
    
    if lang_key == "hi":
        params = LANGUAGE_MAP["hi"]
    else:
        params = REGION_MAP.get(region_key, REGION_MAP["Global"])
        
    keyword_encoded = urllib.parse.quote(keyword)
    return f"https://news.google.com/rss/search?q={keyword_encoded}&hl={params['hl']}&gl={params['gl']}&ceid={params['ceid']}"

def get_google_news_rss_hindi(keyword):
    """
    Explicit helper for Hindi Google News feed.
    """
    keyword_encoded = urllib.parse.quote(keyword)
    return f"https://news.google.com/rss/search?q={keyword_encoded}&hl=hi-IN&gl=IN&ceid=IN:hi"

