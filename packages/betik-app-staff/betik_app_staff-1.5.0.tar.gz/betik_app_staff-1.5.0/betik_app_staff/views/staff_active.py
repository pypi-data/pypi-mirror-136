from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import ActiveReasonFilter, ActiveStaffLogFilter
from betik_app_staff.models import ActiveReasonModel, ActiveStaffLogModel
from betik_app_staff.serializers.staff_active import ActiveReasonSerializer, StaffSetActiveSerializer, \
    ActiveStaffLogSerializer
from betik_app_staff.serializers_merge import ActiveReasonMergeSerializer


class ActiveReasonCreateView(generics.CreateAPIView):
    """
        create a active reason

        create a active reason
    """
    queryset = ActiveReasonModel.objects.all()
    serializer_class = ActiveReasonSerializer


class ActiveReasonUpdateView(generics.UpdateAPIView):
    """
        update a active reason

        update a active reason
    """
    queryset = ActiveReasonModel.objects.all()
    serializer_class = ActiveReasonSerializer


class ActiveReasonDeleteView(generics.DestroyAPIView):
    """
        delete a active reason

        delete a active reason
    """
    queryset = ActiveReasonModel.objects.all()


class ActiveReasonMergeView(generics.UpdateAPIView):
    """
        merge a active reason

        merge a active reason
    """
    queryset = ActiveReasonModel.objects.all()
    serializer_class = ActiveReasonMergeSerializer


class ActiveReasonPaginateView(generics.ListAPIView):
    """
        paginate active reasons

        paginate active reasons
    """
    queryset = ActiveReasonModel.objects.all()
    serializer_class = ActiveReasonSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ActiveReasonFilter
    ordering_fields = ['explain']
    ordering = ['explain']


class StaffSetActiveView(generics.CreateAPIView):
    """
        set active a staff

        set active a staff
    """
    queryset = ActiveStaffLogModel.objects.all()
    serializer_class = StaffSetActiveSerializer


class ActiveStaffLogPaginateView(generics.ListAPIView):
    """
        paginate active staff logs

        paginate active staff logs
    """
    queryset = ActiveStaffLogModel.objects.all()
    serializer_class = ActiveStaffLogSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ActiveStaffLogFilter
    ordering_fields = [
        'staff__person__identity', 'staff__person__name', 'staff__person__last_name', 'staff__registration_number',
        'date', 'reason__explain'
    ]
    ordering = ['-date']
