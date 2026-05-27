import time
import logging
import os

def call_with_retry(fn, label):
    max_attempts_raw = os.environ.get("GEMMA_MAX_ATTEMPTS", "")
    max_attempts = 5
    if max_attempts_raw and max_attempts_raw.strip():
        try:
            max_attempts = int(max_attempts_raw.strip())
        except ValueError:
            logging.warning(f"Environment variable GEMMA_MAX_ATTEMPTS has invalid integer value '{max_attempts_raw}'. Falling back to default: 5")

    delay_seconds_raw = os.environ.get("GEMMA_RETRY_DELAY_SECONDS", "")
    delay_seconds = 2
    if delay_seconds_raw and delay_seconds_raw.strip():
        try:
            delay_seconds = int(delay_seconds_raw.strip())
        except ValueError:
            logging.warning(f"Environment variable GEMMA_RETRY_DELAY_SECONDS has invalid integer value '{delay_seconds_raw}'. Falling back to default: 2")

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
