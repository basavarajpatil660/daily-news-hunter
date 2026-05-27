from datetime import datetime, timezone

def filter_by_age(articles, hours=24):
    now = datetime.now(timezone.utc)
    filtered = []
    for a in articles:
        if a.get('published_date'):
            diff = (now - a['published_date']).total_seconds() / 3600
            if diff <= hours:
                filtered.append(a)
    return filtered

def filter_by_score(articles, min_score=5):
    return [a for a in articles if a.get('final_score', 0) >= min_score]

def filter_clickbait(articles):
    return [a for a in articles if not a.get('clickbait', True)]
