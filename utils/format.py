from datetime import datetime, timezone


def format_time_ago(published_datetime):
    if not published_datetime:
        return "Unknown time"
    diff = datetime.now(timezone.utc) - published_datetime
    hours = int(diff.total_seconds() / 3600)
    if hours == 0:
        mins = int(diff.total_seconds() / 60)
        return f"{mins}m ago"
    elif hours == 1:
        return "1 hr ago"
    return f"{hours} hrs ago"


def format_relevance_label(score):
    """Return a small human-readable relevance label, or empty string."""
    if score is None:
        return ""
    if score >= 9.5:
        return "Important"
    return ""


def get_category_color(category_name):
    from config.categories import CATEGORIES
    if category_name in CATEGORIES:
        return CATEGORIES[category_name]["color"]
    return "#4b5563"
