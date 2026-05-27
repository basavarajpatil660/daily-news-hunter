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
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:#f5f5f0;margin:0;padding:24px 16px;color:#1a1a1a;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
    <tr><td align="center">
      <table width="100%" style="max-width:620px;" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td style="background:#1a1a2e;padding:32px 28px;text-align:center;border-radius:8px 8px 0 0;">
            <p style="margin:0;font-size:11px;letter-spacing:2px;color:#8892b0;text-transform:uppercase;">Daily News Hunter</p>
            <h1 style="margin:8px 0 4px 0;font-size:26px;font-weight:700;color:#ffffff;letter-spacing:0;">Daily News Report</h1>
            <p style="margin:0;font-size:13px;color:#8892b0;">{_escape(date_str)}</p>
          </td>
        </tr>
        <tr>
          <td style="background:#ffffff;padding:40px 28px;text-align:center;border-radius:0 0 8px 8px;">
            <p style="font-size:16px;color:#555;line-height:1.6;">No qualifying articles were found today for your chosen categories.</p>
            <p style="font-size:14px;color:#888;">The system will try again at the next scheduled run automatically.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    cards_html = ""
    for idx, article in enumerate(articles):
        cat_color = get_category_color(article.get("category", ""))
        category = _escape(article.get("category", "General"))
        title = _escape(article.get("title", "Untitled"))
        source = _escape(article.get("source", "Unknown source"))
        time_ago = _escape(format_time_ago(article.get("published_date")))
        summary = _escape(article.get("gemma_summary", ""))
        link = _escape(article.get("link", "#"))
        relevance_label = format_relevance_label(article.get("final_score", 0))
        top_border = "border-top: none;" if idx == 0 else "border-top: 1px solid #eeeeee;"

        relevance_html = ""
        if relevance_label:
            relevance_html = f"""
            <span style="display:inline-block;font-size:10px;font-weight:700;color:#15803d;background:#dcfce7;padding:2px 7px;border-radius:10px;letter-spacing:0.5px;text-transform:uppercase;margin-left:6px;">{_escape(relevance_label)}</span>"""

        cards_html += f"""
        <tr>
          <td style="padding:24px 28px;{top_border}">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
              <tr>
                <td>
                  <span style="display:inline-block;font-size:10px;font-weight:700;color:#ffffff;background:{cat_color};padding:3px 9px;border-radius:10px;letter-spacing:0.5px;text-transform:uppercase;">{category}</span>{relevance_html}
                </td>
                <td align="right" style="font-size:11px;color:#9ca3af;white-space:nowrap;">{time_ago}</td>
              </tr>
            </table>
            <h2 style="margin:10px 0 4px 0;font-size:17px;font-weight:700;line-height:1.4;color:#111827;letter-spacing:0;">
              <a href="{link}" style="color:#111827;text-decoration:none;">{title}</a>
            </h2>
            <p style="margin:0 0 10px 0;font-size:12px;color:#6b7280;">{source}</p>
            <p style="margin:0 0 16px 0;font-size:14px;color:#374151;line-height:1.65;">{summary}</p>
            <a href="{link}"
               style="display:inline-block;background:#1a1a2e;color:#ffffff;text-decoration:none;padding:9px 20px;border-radius:6px;font-size:13px;font-weight:600;letter-spacing:0.2px;">
              Read Full Article &rarr;
            </a>
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily News Report - {_escape(date_str)}</title>
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:#f5f5f0;margin:0;padding:24px 16px;color:#1a1a1a;-webkit-text-size-adjust:100%;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
    <tr><td align="center">
      <table width="100%" style="max-width:640px;" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td style="background:#1a1a2e;padding:32px 28px 28px 28px;text-align:center;border-radius:8px 8px 0 0;">
            <p style="margin:0 0 6px 0;font-size:10px;letter-spacing:3px;color:#8892b0;text-transform:uppercase;font-weight:600;">Daily News Hunter</p>
            <h1 style="margin:0 0 8px 0;font-size:28px;font-weight:800;color:#ffffff;letter-spacing:0;">Daily News Report</h1>
            <p style="margin:0;font-size:13px;color:#8892b0;">{_escape(date_str)}</p>
          </td>
        </tr>
        <tr>
          <td style="background:#16213e;padding:12px 28px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
              <tr>
                <td style="text-align:center;padding:0 8px;border-right:1px solid #2d3561;">
                  <p style="margin:0;font-size:18px;font-weight:700;color:#64ffda;">{total_fetched}</p>
                  <p style="margin:2px 0 0 0;font-size:10px;color:#8892b0;text-transform:uppercase;letter-spacing:0.5px;">Fetched</p>
                </td>
                <td style="text-align:center;padding:0 8px;border-right:1px solid #2d3561;">
                  <p style="margin:0;font-size:18px;font-weight:700;color:#64ffda;">{total_scored}</p>
                  <p style="margin:2px 0 0 0;font-size:10px;color:#8892b0;text-transform:uppercase;letter-spacing:0.5px;">Scored</p>
                </td>
                <td style="text-align:center;padding:0 8px;border-right:1px solid #2d3561;">
                  <p style="margin:0;font-size:18px;font-weight:700;color:#64ffda;">{total_selected}</p>
                  <p style="margin:2px 0 0 0;font-size:10px;color:#8892b0;text-transform:uppercase;letter-spacing:0.5px;">Selected</p>
                </td>
                <td style="text-align:center;padding:0 8px;">
                  <p style="margin:0;font-size:11px;font-weight:600;color:#64ffda;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:120px;">{_escape(categories_str)}</p>
                  <p style="margin:2px 0 0 0;font-size:10px;color:#8892b0;text-transform:uppercase;letter-spacing:0.5px;">Topics</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="background:#ffffff;padding:20px 28px 8px 28px;border-top:3px solid #64ffda;">
            <p style="margin:0;font-size:13px;color:#6b7280;">Here are today's top stories, curated and summarised by Gemma&nbsp;4.</p>
          </td>
        </tr>
        {cards_html}
        <tr>
          <td style="background:#f9fafb;padding:20px 28px;text-align:center;border-top:1px solid #e5e7eb;border-radius:0 0 8px 8px;">
            <p style="margin:0;font-size:11px;color:#9ca3af;">Automated by <strong>Daily News Hunter</strong> &bull; Powered by Gemma&nbsp;4</p>
            <p style="margin:4px 0 0 0;font-size:11px;color:#d1d5db;">You are receiving this because you set up Daily News Hunter.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
