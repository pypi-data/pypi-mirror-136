from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import WorkingHourFilter
from betik_app_staff.models import WorkingHourModel
from betik_app_staff.serializers.working_hour import WorkingHourSerializer


class AbsenteePaginateOnDateView(generics.ListAPIView):
    """
        paginate absentee staff on date

        paginate absentee staff on date
    """

    queryset = WorkingHourModel.objects.all()
    serializer_class = WorkingHourSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = WorkingHourFilter
    ordering_fields = ['start_dt', 'finish_dt', 'staff__person__identity', 'staff__person__name',
                       'staff__person__last_name', 'staff__registration_number']
    ordering = ['-start_dt', 'staff__person__name', 'staff__person__last_name']

    def get_queryset(self):
        date = self.kwargs.get('date')

        qs = super().get_queryset().filter(in_dt__isnull=True, start_dt__date=date)

        return qs


class LatePaginateOnDateView(generics.ListAPIView):
    """
        paginate late staff on date

        paginate late staff on date
    """

    queryset = WorkingHourModel.objects.all()
    serializer_class = WorkingHourSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = WorkingHourFilter
    ordering_fields = [
        'start_dt', 'finish_dt', 'late_minute', 'staff__person__identity', 'staff__person__name',
        'staff__person__last_name', 'staff__registration_number'
    ]
    ordering = [
        '-start_dt', 'late_minute', 'staff__person__name', 'staff__person__last_name'
    ]

    def get_queryset(self):
        date = self.kwargs.get('date')

        qs = super().get_queryset().filter(late_minute__isnull=False, start_dt__date=date)

        return qs
