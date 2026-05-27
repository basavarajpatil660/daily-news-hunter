import time
import logging
import os

def call_with_retry(fn, label):
    max_attempts_raw = os.environ.get("GEMMA_MAX_ATTEMPTS", "5")
    max_attempts = 5
    if max_attempts_raw and max_attempts_raw.strip():
        try:
            max_attempts = int(max_attempts_raw.strip())
        except ValueError:
            logging.warning(f"Environment variable GEMMA_MAX_ATTEMPTS has invalid integer value '{max_attempts_raw}'. Falling back to default: 5")

    for attempt in range(1, max_attempts + 1):
        try:
            logging.info(f"AI [{label}]: attempt {attempt} of {max_attempts}...")
            result = fn()
            return result
        except Exception as e:
            err_str = str(e).lower()
            if any(term in err_str for term in ["not found", "404", "api key", "apikey", "permission", "invalid argument", "400", "403"]):
                logging.error(f"Permanent error encountered for [{label}]: {e}")
                return None
            
            logging.warning(f"Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                wait_time = 0
                if any(term in err_str for term in ["429", "quota", "limit exceeded", "resource_exhausted"]):
                    wait_time = 60
                elif any(term in err_str for term in ["503", "504", "service unavailable", "gateway timeout"]):
                    wait_time = 30
                elif "500" in err_str:
                    wait_time = 15
                
                # Exponential backoff base
                base_wait = 5 * (2 ** (attempt - 1))
                base_wait = min(base_wait, 60)
                
                final_wait = max(base_wait, wait_time)
                logging.info(f"Waiting {final_wait} seconds before next attempt...")
                time.sleep(final_wait)

    logging.error(f"AI permanently failed for [{label}] after {max_attempts} attempts.")
    return None
