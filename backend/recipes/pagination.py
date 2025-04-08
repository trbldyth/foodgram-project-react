from users.pagination import CustomPageNumberPagination
from rest_framework.response import Response


class CustomDataPagination(CustomPageNumberPagination):
    def get_paginated_response(self, data):
        return Response(data)
