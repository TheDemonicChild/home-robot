import logging
import time
from functools import wraps

# ----- Logging Configuration -----

# Flag to enable or disable debug logging
ENABLE_DEBUG_LOG = False  # Set to False to disable debug logging

# Determine the logging level based on the ENABLE_DEBUG_LOG flag
LOG_LEVEL = logging.DEBUG if ENABLE_DEBUG_LOG else logging.INFO

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("debug_timings.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ----- Timing Decorator with Toggle -----

# Toggle flag to enable or disable timing
ENABLE_TIMING = False  # Set to True to enable timing

def timing(func):
    """
    Decorator to measure and log the execution time of functions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if ENABLE_TIMING:
            start_time = time.perf_counter()
            logger.debug(f"Started '{func.__name__}'")
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            logger.debug(f"Finished '{func.__name__}' in {elapsed_time:.4f} seconds")
            return result
        else:
            return func(*args, **kwargs)
    return wrapper