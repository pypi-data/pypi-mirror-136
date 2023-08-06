from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from betik_app_staff.filters import HolidayFilter
from betik_app_staff.models import HolidayModel
from betik_app_staff.serializers.holiday import HolidaySerializer


class HolidayCreateView(generics.CreateAPIView):
    """
        create a holiday

        create a holiday
    """
    queryset = HolidayModel.objects.all()
    serializer_class = HolidaySerializer


class HolidayUpdateView(generics.UpdateAPIView):
    """
        update a holiday

        update a holiday
    """
    queryset = HolidayModel.objects.all()
    serializer_class = HolidaySerializer


class HolidayDeleteView(generics.DestroyAPIView):
    """
        delete a holiday

        delete a holiday
    """
    queryset = HolidayModel.objects.all()


class HolidayPaginateView(generics.ListAPIView):
    """
        paginate holidays

        paginate holidays
    """
    queryset = HolidayModel.objects.all()
    serializer_class = HolidaySerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = HolidayFilter
    ordering_fields = ['name', 'start_date']
    ordering = ['-start_date', 'name']
