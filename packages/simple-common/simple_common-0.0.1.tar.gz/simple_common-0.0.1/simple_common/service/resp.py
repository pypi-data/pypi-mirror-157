import uuid


class ServiceResp(object):
    def __init__(self, data, error, success, **kwargs):
        self.uid = uuid.uuid4().hex
        self.data = data
        self.error = error
        self.success = success
        self.msg = kwargs.get('msg', None)
        self.service_name = kwargs.get('service_name', None)
        self.error_msg = kwargs.get('error_msg', None)

    def dict(self):
        if not (isinstance(self.data, dict) or isinstance(self.data, list)):
            self.data = None

        return dict(data=self.data,
                    error=str(self.error),
                    success=self.success,
                    msg=self.msg,
                    error_msg=self.error_msg)

    def json(self):
        if hasattr(self.data, 'as_json'):
            return dict(data=self.data.as_json(),
                        error=str(self.error),
                        success=self.success,
                        error_msg=self.error_msg)
        else:
            if not (isinstance(self.data, dict) or isinstance(self.data, list)):
                self.data = None
            return dict(data=self.data,
                        error=str(self.error),
                        success=self.success,
                        error_msg=self.error_msg)

    def ok(self):
        return self.success


class SuccessResp(ServiceResp):
    def __init__(self, data, **kwargs):
        super().__init__(data=data, error=None, success=True, **kwargs)


class ErrorResp(ServiceResp):

    def __init__(self, error, **kwargs):
        super().__init__(data=None, error=error, success=False, **kwargs)

    def get_msg(self):
        return str(self.error)
