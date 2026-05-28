CREDIBLE_SOURCES = [
    "TechCrunch", "The Verge", "Wired", "Ars Technica",
    "MIT Technology Review", "BBC", "Reuters", "AP News",
    "The Hindu", "Times of India", "Economic Times",
    "NDTV", "India Today", "Hindustan Times", "Bloomberg",
    "Forbes", "VentureBeat", "ZDNet", "CNET", "Engadget"
]

BOOST_KEYWORDS = [
    "ai regulation", "cybersecurity breach", "funding round",
    "acquisition", "developer tools", "api release",
    "open source", "platform change", "research paper",
    "government policy", "data privacy law"
]

PENALTY_KEYWORDS = [
    "deals", "rumors", "fitbit", "ui change", "complaint",
    "review", "unboxing", "comparison", "best of list",
    "top 10", "how to", "tips and tricks"
]

def get_source_adjustment(source_name):
    """
    Returns +1 for known credible sources, -1 for unknown sources.
    """
    if not source_name:
        return -1
    source_lower = source_name.lower()
    for s in CREDIBLE_SOURCES:
        if s.lower() in source_lower:
            return 1
    return -1

def calculate_final_score(gemma_score, source):
    """
    Adjusts Gemma score based on source credibility.
    """
    adj = get_source_adjustment(source)
    return gemma_score + adj

def pre_rank_article(article):
    """
    Pre-ranks article based on source credibility and keyword relevance (without AI).
    Boosts: +2 for each boost keyword match.
    Penalties: -2 for each penalty keyword match.
    """
    # Start with credibility score adjustment
    score = get_source_adjustment(article.get("source", ""))
    
    title = (article.get("title") or "").lower()
    desc = (article.get("description") or "").lower()
    text = f"{title} {desc}"
    
    # Add +2 for each boost keyword match
    for kw in BOOST_KEYWORDS:
        if kw in text:
            score += 2
            
    # Subtract 2 for each penalty keyword match
    for kw in PENALTY_KEYWORDS:
        if kw in text:
            score -= 2
            
    return score

