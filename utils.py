import logging
import time
from functools import wraps
import re

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("debug_timings.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MaskBase64Filter(logging.Filter):
    """
    A logging filter that masks base64 strings in log messages.
    """
    BASE64_REGEX = re.compile(r'data:image/[a-zA-Z]+;base64,[A-Za-z0-9+/=]+')

    def filter(self, record):
        if record.msg:
            record.msg = self.BASE64_REGEX.sub('[BASE64 DATA OMITTED]', record.msg)
        return True

# Instantiate and add the filter to all handlers
mask_filter = MaskBase64Filter()
for handler in logger.handlers:
    handler.addFilter(mask_filter)

def timing(func):
    """
    Decorator to measure and log the execution time of functions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        logger.debug(f"Started '{func.__name__}'")
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logger.debug(f"Finished '{func.__name__}' in {elapsed_time:.4f} seconds")
        return result
    return wrapper