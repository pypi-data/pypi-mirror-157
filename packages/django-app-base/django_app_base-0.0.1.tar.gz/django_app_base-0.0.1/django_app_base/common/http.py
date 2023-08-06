from django.http import JsonResponse


class SuccessJsonResponse(JsonResponse):

    def __init__(self, data):
        _data = dict(data=data,
                     error=None,
                     success=True,
                     error_msg=None)
        super().__init__(data=_data)
