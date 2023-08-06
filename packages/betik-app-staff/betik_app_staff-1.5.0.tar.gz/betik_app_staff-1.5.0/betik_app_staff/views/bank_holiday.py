from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import BankHolidayFilter
from betik_app_staff.models import BankHolidayModel
from betik_app_staff.serializers.bank_holiday import BankHolidaySerializer


class BankHolidayCreateView(generics.CreateAPIView):
    """
        create a bank holiday

        create a bank holiday
    """
    queryset = BankHolidayModel.objects.all()
    serializer_class = BankHolidaySerializer


class BankHolidayUpdateView(generics.UpdateAPIView):
    """
        update a bank holiday

        update a bank holiday
    """
    queryset = BankHolidayModel.objects.all()
    serializer_class = BankHolidaySerializer


class BankHolidayDeleteView(generics.DestroyAPIView):
    """
        delete a bank holiday

        delete a bank holiday
    """
    queryset = BankHolidayModel.objects.all()


class BankHolidayPaginateView(generics.ListAPIView):
    """
        paginate bank holidays

        paginate bank holidays
    """
    queryset = BankHolidayModel.objects.all()
    serializer_class = BankHolidaySerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = BankHolidayFilter
    ordering_fields = ['name']
    ordering = ['name']
