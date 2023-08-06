import logging
import uuid
from functools import wraps

logger = logging.getLogger('api')


class ServiceResp(object):
    def __init__(self, data, error, success, **kwargs):
        self.uid = uuid.uuid4().hex
        self.data = data
        self.error = error
        self.success = success
        # status_code 默认为-1, 表明未设置具体的状态码
        self.status_code = kwargs.get('status_code', -1)
        self.operation_name = kwargs.get('operation_name', None)
        self.error_msg = kwargs.get('error_msg', None)

    def get_msg(self):
        return self.error_msg

    def get_dict(self):
        return dict(data=self.data,
                    error=str(self.error),
                    success=self.success,
                    status_code=self.status_code,
                    error_msg=self.error_msg)

    def json(self):
        if hasattr(self.data, 'as_json'):
            return dict(data=self.data.as_json(),
                        error=str(self.error),
                        success=self.success,
                        status_code=self.status_code,
                        error_msg=self.error_msg)
        else:
            return dict(data=self.data,
                        error=str(self.error),
                        success=self.success,
                        status_code=self.status_code,
                        error_msg=self.error_msg)


class SuccessResp(ServiceResp):
    def __init__(self, data, **kwargs):
        super().__init__(data=data, error=None, success=True, **kwargs)


class ErrorResp(ServiceResp):
    def __init__(self, error, **kwargs):
        super().__init__(data=None, error=error, success=False, **kwargs)


def service_wrap(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        service_resp = ErrorResp(None)
        try:

            resp = f(*args, **kwargs)
            if isinstance(resp, ServiceResp):
                service_resp = resp
            elif isinstance(resp, ErrorResp):
                # error_resp 不处理
                pass
            else:
                service_resp = SuccessResp(data=resp)
        except Exception as e:
            logger.error('service wrap catch error', exc_info=True)
            if e.__dict__.get('code', None):
                service_resp = ErrorResp(e, error_msg=str(e), status_code=e.code)
            else:
                service_resp = ErrorResp(e, error_msg=str(e))
        finally:
            return service_resp

    return wrapper
