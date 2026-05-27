import sys
import os
import json
import logging
import html
import google.generativeai as genai
from utils.retry import call_with_retry

MODELS_IN_ORDER = [
    "models/gemma-4-31b-it"
]

_active_model = None


def get_model():
    global _active_model
    if _active_model:
        return _active_model

    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    # MODEL_NAME override for testing (e.g. models/gemini-2.5-flash)
    override = os.environ.get("MODEL_NAME", "").strip()
    if override:
        try:
            model = genai.GenerativeModel(override)
            logging.info(f"Selected model (MODEL_NAME override): {override}")
            _active_model = model
            return model
        except Exception as e:
            logging.error(f"MODEL_NAME override '{override}' failed: {e}")
            return None

    # Default: iterate through Gemma 4 model list
    for model_name in MODELS_IN_ORDER:
        try:
            model = genai.GenerativeModel(model_name)
            logging.info(f"Selected model: {model_name}")
            _active_model = model
            return model
        except Exception as e:
            logging.warning(f"Model {model_name} failed: {e}")

    logging.error("All Gemma 4 models failed.")
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
        logging.error("No Gemma 4 model available. Aborting run.")
        sys.exit(1)

    prompt = f"""You are a strict technology news editor scoring articles for an executive daily briefing.
The reader cares about: {categories}
Reader region: {region}

Article title: {article['title']}
Article description: {article['description']}
Article source: {article['source']}

SCORING CRITERIA (0-10):
- Score 9-10 (Major, High-Impact Industry News): Reserved ONLY for critical news with major industry-wide implications. Examples: major AI research breakthroughs, foundation model releases, critical zero-day security vulnerabilities or major cyber attacks, significant government tech regulations or policy changes, large funding/acquisitions/IPOs (Series B+), or massive platform changes affecting millions of users/developers.
- Score 7-8 (Important/Useful News): Helpful, notable tech news but not groundbreaking. Examples: solid company product launches, smaller funding rounds, notable but non-critical security incidents, or developer-relevant updates.
- Score 5-6 (Normal/Routine Updates): Standard industry events, ordinary product updates, or typical tech press releases.
- Score below 5 (Low-Impact/Noise - Penalize heavily): Fitbit-related stories, app complaints, user complaints, app redesigns (such as Fitbit app UI redesigns or consumer health app UI changes), small subscription changes, minor updates, shopping/deals, coupon/sales, rumors (e.g. might/could), opinion pieces, or soft consumer/lifestyle product/tech stories. These MUST score below 5 unless there is a major, documented industry-wide impact.

SUMMARY - exactly 2 sentences with strong insight:
Sentence 1: What happened - name the key actor and the specific concrete action. Under 24 words.
Sentence 2: Why it matters - state the concrete, high-level business, developer, or industry impact. Give a strong, insightful explanation instead of a vague or obvious statement. Under 24 words.
Rules:
- Do NOT repeat the headline word-for-word.
- Do NOT start with "This article", "The article", or "This piece".
- No vague phrases like "This is important because" or "This could impact".
- Use active voice. Be specific.

IMPORTANCE REASON:
Write one short phrase (3-7 words) classifying why this story matters.
Examples: "Major AI product shift", "Security risk for developers", "Key platform policy change", "Low impact consumer update".

CLICKBAIT:
Set true if the headline is misleading, sensationalized, has no real news, or is pure opinion.

Respond ONLY in valid JSON. No extra text, no markdown, no code blocks.

{{
  "score": 8,
  "summary": "What happened sentence. Why it matters sentence.",
  "importance_reason": "Short phrase here",
  "clickbait": false
}}
"""

    def _call_gemma():
        selected_model = get_model()
        if not selected_model:
            raise Exception("No Gemma 4 model available")
        timeout_raw = os.environ.get("GEMMA_REQUEST_TIMEOUT_SECONDS", "")
        timeout = 20
        if timeout_raw and timeout_raw.strip():
            try:
                timeout = int(timeout_raw.strip())
            except ValueError:
                logging.warning(f"Environment variable GEMMA_REQUEST_TIMEOUT_SECONDS has invalid integer value '{timeout_raw}'. Falling back to default: 20")

        response = selected_model.generate_content(
            prompt,
            request_options={"timeout": timeout}
        )
        raw_text = response.text
        parsed = extract_json(raw_text)
        if not parsed:
            preview = raw_text[:200] if raw_text else "(empty response)"
            raise Exception(f"Failed to parse JSON from model response: {preview}")
        if "score" not in parsed or "summary" not in parsed or "clickbait" not in parsed:
            raise Exception("Missing required fields in JSON")
        if not isinstance(parsed["score"], (int, float)) or not (0 <= parsed["score"] <= 10):
            raise Exception("Invalid score")
        if not isinstance(parsed["summary"], str) or len(parsed["summary"].strip()) == 0:
            raise Exception("Invalid summary")
        parsed["summary"] = html.unescape(parsed["summary"])
        if "importance_reason" in parsed and isinstance(parsed["importance_reason"], str):
            parsed["importance_reason"] = html.unescape(parsed["importance_reason"])
        if not isinstance(parsed["clickbait"], bool):
            raise Exception("Invalid clickbait boolean")
        # importance_reason is optional for validation - use default if missing
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
