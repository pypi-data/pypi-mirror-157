import logging
import threading
from functools import wraps

logger = logging.getLogger()


def in_thread(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            logger.info('service exec in thread')
            t = threading.Thread(target=f, args=args, kwargs=kwargs)
            t.start()
        except Exception as e:
            logger.error("service exec has error.\n", exc_info=True)

    return wrapper
