from utils.format import format_time_ago, get_category_color, format_relevance_label


def _escape(text):
    """Minimal HTML escaping for safe rendering in email."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate_html(articles, summary_stats):
    date_str = summary_stats.get("date", "")
    categories_str = ", ".join(summary_stats.get("categories", []))
    total_fetched = summary_stats.get("total_fetched", 0)
    total_scored = summary_stats.get("total_scored", 0)
    total_selected = len(articles)

    if not articles:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily News Report - {_escape(date_str)}</title>
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:#f4f4f2;margin:0;padding:24px 16px;color:#1a1a1a;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
    <tr><td align="center">
      <table width="100%" style="max-width:600px;" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td style="background:#1a1a2e;padding:28px 24px;text-align:center;border-radius:6px 6px 0 0;">
            <h1 style="margin:0;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:0;">Daily News Report</h1>
            <p style="margin:6px 0 0 0;font-size:12px;color:#8892b0;">{_escape(date_str)}</p>
          </td>
        </tr>
        <tr>
          <td style="background:#ffffff;padding:36px 24px;text-align:center;border-radius:0 0 6px 6px;">
            <p style="font-size:15px;color:#555;line-height:1.6;margin:0;">No qualifying articles were found today.</p>
            <p style="font-size:13px;color:#999;margin:10px 0 0 0;">The system will try again at the next scheduled run.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    # Build article cards
    cards_html = ""
    for idx, article in enumerate(articles):
        cat_color = get_category_color(article.get("category", ""))
        category = _escape(article.get("category", "General"))
        title = _escape(article.get("title", "Untitled"))
        source = _escape(article.get("source", "Unknown source"))
        time_ago = _escape(format_time_ago(article.get("published_date")))
        summary = _escape(article.get("gemma_summary", ""))
        importance = _escape(article.get("importance_reason", ""))
        link = article.get("link", "#")
        relevance_label = format_relevance_label(article.get("final_score", 0))
        separator = "" if idx == 0 else '<tr><td style="padding:0 24px;"><hr style="border:none;border-top:1px solid #eee;margin:0;"></td></tr>'

        # Badge HTML - only for Top Pick or Important
        badge_html = ""
        if relevance_label:
            badge_html = f' <span style="display:inline-block;font-size:9px;font-weight:700;color:#15803d;background:#dcfce7;padding:1px 6px;border-radius:8px;letter-spacing:0.3px;text-transform:uppercase;vertical-align:middle;">{_escape(relevance_label)}</span>'

        # Why it matters line - only if importance_reason exists
        importance_html = ""
        if importance:
            importance_html = f'<p style="margin:0 0 12px 0;font-size:12px;color:#8b5cf6;font-style:italic;line-height:1.4;">Why it matters: {importance}</p>'

        cards_html += f"""{separator}
        <tr>
          <td style="padding:20px 24px;">
            <p style="margin:0 0 6px 0;font-size:10px;color:#6b7280;letter-spacing:0.3px;">
              <span style="display:inline-block;font-size:9px;font-weight:700;color:#fff;background:{cat_color};padding:2px 7px;border-radius:8px;text-transform:uppercase;letter-spacing:0.5px;vertical-align:middle;">{category}</span>{badge_html}
              <span style="color:#bbb;margin:0 4px;">|</span>{source}<span style="color:#bbb;margin:0 4px;">|</span>{time_ago}
            </p>
            <h2 style="margin:0 0 8px 0;font-size:16px;font-weight:700;line-height:1.35;color:#111;">
              <a href="{_escape(link)}" style="color:#111;text-decoration:none;">{title}</a>
            </h2>
            <p style="margin:0 0 8px 0;font-size:14px;color:#374151;line-height:1.55;">{summary}</p>
            {importance_html}
            <a href="{_escape(link)}" style="font-size:13px;color:#2563eb;text-decoration:none;font-weight:600;">Read full article &rarr;</a>
          </td>
        </tr>"""

    # Full document
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily News Report - {_escape(date_str)}</title>
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:#f4f4f2;margin:0;padding:24px 16px;color:#1a1a1a;-webkit-text-size-adjust:100%;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
    <tr><td align="center">
      <table width="100%" style="max-width:600px;" cellpadding="0" cellspacing="0" border="0" role="presentation">

        <!-- Header -->
        <tr>
          <td style="background:#1a1a2e;padding:28px 24px 22px 24px;text-align:center;border-radius:6px 6px 0 0;">
            <h1 style="margin:0 0 4px 0;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:0;">Daily News Report</h1>
            <p style="margin:0;font-size:12px;color:#8892b0;">{_escape(date_str)} - {_escape(categories_str)}</p>
          </td>
        </tr>

        <!-- Subtle stats line -->
        <tr>
          <td style="background:#ffffff;padding:14px 24px 10px 24px;border-bottom:1px solid #f0f0f0;">
            <p style="margin:0;font-size:11px;color:#9ca3af;text-align:center;">{total_fetched} scanned &middot; {total_scored} scored &middot; {total_selected} selected</p>
          </td>
        </tr>

        <!-- Articles -->
        {cards_html}

        <!-- Footer -->
        <tr>
          <td style="background:#fafafa;padding:18px 24px;text-align:center;border-top:1px solid #eee;border-radius:0 0 6px 6px;">
            <p style="margin:0;font-size:11px;color:#aaa;">Daily News Hunter &middot; Powered by Gemma 4</p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""
