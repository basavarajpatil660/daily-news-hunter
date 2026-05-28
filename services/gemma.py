import sys
import os
import json
import logging
import html
import time
import re
import google.generativeai as genai
from utils.retry import call_with_retry

MODEL_NAME = "gemma-4-31b-it"
_model = None

def initialize_gemma_with_retry():
    """
    Initializes the Gemma 4 model with retries and exponential waits.
    """
    global _model
    if _model is not None:
        return _model

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY is missing from environment variables.")
        return None

    genai.configure(api_key=api_key)
    for attempt in range(1, 6):  # 5 attempts
        try:
            model = genai.GenerativeModel("gemma-4-31b-it")
            test = model.generate_content("Reply with: ok")
            if test:
                logging.info("Gemma 4 initialized successfully.")
                _model = model
                return model
        except Exception as e:
            err = str(e)
            if "404" in err:
                logging.error("Gemma 4 model not found (404). Cannot continue.")
                return None
            elif "504" in err or "503" in err or "timeout" in err.lower() or "deadline" in err.lower():
                wait = min(attempt * 20, 60)
                logging.warning(f"Gemma 4 busy (attempt {attempt}/5). Waiting {wait}s...")
                time.sleep(wait)
            else:
                logging.error(f"Unexpected Gemma 4 error: {e}")
                return None
    logging.error("Gemma 4 failed after 5 initialization attempts.")
    return None

def get_model():
    """
    Returns the cached GenerativeModel instance.
    """
    global _model
    return _model


def extract_json(text):
    """
    Cleans response text from the model and extracts JSON.
    """
    if not text:
        return None
    # Strip markdown code blocks first
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'```', '', text)
    text = text.strip()
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        pass
    # Last resort pattern match
    match = re.search(r'\{[^{}]*"score"[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None

def validate_gemma_response(parsed):
    """
    Validates the parsed model response matching required types and ranges.
    """
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
        
    # Handle Gemma returning "true"/"false" as strings
    if isinstance(clickbait, str):
        parsed["clickbait"] = clickbait.lower() == "true"
    elif not isinstance(clickbait, bool):
        return False
        
    return True

def process_article(article, categories, region):
    """
    Calls Gemma 4 to score and summarize the article. Uses call_with_retry for safety.
    """
    model = get_model()
    if not model:
        logging.error("Gemma 4 model is not initialized.")
        sys.exit(1)

    # Determine if we need to explicitly reject entertainment/sports
    lower_cats = categories.lower()
    reject_entertainment = "bollywood" not in lower_cats and "entertainment" not in lower_cats
    reject_sports = "sports" not in lower_cats
    
    rejection_details = []
    if reject_entertainment:
        rejection_details.append("- Bollywood or celebrity entertainment")
    if reject_sports:
        rejection_details.append("- Sports scores or sports updates")
    rejection_details.extend([
        "- Celebrity gossip",
        "- Astrology or horoscopes",
        "- Motivational content with no real news value",
        "- Crypto pump or investment schemes",
        "- Pure opinion pieces"
    ])
    
    rejection_text = "\n".join(rejection_details)

    prompt = f"""You are a news relevance scorer.
The user wants news about: {categories}
The user region is: {region}

Article title: {article['title']}
Article description: {article['description']}
Article source: {article['source']}

Your tasks:
1. Rate relevance from 0 to 10.
   10 means perfectly matches user interest.
   0 means completely irrelevant.
   Only give scores of 7 or above for genuinely
   important, substantial news stories.
   Do not give high scores to minor app updates,
   rumors, opinion pieces, or consumer complaints.
2. Write a 2 sentence summary in simple English.
3. Write an importance_reason explaining why the story matters (3-7 words).
4. Decide if this is clickbait.
   Clickbait means: shocking title with no real news,
   misleading headline, or pure motivation/opinion.

Additionally, you MUST reject (rate relevance score 0) any articles about:
{rejection_text}

IMPORTANT: Respond ONLY in valid JSON format.
No extra text before or after.
No markdown formatting.
No code blocks.
Start response with {{ and end with }}

{{
  "score": 8,
  "summary": "First sentence here. Second sentence here.",
  "importance_reason": "Brief insight phrase",
  "clickbait": false
}}"""

    def _call_gemma():
        # Ensure model is checked/loaded
        selected_model = get_model()
        
        try:
            response = selected_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                )
            )
            raw_text = response.text
        except Exception as e:
            err_msg = str(e).lower()
            # If 404 is raised here: permanent model error, exit cleanly
            if "404" in err_msg or "not found" in err_msg or "not_found" in err_msg:
                logging.error("Gemma 4 (gemma-4-31b-it) is not available right now.")
                logging.error("Will retry at next scheduled run.")
                sys.exit(0)
            raise e
            
        parsed = extract_json(raw_text)
        if not parsed:
            raise Exception("Failed to extract JSON from Gemma response")
            
        if not validate_gemma_response(parsed):
            raise Exception("Gemma response failed validation checks")
            
        # Ensure optional importance_reason is set
        if "importance_reason" not in parsed or not isinstance(parsed.get("importance_reason"), str):
            parsed["importance_reason"] = ""
            
        return parsed

    label = f"Score article: {article['title'][:30]}"
    result = call_with_retry(_call_gemma, label)

    if result:
        article["gemma_score"] = result["score"]
        article["gemma_summary"] = result["summary"]
        article["importance_reason"] = result.get("importance_reason", "")
        article["clickbait"] = result["clickbait"]
        return article
        
    return None

