from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import PassiveReasonFilter, PassiveStaffLogFilter
from betik_app_staff.models import PassiveReasonModel, PassiveStaffLogModel
from betik_app_staff.serializers.staff_passive import PassiveReasonSerializer, StaffSetPassiveSerializer, \
    PassiveStaffLogSerializer
from betik_app_staff.serializers_merge import PassiveReasonMergeSerializer


class PassiveReasonCreateView(generics.CreateAPIView):
    """
        create a passive reason

        create a passive reason
    """
    queryset = PassiveReasonModel.objects.all()
    serializer_class = PassiveReasonSerializer


class PassiveReasonUpdateView(generics.UpdateAPIView):
    """
        update a passive reason

        update a passive reason
    """
    queryset = PassiveReasonModel.objects.all()
    serializer_class = PassiveReasonSerializer


class PassiveReasonDeleteView(generics.DestroyAPIView):
    """
        delete a passive reason

        delete a passive reason
    """
    queryset = PassiveReasonModel.objects.all()


class PassiveReasonMergeView(generics.UpdateAPIView):
    """
        merge a passive reason

        merge a passive reason
    """
    queryset = PassiveReasonModel.objects.all()
    serializer_class = PassiveReasonMergeSerializer


class PassiveReasonPaginateView(generics.ListAPIView):
    """
        paginate passive reasons

        paginate passive reasons
    """
    queryset = PassiveReasonModel.objects.all()
    serializer_class = PassiveReasonSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = PassiveReasonFilter
    ordering_fields = ['explain']
    ordering = ['explain']


class StaffSetPassiveView(generics.CreateAPIView):
    """
        set passive a staff

        set passive a staff
    """
    queryset = PassiveStaffLogModel.objects.all()
    serializer_class = StaffSetPassiveSerializer


class PassiveStaffLogPaginateView(generics.ListAPIView):
    """
        paginate passive staff logs

        paginate passive staff logs
    """
    queryset = PassiveStaffLogModel.objects.all()
    serializer_class = PassiveStaffLogSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = PassiveStaffLogFilter
    ordering_fields = [
        'staff__person__identity', 'staff__person__name', 'staff__person__last_name', 'staff__registration_number',
        'date', 'reason__explain'
    ]
    ordering = ['-date']
