CATEGORIES = {
    "AI News": {
        "keywords": ["artificial intelligence", "ChatGPT", "OpenAI", "Google Gemini", "AI model", "Anthropic Claude", "large language model", "AI research"],
        "color": "#7c3aed"
    },
    "Tech News": {
        "keywords": ["technology news", "software update", "Apple", "Google", "Microsoft", "Meta", "developer tools", "programming"],
        "color": "#2563eb"
    },
    "AI App Building": {
        "keywords": ["AI app development", "build with AI", "AI agent", "LLM development", "no code AI", "AI automation"],
        "color": "#4338ca"
    },
    "Cybersecurity": {
        "keywords": ["cybersecurity", "data breach", "hacking", "security vulnerability", "ransomware", "privacy"],
        "color": "#dc2626"
    },
    "Startup and Entrepreneur": {
        "keywords": ["startup funding", "venture capital", "new startup", "founder", "startup India"],
        "color": "#ea580c"
    },
    "Science and Research": {
        "keywords": ["science discovery", "research breakthrough", "NASA", "ISRO", "scientific study"],
        "color": "#16a34a"
    },
    "Space and Astronomy": {
        "keywords": ["space news", "NASA mission", "ISRO", "satellite launch", "space exploration"],
        "color": "#1e3a5f"
    },
    "Finance and Economy": {
        "keywords": ["economy India", "RBI", "financial news", "stock market India", "budget India", "inflation"],
        "color": "#ca8a04"
    },
    "Health and Medical Tech": {
        "keywords": ["health technology", "medical AI", "healthcare news", "biotech", "pharma"],
        "color": "#0d9488"
    },
    "Custom": {
        "keywords": [],
        "color": "#4b5563"
    }
}

RELIABLE_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://venturebeat.com/feed/",
    "https://www.technologyreview.com/feed/",
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.reuters.com/reuters/technologyNews",
    "https://feeds.feedburner.com/NdtvNews-Tech",
    "https://economictimes.indiatimes.com/tech/rss.cms",
    "https://www.thehindu.com/sci-tech/feeder/default.rss",
    "https://www.indiatoday.in/rss/1206578",
    "https://www.hindustantimes.com/feeds/rss/technology/rssfeed.xml"
]

def get_google_news_rss(keyword, region="Global worldwide", language="English only"):
    hl = "en-IN"
    gl = "IN"
    ceid = "IN:en"
    
    if region == "Global worldwide":
        hl = "en-US"
        gl = "US"
        ceid = "US:en"
    elif region == "USA only":
        hl = "en-US"
        gl = "US"
        ceid = "US:en"
    
    return f"https://news.google.com/rss/search?q={keyword}&hl={hl}&gl={gl}&ceid={ceid}"

def get_google_news_rss_hindi(keyword):
    return f"https://news.google.com/rss/search?q={keyword}&hl=hi-IN&gl=IN&ceid=IN:hi"
