from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import DismissReasonFilter, DismissStaffLogFilter
from betik_app_staff.models import DismissReasonModel, DismissStaffLogModel
from betik_app_staff.serializers.staff_dismiss import DismissReasonSerializer, StaffSetDismissSerializer, \
    DismissStaffLogSerializer
from betik_app_staff.serializers_merge import DismissReasonMergeSerializer


class DismissReasonCreateView(generics.CreateAPIView):
    """
        create a dismiss reason

        create a dismiss reason
    """
    queryset = DismissReasonModel.objects.all()
    serializer_class = DismissReasonSerializer


class DismissReasonUpdateView(generics.UpdateAPIView):
    """
        update a dismiss reason

        update a dismiss reason
    """
    queryset = DismissReasonModel.objects.all()
    serializer_class = DismissReasonSerializer


class DismissReasonDeleteView(generics.DestroyAPIView):
    """
        delete a dismiss reason

        delete a dismiss reason
    """
    queryset = DismissReasonModel.objects.all()


class DismissReasonPaginateView(generics.ListAPIView):
    """
        paginate dismiss reasons

        paginate dismiss reasons
    """
    queryset = DismissReasonModel.objects.all()
    serializer_class = DismissReasonSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = DismissReasonFilter
    ordering_fields = ['explain']
    ordering = ['explain']


class DismissReasonMergeView(generics.UpdateAPIView):
    """
        merge a dismiss reason

        merge a dismiss reason
    """
    queryset = DismissReasonModel.objects.all()
    serializer_class = DismissReasonMergeSerializer


class StaffSetDismissView(generics.CreateAPIView):
    """
        set dismiss a staff

        set dismiss a staff
    """
    queryset = DismissStaffLogModel.objects.all()
    serializer_class = StaffSetDismissSerializer


class DismissStaffLogPaginateView(generics.ListAPIView):
    """
        paginate dismiss staff logs

        paginate dismiss staff logs
    """
    queryset = DismissStaffLogModel.objects.all()
    serializer_class = DismissStaffLogSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = DismissStaffLogFilter
    ordering_fields = [
        'staff__person__identity', 'staff__person__name', 'staff__person__last_name', 'staff__registration_number',
        'date', 'reason__explain'
    ]
    ordering = ['-date']
