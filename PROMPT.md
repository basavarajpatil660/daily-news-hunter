# 🤖 AI Daily News Trend Hunter — Full Build Prompt

> Copy this entire prompt and paste it into any AI assistant (Claude, Gemini, ChatGPT) to build the full project from scratch.

---

```
You are a Senior Python Automation Engineer.

Build or update a project called:

AI Daily News Trend Hunter

IMPORTANT:
Follow the existing project structure exactly.
Do not rename files.
Do not move files.
Do not introduce new frameworks.
Do not add Node.js, JavaScript, npm, React, frontend tooling, or any non-Python stack.

This project must be Python only.
Use Python 3.11+ and pip only.

Use this exact folder/file structure:

main.py
requirements.txt
.env.example
README.md
LICENSE
CONTRIBUTING.md
.github/workflows/daily.yml
config/__init__.py
config/categories.py
services/__init__.py
services/rss.py
services/gemma.py
services/mail.py
utils/__init__.py
utils/retry.py
utils/filter.py
utils/deduplicate.py
utils/scoring.py
utils/format.py
reports/__init__.py
reports/email_template.py

Do not create extra files unless absolutely required.

==================================================
ENVIRONMENT VARIABLES
==================================================

Use only these simple environment variable names:

GEMINI_API_KEY=your_google_ai_studio_key_here
GMAIL_USER=your_gmail_address_here
GMAIL_PASS=your_gmail_app_password_here
EMAIL_TO=recipient_email_here
NEWS_CATEGORIES=AI News,Tech News
NEWS_REGION=IN
NEWS_LANGUAGE=en
TOP_ARTICLES_COUNT=10
MAX_ARTICLES_TO_SCORE=15
SCHEDULE_TIME=daily_morning

Create `.env.example` with these exact names.

Do not add MODEL_NAME.
Do not add user-facing retry env variables.
Do not add complicated config.

NEWS_CATEGORIES controls categories automatically.
Example:
NEWS_CATEGORIES=AI News,Tech News,Cybersecurity

If an unknown category is provided, ignore it and log a warning.
If no valid category is found, default to:
AI News,Tech News

NEWS_REGION:
- IN means India
- GLOBAL means worldwide
- US means USA

NEWS_LANGUAGE:
- en means English
- hi means Hindi
- both means English and Hindi

SCHEDULE_TIME:
Keep it in `.env.example` for simple user understanding.
The actual GitHub Actions schedule can remain hardcoded in daily.yml.

==================================================
MODEL RULE
==================================================

Use Google AI Studio through:

google-generativeai

Use env variable:

GEMINI_API_KEY

Use ONLY this model string:

gemma-4-31b-it

Do not use:
- gemini-2.5-flash
- gemini-1.5-flash
- Gemma 3
- Gemma 2
- OpenAI
- GPT
- any fallback model

If Gemma 4 returns 404:
- Log clearly that Gemma 4 is unavailable.
- Log that it will retry on the next scheduled run.
- Exit cleanly with sys.exit(0).
- Do not try any other model.

If Gemma 4 returns 503, 504, timeout, or deadline errors:
- Retry initialization up to 5 times.
- Wait 20s, 40s, 60s, 60s, 60s.
- If all fail, exit cleanly with sys.exit(0).

==================================================
RSS FETCHING
==================================================

Use RSS only.

Use:
- feedparser
- requests
- python-dateutil

Use Google News RSS based on category keywords.

Also include:
- TechCrunch
- The Verge
- Wired
- Ars Technica
- VentureBeat
- MIT Technology Review
- BBC Tech
- Economic Times Tech
- The Hindu Science
- India Today Tech
- Hindustan Times Tech

Do not include broken Reuters or NDTV RSS feeds.

For each article extract:
- title
- link
- published_date
- description
- source
- thumbnail if available

Decode HTML entities with html.unescape.

Use python-dateutil for all date parsing.
Reject articles older than 24 hours.

Fetch feeds concurrently using Python threading.
Use 10 second timeout per feed.
Retry each feed up to 3 times.
If one feed fails, log it and continue.

==================================================
GEMMA ARTICLE RESPONSE
==================================================

For each article, Gemma must return JSON with these exact keys:

{
  "score": 8,
  "summary": "Two simple sentences.",
  "importance_reason": "Brief insight phrase",
  "clickbait": false
}

Use `importance_reason`, not `insight`, because the existing email template expects `importance_reason`.

Gemma should:
- score relevance from 0 to 10
- write a 2 sentence summary
- detect clickbait
- write importance_reason in 3 to 7 words

Use:
- temperature: 0.1
- response_mime_type: "application/json"

==================================================
SCORING AND FILTERING
==================================================

Before Gemma:
- remove duplicate URLs
- remove duplicate titles
- remove near duplicates
- reject articles older than 24 hours
- reject empty title or description
- pre-rank articles locally

Boost keywords:
- AI regulation
- cybersecurity breach
- funding round
- acquisition
- developer tools
- API release
- open source
- platform change
- research paper
- government policy
- data privacy law

Penalty keywords:
- deals
- rumors
- UI change
- complaint
- review
- unboxing
- comparison
- best of list
- top 10
- how to
- tips and tricks

Final Score = Gemma Score + Source Modifier.

Minimum qualifying score: 5.
Clickbait is always rejected.
Sort final articles by final score descending.

==================================================
RETRY LOGIC
==================================================

Use utils/retry.py.

Maximum 5 attempts.

Waits:
- attempt 1 fail: wait 5 seconds
- attempt 2 fail: wait 10 seconds
- attempt 3 fail: wait 20 seconds
- attempt 4 fail: wait 40 seconds
- attempt 5 fail: stop

Overrides:
- 429/quota/rate: wait 60 seconds
- 503/504/timeout/deadline: wait 30 seconds
- 500: wait 15 seconds
- 404: return None immediately, no retry

No 15-minute waits.
No infinite loops.
Sleep 2 seconds after successful Gemma calls.

==================================================
EMAIL
==================================================

Use reports/email_template.py.

Email rules:
- single column
- inline CSS only
- Gmail compatible
- max width 600px
- no thumbnails
- no placeholders
- no score like X/11
- no Top Pick label
- Important badge only for final score 9+
- each article card shows:
  - category
  - source
  - time ago
  - title
  - summary
  - Insight line from importance_reason
  - Read Full Article link

Footer must say:

Powered by @b.nick.ai

Link:
https://www.instagram.com/b.nick.ai/

If email sending fails:
- save report_backup.html
- exit cleanly

==================================================
GITHUB ACTIONS
==================================================

Use existing workflow path:

.github/workflows/daily.yml

Workflow:
- runs-on ubuntu-latest
- Python 3.11
- pip install -r requirements.txt
- run python main.py
- schedule daily at 6:00 AM IST
- workflow_dispatch enabled
- timeout-minutes: 30

Pass these secrets:

GEMINI_API_KEY
GMAIL_USER
GMAIL_PASS
EMAIL_TO
NEWS_CATEGORIES
NEWS_REGION
NEWS_LANGUAGE
TOP_ARTICLES_COUNT
MAX_ARTICLES_TO_SCORE

SCHEDULE_TIME may stay in `.env.example`, but the workflow schedule can remain hardcoded.

==================================================
README GUIDE
==================================================

README should guide the user clearly:

1. Create a GitHub repository.
2. Make it PRIVATE.
3. Push this project to the private repo.
4. Go to GitHub repo Settings.
5. Open Secrets and variables -> Actions.
6. Add repository secrets:
   - GEMINI_API_KEY
   - GMAIL_USER
   - GMAIL_PASS
   - EMAIL_TO
   - NEWS_CATEGORIES
   - NEWS_REGION
   - NEWS_LANGUAGE
   - TOP_ARTICLES_COUNT
   - MAX_ARTICLES_TO_SCORE

Explain:
- GitHub Secrets hide keys from other users.
- Never commit `.env`.
- Never paste API keys into README.
- Use Gmail App Password, not normal Gmail password.
- Get Google AI Studio key from:
  https://aistudio.google.com/app/apikey

==================================================
ACCEPTANCE
==================================================

The final project must match the existing repo structure exactly.

Do not replace the architecture with a different design.
Do not rename `importance_reason` to `insight`.
Do not introduce MODEL_NAME.
Do not switch to Gemini Flash.
Do not add thumbnails to email.
Do not remove @b.nick.ai footer.
Do not change from Python-only.

Build using the existing file layout and current working behavior.
```

---

<div align="center">

Built by [**@b.nick.ai**](https://www.instagram.com/b.nick.ai/) · [Back to README](README.md)

</div>

