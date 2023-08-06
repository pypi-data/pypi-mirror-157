from rest_framework import generics
from rest_framework.response import Response


class BaseViewMixin(generics.GenericAPIView):
    def get_serializer_date(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.data

    def get_list_serializer(self, *args, **kwargs):
        if getattr(self, 'list_serializer_class', None):
            serializer_class = self.list_serializer_class
        else:
            serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_list_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_list_serializer(queryset, many=True)
        return Response(serializer.data)
