import time
import logging

def call_with_retry(fn, label):
    # ROUND 1
    for attempt in range(1, 11):
        try:
            logging.info(f"Gemma 4 [{label}]: attempt {attempt} of 10...")
            result = fn()
            return result
        except Exception as e:
            err_str = str(e).lower()
            # If it is a API key error, permission error, or model not found error, fail fast.
            if any(term in err_str for term in ["not found", "404", "api key", "apikey", "permission", "invalid argument", "400", "403"]):
                logging.error(f"Permanent error encountered for [{label}]: {e}")
                raise e
            logging.debug(f"Attempt {attempt} failed: {e}")
            time.sleep(3)
    
    logging.warning(f"All 10 attempts failed for [{label}]")
    logging.info("Waiting 15 minutes before round 2...")
    time.sleep(900)
    logging.info(f"Starting round 2 for [{label}]...")
    
    # ROUND 2
    for attempt in range(1, 11):
        try:
            logging.info(f"Gemma 4 [{label}]: round 2 attempt {attempt} of 10...")
            result = fn()
            return result
        except Exception as e:
            err_str = str(e).lower()
            if any(term in err_str for term in ["not found", "404", "api key", "apikey", "permission", "invalid argument", "400", "403"]):
                logging.error(f"Permanent error encountered for [{label}]: {e}")
                raise e
            logging.debug(f"Round 2 attempt {attempt} failed: {e}")
            time.sleep(3)
            
    logging.error(f"Gemma 4 permanently failed for [{label}]")
    return None

