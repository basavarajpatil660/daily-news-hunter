import time
import logging

def call_with_retry(fn, label):
    """
    Execute fn with up to 5 attempts, utilizing exponential backoff
    and error-specific wait overrides. Caps wait times at 60 seconds
    and implements a mandatory 2-second delay after successful calls.
    """
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            logging.info(f"AI [{label}]: attempt {attempt} of {max_attempts}...")
            result = fn()
            
            # Mandatory 2 second gap after every successful API call
            time.sleep(2)
            return result
        except Exception as e:
            err_str = str(e).lower()
            
            # 404 is a permanent model error - do not retry
            if "404" in err_str or "not found" in err_str:
                logging.error(f"Permanent 404 error encountered for [{label}]: {e}")
                return None
                
            logging.warning(f"Attempt {attempt} failed for [{label}]: {e}")
            
            if attempt == max_attempts:
                break
                
            # Base exponential backoff wait times
            backoff_waits = {1: 5, 2: 10, 3: 20, 4: 40}
            base_wait = backoff_waits.get(attempt, 60)
            
            # Error-specific wait overrides
            override_wait = 0
            if any(term in err_str for term in ["429", "quota", "rate"]):
                override_wait = 60
            elif any(term in err_str for term in ["503", "504", "timeout"]):
                override_wait = 30
            elif "500" in err_str:
                override_wait = 15
                
            # Apply override and cap at 60s
            wait_time = min(max(base_wait, override_wait), 60)
            
            logging.info(f"Waiting {wait_time} seconds before retrying [{label}]...")
            time.sleep(wait_time)
            
    logging.error(f"AI permanently failed for [{label}] after {max_attempts} attempts.")
    return None

