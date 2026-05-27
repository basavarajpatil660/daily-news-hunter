import time
import logging
import os

def call_with_retry(fn, label):
    max_attempts = int(os.environ.get("GEMMA_MAX_ATTEMPTS", 1))
    delay_seconds = int(os.environ.get("GEMMA_RETRY_DELAY_SECONDS", 2))

    for attempt in range(1, max_attempts + 1):
        try:
            logging.info(f"Gemma [{label}]: attempt {attempt} of {max_attempts}...")
            result = fn()
            return result
        except Exception as e:
            err_str = str(e).lower()
            if any(term in err_str for term in ["not found", "404", "api key", "apikey", "permission", "invalid argument", "400", "403"]):
                logging.error(f"Permanent error encountered for [{label}]: {e}")
                return None
            logging.debug(f"Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                time.sleep(delay_seconds)

    logging.error(f"Gemma permanently failed for [{label}]")
    return None
