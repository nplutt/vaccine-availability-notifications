from functools import wraps
import time

from chalicelib.logs.utils import get_logger, CURRENT_REQUEST_ID


logger = get_logger(__name__)


def set_request_id(func):
    def wrapper(event, context):
        CURRENT_REQUEST_ID.set_request_id(context.aws_request_id)
        return func(event, context)
    return wrapper


def func_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        function_time_ms = (time.time() - start) * 1000
        logger.info('Function time', extra={
            'time': function_time_ms,
            'function_name': func.__name__,
        })
        return result
    return wrapper
