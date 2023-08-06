import json
from rest_framework.request import Request
from django.http import JsonResponse
from django.http.request import HttpRequest as DjangoHttpRequest
from django.http import QueryDict

result = dict()
result_arr = []


def get_params(request, *args, **kwargs):
    """
    django rest framework 的request 多了一个data,各种请求方式的参数都会在里面
    :param request:
    :param args:
    :param kwargs:
    :return:
    """

    content_type = getattr(request, 'content_type', None)
    method = request.method

    # django request
    if isinstance(request, DjangoHttpRequest):
        if method == 'GET':
            return request.GET
        if method == 'POST':
            if content_type == 'application/json':
                return json.loads(request.body.decode())
            else:
                return request.POST

    # django rest framework request
    if isinstance(request, Request):

        query_params = request.query_params
        if isinstance(query_params, QueryDict):
            query_params = query_params.dict()
        result_data = request.data
        if isinstance(result_data, QueryDict):
            result_data = result_data.dict()

        if query_params != {}:
            return query_params
        else:
            return result_data


class SuccessJsonResponse(JsonResponse):

    def __init__(self, data):
        _data = dict(data=data,
                     error=None,
                     success=True,
                     error_msg=None)
        super().__init__(data=_data)
