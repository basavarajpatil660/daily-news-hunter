from datetime import datetime, timezone

def format_time_ago(published_datetime):
    if not published_datetime:
        return "Unknown time"
    diff = datetime.now(timezone.utc) - published_datetime
    hours = int(diff.total_seconds() / 3600)
    if hours == 0:
        mins = int(diff.total_seconds() / 60)
        return f"{mins} mins ago"
    elif hours == 1:
        return "1 hour ago"
    return f"{hours} hours ago"

def format_score_badge(score):
    return f"{score:.1f}/11"

def get_category_color(category_name):
    from config.categories import CATEGORIES
    if category_name in CATEGORIES:
        return CATEGORIES[category_name]["color"]
    return "#4b5563"
