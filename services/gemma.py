import sys
import os
import json
import logging
import google.generativeai as genai
from utils.retry import call_with_retry

MODELS_IN_ORDER = [
    "models/gemma-4-31b-it",
    "models/gemma-4-27b-it",
    "models/gemma-4-12b-it",
    "models/gemma-4-4b-it"
]

_active_model = None

def get_model():
    global _active_model
    if _active_model:
        return _active_model
    
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    for model_name in MODELS_IN_ORDER:
        try:
            model = genai.GenerativeModel(model_name)
            # Try a dummy call or just trust it. GenerativeModel constructor doesn't verify existence until run, 
            # so let's log and return it.
            logging.info(f"Successfully selected model: {model_name}")
            _active_model = model
            return model
        except Exception as e:
            logging.warning(f"Model {model_name} failed: {e}")
    
    logging.error("All Gemma models failed.")
    return None

def extract_json(text):
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        return None

def process_article(article, categories, region):
    model = get_model()
    if not model:
        logging.error("No Gemma model available. Aborting run.")
        sys.exit(1)

    prompt = f"""
You are a news relevance scorer.
The user wants news about: {categories}
The user region is: {region}

Article title: {article['title']}
Article description: {article['description']}
Article source: {article['source']}

Your tasks:
1. Rate relevance from 0 to 10.
   10 means perfectly matches user interest.
   0 means completely irrelevant.
2. Write a 2 sentence summary in simple English.
3. Decide if this is clickbait.
   Clickbait means: shocking title with no real news,
   misleading headline, or pure motivation/opinion.
   Reject articles about: Celebrity gossip, Bollywood entertainment (unless chosen), Sports scores (unless chosen), Astrology, horoscopes, Motivational content, Crypto pump, Pure opinion pieces.

IMPORTANT: Respond ONLY in valid JSON format.
No extra text before or after.
No markdown formatting.
No code blocks.
Start response with {{ and end with }}

{{
  "score": 8,
  "summary": "First sentence here. Second sentence here.",
  "clickbait": false
}}
"""
    def _call_gemma():
        model = get_model()
        if not model:
            raise Exception("No Gemma model available")
        response = model.generate_content(
            prompt,
            request_options={"timeout": int(os.environ.get("GEMMA_REQUEST_TIMEOUT_SECONDS", 20))}
        )
        parsed = extract_json(response.text)
        if not parsed:
            raise Exception("Failed to parse JSON")
        if "score" not in parsed or "summary" not in parsed or "clickbait" not in parsed:
            raise Exception("Missing required fields in JSON")
        if not isinstance(parsed["score"], (int, float)) or not (0 <= parsed["score"] <= 10):
            raise Exception("Invalid score")
        if not isinstance(parsed["summary"], str) or len(parsed["summary"].strip()) == 0:
            raise Exception("Invalid summary")
        if not isinstance(parsed["clickbait"], bool):
            raise Exception("Invalid clickbait boolean")
        return parsed

    label = f"Score article: {article['title'][:30]}"
    result = call_with_retry(_call_gemma, label)
    
    if result:
        article['gemma_score'] = result['score']
        article['gemma_summary'] = result['summary']
        article['clickbait'] = result['clickbait']
        return article
    return None
