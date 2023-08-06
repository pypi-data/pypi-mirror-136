from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext as _

from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import LeaveTypeFilter
from betik_app_staff.models import LeaveTypeModel
from betik_app_staff.serializers.staff_leave import LeaveTypeSerializer
from betik_app_util.paginations import StandardPagination


class LeaveTypePaginateView(generics.ListAPIView):
    """
        paginate leave types

        paginate leave types
    """

    queryset = LeaveTypeModel.objects.all()
    serializer_class = LeaveTypeSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = LeaveTypeFilter
    ordering_fields = ['type']
    ordering = ['type']


class LeaveTypeCreateView(generics.CreateAPIView):
    """
        create a leave type

        create a leave type
    """
    queryset = LeaveTypeModel.objects.all()
    serializer_class = LeaveTypeSerializer


class LeaveTypeUpdateView(generics.UpdateAPIView):
    """
        update a leave type

        update a leave type
    """
    queryset = LeaveTypeModel.objects.all()
    serializer_class = LeaveTypeSerializer


class LeaveTypeDeleteView(generics.DestroyAPIView):
    """
        delete a leave type

        delete a leave type
    """
    queryset = LeaveTypeModel.objects.all()

    def perform_destroy(self, instance):
        if instance.code:
            msg = _('This leave type can not be deleted')
            raise ValidationError({'detail': msg})

        super().perform_destroy(instance)
