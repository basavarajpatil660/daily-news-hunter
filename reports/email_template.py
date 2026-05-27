from utils.format import format_time_ago, format_score_badge, get_category_color

def generate_html(articles, summary_stats):
    if not articles:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
            <h2>Daily News Hunter</h2>
            <p>No qualifying articles were found today for your chosen categories.</p>
            <p>The system will try again at the next scheduled run automatically.</p>
        </body>
        </html>
        """
        
    date_str = summary_stats['date']
    categories_str = ", ".join(summary_stats['categories'])
    
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px; color: #111827;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="background: #111827; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">Daily News Report</h1>
                <p style="margin: 5px 0 0 0; color: #9ca3af;">{date_str}</p>
            </div>
            
            <div style="padding: 20px; background: #f3f4f6; border-bottom: 1px solid #e5e7eb;">
                <h3 style="margin-top: 0;">Summary Stats</h3>
                <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #4b5563;">
                    <li>Total RSS articles fetched: {summary_stats['total_fetched']}</li>
                    <li>Total scored by Gemma 4: {summary_stats['total_scored']}</li>
                    <li>Total qualifying articles: {summary_stats['total_qualifying']}</li>
                    <li>Categories covered: {categories_str}</li>
                    <li>Model used: Gemma 4</li>
                </ul>
            </div>
            
            <div style="padding: 20px;">
    """
    
    for a in articles:
        cat_color = get_category_color(a['category'])
        initial = a['category'][0].upper() if a['category'] else 'N'
        
        thumbnail_html = f'<img src="{a["thumbnail"]}" alt="Thumbnail" style="width: 80px; height: 80px; object-fit: cover; border-radius: 6px;">' if a['thumbnail'] else f'<div style="width: 80px; height: 80px; background: {cat_color}; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold; text-align: center; line-height: 80px;">{initial}</div>'
        
        html += f"""
        <div style="margin-bottom: 24px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px;">
            <div style="display: flex; gap: 16px;">
                <div style="flex-shrink: 0;">
                    {thumbnail_html}
                </div>
                <div>
                    <h2 style="margin: 0 0 8px 0; font-size: 18px;">
                        <a href="{a['link']}" style="color: #111827; text-decoration: none;">{a['title']}</a>
                    </h2>
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 8px;">
                        <strong>{a['source']}</strong> &bull; {format_time_ago(a['published_date'])}
                    </div>
                    <div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">
                        <span style="background: {cat_color}; color: white; font-size: 12px; padding: 2px 8px; border-radius: 12px;">{a['category']}</span>
                        <span style="background: #e5e7eb; color: #374151; font-size: 12px; padding: 2px 8px; border-radius: 12px; font-weight: bold;">Score: {format_score_badge(a['final_score'])}</span>
                    </div>
                </div>
            </div>
            <p style="margin: 0; font-size: 14px; color: #4b5563; line-height: 1.5;">
                {a['gemma_summary']}
            </p>
            <div style="margin-top: 16px; text-align: right;">
                <a href="{a['link']}" style="display: inline-block; background: #111827; color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; font-size: 14px; font-weight: bold;">Read Full Article</a>
            </div>
        </div>
        """
        
    html += """
            </div>
            <div style="text-align: center; padding: 20px; font-size: 12px; color: #9ca3af; background: #f3f4f6;">
                Automated by Daily News Hunter
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
