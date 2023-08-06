from django.utils.translation import gettext as _
from drf_yasg.openapi import Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.response import Response

from betik_app_staff.enums import ShiftTypeEnum


class ShiftTypeListView(generics.ListAPIView):
    """
        list all shift types

        list all shift types
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        responses={
            200: Schema(type='array', items=Schema(type='object', properties={
                'code': Schema(title=_('Code'), type='string'),
                'exp': Schema(title=_('Explanation'), type='string')
            }))
        })
    def get(self, request, *args, **kwargs):
        type_list = ShiftTypeEnum.types
        new_list = []
        for item in type_list:
            new_list.append({'code': item[0], 'exp': item[1]})
        return Response(new_list)
