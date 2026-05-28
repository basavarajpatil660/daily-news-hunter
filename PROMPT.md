# 🤖 AI Daily News Trend Hunter — Full Build Prompt

> Copy this entire prompt and paste it into any AI assistant (Claude, Gemini, ChatGPT) to build the full project from scratch.

---

```
You are a Senior Full-Stack Automation Engineer and AI Product Architect.

I want you to build a production-ready MVP called:

AI Daily News Trend Hunter

This is a daily automation agent built in Python that:
1. Fetches real trending news using RSS feeds (100% free)
2. Uses Gemma 4 model ONLY for scoring,
   summarizing, and filtering articles
3. Sends a beautiful HTML email report daily

==================================================
MOST IMPORTANT RULE — READ THIS FIRST
==================================================

This project must be Python only.
Do NOT use Node.js.
Do NOT use JavaScript.
Do NOT use npm.
Use pip and Python 3.11 or higher.

The ONLY AI model allowed in this project is Gemma 4.
The ONLY model string to use is: gemma-4-31b-it

Do NOT use any other model under any circumstance.
Do NOT fall back to gemini-2.5-flash.
Do NOT fall back to gemini-1.5-flash.
Do NOT fall back to any Gemma 3 or Gemma 2 model.
Do NOT fall back to GPT or any OpenAI model.
Do NOT fall back to any non-Gemma-4 model ever.

If gemma-4-31b-it returns 404 (model not found):
- Log: "Gemma 4 (gemma-4-31b-it) is not available."
- Log: "Will retry at next scheduled run."
- Exit cleanly with sys.exit(0)
- Do NOT try any other model
- Do NOT crash with exit code 1

If gemma-4-31b-it returns 504 or 503 or timeout
or deadline expired:
- This means Google servers are temporarily busy
- Retry initialization up to 5 times
- Attempt 1 fails: wait 20 seconds
- Attempt 2 fails: wait 40 seconds
- Attempt 3 fails: wait 60 seconds
- Attempt 4 fails: wait 60 seconds
- Attempt 5 fails: wait 60 seconds
- If all 5 fail: log and exit with sys.exit(0)
- Do NOT try any other model

API provider: Google AI Studio
Python SDK: google-generativeai
API Key env variable: GEMINI_API_KEY

==================================================
NEWS FETCHING — RSS FEEDS ONLY
==================================================

Use RSS feeds to fetch real fresh news articles.
This is 100% free. No extra API key needed.

Use the feedparser Python library to parse feeds.

RSS feed sources to use:

Google News RSS (primary):
For each search keyword, build this URL:
https://news.google.com/rss/search?q=KEYWORD&hl=en-IN&gl=IN&ceid=IN:en

For Hindi content if user chose it:
https://news.google.com/rss/search?q=KEYWORD&hl=hi-IN&gl=IN&ceid=IN:hi

Additional reliable RSS feeds to always include:

TechCrunch: https://techcrunch.com/feed/
The Verge: https://www.theverge.com/rss/index.xml
Wired: https://www.wired.com/feed/rss
Ars Technica: https://feeds.arstechnica.com/arstechnica/index
VentureBeat: https://venturebeat.com/feed/
MIT Tech Review: https://www.technologyreview.com/feed/
BBC Tech: http://feeds.bbci.co.uk/news/technology/rss.xml
Economic Times Tech: https://economictimes.indiatimes.com/tech/rss.cms
The Hindu Science: https://www.thehindu.com/sci-tech/feeder/default.rss
India Today Tech: https://www.indiatoday.in/rss/1206578
Hindustan Times Tech: https://www.hindustantimes.com/feeds/rss/technology/rssfeed.xml

IMPORTANT: Do NOT include these feeds — they are broken:
- Reuters Tech (causes errors)
- NDTV Tech RSS (causes errors)

For each RSS feed entry, extract and decode:
- title (decode all HTML entities like &#8217; to proper characters)
- link (URL)
- published date
- summary or description (decode all HTML entities)
- source name (decode all HTML entities)
- thumbnail/media if available

DATE PARSING — USE python-dateutil:
Use this exact function for all date parsing:

from datetime import timezone, timedelta
from dateutil import parser as dateutil_parser

def parse_date(date_string):
    try:
        dt = dateutil_parser.parse(date_string)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc) - timedelta(hours=12)

This handles all ISO 8601 formats including timezone
offsets like 2026-05-27T18:30:02-04:00 correctly.
Never use a custom date parser — always use dateutil.

Reject any article older than 24 hours.

Fetch all feeds concurrently using Python threading.
Set a timeout of 10 seconds per feed request.
Retry each feed up to 3 times before skipping.
If a feed fails, log the error and skip it.
Do not stop the whole script for one failed feed.

==================================================
GEMMA 4 INITIALIZATION — MANDATORY
==================================================

Create this function in services/gemma.py:

def initialize_gemma_with_retry():
    import time
    for attempt in range(1, 6):
        try:
            model = genai.GenerativeModel("gemma-4-31b-it")
            test = model.generate_content("Reply with: ok")
            if test:
                logging.info("Gemma 4 initialized successfully.")
                return model
        except Exception as e:
            err = str(e)
            if "404" in err:
                logging.error("Gemma 4 (gemma-4-31b-it) not found (404).")
                logging.error("Will retry at next scheduled run.")
                return None
            elif any(x in err for x in ["504", "503", "timeout", "deadline", "Deadline"]):
                wait = min(attempt * 20, 60)
                logging.warning(f"Gemma 4 busy (attempt {attempt}/5). Waiting {wait}s...")
                time.sleep(wait)
            else:
                logging.error(f"Unexpected Gemma 4 error: {e}")
                return None
    logging.error("Gemma 4 failed after 5 initialization attempts.")
    logging.error("Will retry at next scheduled run.")
    return None

In main.py, call initialize_gemma_with_retry() first.
If it returns None, call sys.exit(0) immediately.
Never attempt any other model.
Log the confirmed model name after initialization.

==================================================
GEMMA 4 RESPONSIBILITIES
==================================================

Gemma 4 does ONLY these tasks:
1. Score each article for relevance (0 to 10)
2. Generate 2 to 3 line summary for each article
3. Detect if article is clickbait (true or false)
4. Generate one insight line explaining importance

For each article, call Gemma 4 with this prompt:

"""
You are a news relevance scorer.
The user wants news about: {categories}
The user region is: {region}

Article title: {title}
Article description: {description}
Article source: {source}

Your tasks:
1. Rate relevance from 0 to 10.
   10 means perfectly matches user interest.
   0 means completely irrelevant.
   Only give scores of 7 or above for genuinely
   important, substantial news stories.
   Do not give high scores to minor app updates,
   rumors, opinion pieces, or consumer complaints.
   Do not give high scores to deals, unboxing,
   or soft consumer lifestyle content.
2. Write a 2 sentence summary in simple English.
3. Decide if this is clickbait.
   Clickbait means: shocking title with no real news,
   misleading headline, or pure motivation/opinion.
4. Write one short insight line explaining why
   this article matters to the user.

IMPORTANT: Respond ONLY in valid JSON format.
No extra text before or after.
No markdown formatting.
No code blocks.
Start response with { and end with }

{
  "score": 8,
  "summary": "First sentence here. Second sentence here.",
  "clickbait": false,
  "insight": "Why this matters in one line."
}
"""

Always use this generation config when calling Gemma 4:
- temperature: 0.1
- response_mime_type: "application/json"

==================================================
JSON PARSING FROM GEMMA 4
==================================================

def extract_json(text):
    if not text:
        return None
    import re
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'```', '', text)
    text = text.strip()
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        pass
    match = re.search(r'\{[^{}]*"score"[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None

def validate_gemma_response(parsed):
    if not isinstance(parsed, dict):
        return False
    score = parsed.get("score")
    summary = parsed.get("summary")
    clickbait = parsed.get("clickbait")
    if not isinstance(score, (int, float)):
        return False
    if not (0 <= score <= 10):
        return False
    if not isinstance(summary, str) or len(summary.strip()) < 10:
        return False
    if isinstance(clickbait, str):
        parsed["clickbait"] = clickbait.lower() == "true"
    elif not isinstance(clickbait, bool):
        return False
    if "insight" not in parsed or not isinstance(parsed["insight"], str):
        parsed["insight"] = ""
    return True

==================================================
RETRY LOGIC — utils/retry.py
==================================================

FUNCTION: call_with_retry(fn, label)

Exponential backoff:
- Attempt 1 fails: wait 5 seconds
- Attempt 2 fails: wait 10 seconds
- Attempt 3 fails: wait 20 seconds
- Attempt 4 fails: wait 40 seconds
- Attempt 5 fails: wait 60 seconds
- Maximum wait capped at 60 seconds

Error-specific overrides:
- "429" / "quota" / "rate" → wait 60 seconds minimum
- "503" / "504" / "timeout" / "deadline" → wait 30 seconds
- "500" → wait 15 seconds
- "404" → return None immediately, no retry

Maximum 5 attempts. No Round 2. No 15 minute waits.
Mandatory time.sleep(2) after every successful call.

==================================================
QUOTA PROTECTION — MANDATORY
==================================================

Before sending to Gemma 4:
1. Pre-rank all articles locally by keyword signals
2. Cap at MAX_ARTICLES_TO_SCORE (default: 15)
3. Process sequentially — never parallel
4. sleep(2) between every call

Boost keywords (+2): "AI regulation", "cybersecurity breach",
"funding round", "acquisition", "developer tools",
"API release", "open source", "platform change",
"research paper", "government policy", "data privacy law",
"security vulnerability", "data breach", "lawsuit", "antitrust"

Penalty keywords (-2): "deals", "rumors", "UI change",
"complaint", "review", "unboxing", "comparison",
"best of list", "top 10", "how to", "tips and tricks",
"buying guide", "hands on"

==================================================
FIRST STEP — ASK THE USER FOR PREFERENCES
==================================================

Before writing any code, ask the user the following
questions ONE BY ONE in a friendly conversational way.

Do NOT ask all questions at once.
Ask one question, wait for the answer,
then ask the next question.

QUESTION 1:
"Which news categories do you want to track?
You can choose one or multiple."

1. AI News (Latest AI tools, models, releases)
2. Tech News (Software, hardware, startups, big tech)
3. AI App Building and Development
4. Cybersecurity News
5. Startup and Entrepreneur News
6. Science and Research News
7. Space and Astronomy News
8. Finance and Economy News
9. Health and Medical Tech News
10. Custom (I will describe my own topic)

QUESTION 2:
"How many top articles do you want per email?"
Options: 5 / 10 / 15 / 20 articles

QUESTION 3:
"How often do you want to receive the email?"
- Once daily at 6:00 AM IST
- Twice daily at 6:00 AM and 6:00 PM IST
- Custom time

QUESTION 4:
"Do you want English news only or Hindi too?"
- English only
- English and Hindi both

QUESTION 5:
"Which region should news focus on?"
- India only
- Global worldwide
- USA only
- Custom region

After all 5 answers confirm:
"Here is what I will build: [summary].
Shall I proceed? yes or no"

Only after user says yes, build the project.

==================================================
EXCLUSION RULES
==================================================

Reject without Gemma 4:
- Articles older than 24 hours
- Empty title or description
- Duplicate URLs
- Near-duplicate titles (80% word match)

Tell Gemma 4 to score 0-4:
- Celebrity gossip
- Bollywood unless user chose it
- Sports scores unless user chose it
- Astrology / horoscopes
- Motivational content
- Crypto pump schemes
- Pure opinion pieces

==================================================
SCORING SYSTEM
==================================================

Final Score = Gemma Score (0-10) + Source Modifier (±1)

+1 for: TechCrunch, The Verge, Wired, Ars Technica,
MIT Tech Review, BBC, Reuters, AP News, The Hindu,
Times of India, Economic Times, NDTV, India Today,
Hindustan Times, Bloomberg, Forbes, VentureBeat,
ZDNet, CNET, Engadget

-1 for unknown sources

Minimum qualifying score: 5
Important badge: score 9+
Clickbait: always rejected

==================================================
EMAIL DESIGN RULES
==================================================

- Single column, inline CSS only
- Gmail compatible, max-width 600px
- NO image thumbnails or placeholders
- NO score as X/11
- NO Top Pick labels
- Important badge for score 9+ only
- Each card: headline, source, time ago, category badge,
  2-line summary, insight line, Read Full Article button
- Footer: "Powered by @b.nick.ai"
  linked to https://www.instagram.com/b.nick.ai

==================================================
REQUIREMENTS.TXT
==================================================

feedparser==6.0.11
requests==2.31.0
google-generativeai==0.7.2
python-dotenv==1.0.1
python-dateutil==2.9.0

==================================================
GITHUB ACTIONS WORKFLOW
==================================================

- runs-on: ubuntu-latest
- timeout-minutes: 30
- python-version: "3.11"
- Schedule: cron "30 0 * * *" (6:00 AM IST)
- workflow_dispatch enabled
- All 9 secrets passed as env variables

==================================================
ACCEPTANCE CRITERIA
==================================================

1.  pip install -r requirements.txt works
2.  python main.py runs without syntax errors
3.  Missing/empty env vars show clear message
4.  Only gemma-4-31b-it used always
5.  404 exits cleanly with sys.exit(0)
6.  504/503/timeout retries up to 5 times
7.  No other model tried ever
8.  RSS feeds concurrent with threading
9.  Feed failures handled gracefully
10. python-dateutil for all date parsing
11. HTML entities decoded in all fields
12. Only last 24 hours articles included
13. Pre-ranking before AI scoring
14. Max 15 articles to Gemma 4 per run
15. Sequential processing for Gemma 4
16. 2s gap between every Gemma 4 call
17. Exponential backoff in retry logic
18. 404 never triggers retry
19. No 15 minute waits anywhere
20. Articles below score 5 excluded
21. Clickbait always rejected
22. Sorted by final score descending
23. HTML email has no image placeholders
24. No score as X/11
25. No Top Pick labels
26. Important badge for score 9+ only
27. Insight line in each article card
28. Footer: Powered by @b.nick.ai → Instagram
29. report_backup.html saved if email fails
30. GitHub Actions timeout 30 minutes
31. workflow_dispatch enabled
32. Python 3.11 in GitHub Actions
33. .env in .gitignore
34. .env.example with all 9 placeholders
35. requirements.txt includes python-dateutil
36. All 9 GitHub Secrets documented
37. Confirmed model name logged
38. Script completion time logged in seconds

==================================================
BEGIN
==================================================

Start by asking me the 5 preference questions.
Ask ONE question at a time.
Wait for my answer before asking the next.
After all 5 answers, confirm my choices.
Ask: Shall I proceed to build the project?
Only after I say yes, start building all the code.
```

---

<div align="center">

Built by [**@b.nick.ai**](https://www.instagram.com/b.nick.ai/) · [Back to README](README.md)

</div>

