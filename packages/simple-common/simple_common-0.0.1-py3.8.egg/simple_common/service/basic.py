import logging
import time
from functools import wraps

from simple_common.service.resp import ServiceResp, SuccessResp, ErrorResp

error_logger = logging.getLogger("error")


def service_wrap(*wrap_args, **wrap_kwargs):
    service_name = wrap_kwargs.get('name', None)
    raise_error = wrap_kwargs.get('raise_error', False)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            try:

                start_time = time.time()

                resp = f(*args, **kwargs)

                end_time = time.time()

                print("Method: {} Time: {}s".format(f.__name__, (end_time - start_time)))

                if isinstance(resp, ServiceResp):
                    resp.service_name = service_name
                else:
                    resp = SuccessResp(data=resp, service_name=service_name)
            except Exception as e:

                error_logger.error("service exec has error.\n", exc_info=True)
                error_logger.error("service error is: ----- {}".format(str(e)))

                resp = ErrorResp(e, service_name=service_name,
                                 error_msg=str(e))

                if raise_error:
                    raise e
            return resp

        return wrapper

    return decorator
