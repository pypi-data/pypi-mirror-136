import datetime

from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from django.utils.translation import gettext_lazy as _
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema

from rest_framework.filters import OrderingFilter
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError

from betik_app_staff.filters import StaffFilter, IndividualShiftStaffFilter
from betik_app_staff.models import StaffModel, IndividualShiftModel
from betik_app_staff.serializers.custom_shift import CustomShiftCreateBulkSerializer, CustomShiftSerializer
from betik_app_staff.validators import StaffBusinessDaysConflictValidator


class CustomShiftCreateBulkView(generics.CreateAPIView):
    """
        multi staff individual shift

        multi staff individual shift
    """

    queryset = StaffModel.objects.all()
    serializer_class = CustomShiftCreateBulkSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = StaffFilter
    ordering_fields = ['person__identity', 'person__name', 'person__last_name', 'registration_number', 'start_date',
                       'status']
    ordering = ['-registration_number']

    def get_queryset(self):
        return super().get_queryset().select_related('person')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['target_query'] = self.filter_queryset(self.get_queryset())
        return context

    @swagger_auto_schema(request_body=CustomShiftCreateBulkSerializer,
                         responses={202: CustomShiftCreateBulkSerializer})
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response


class CustomShiftDeleteView(generics.DestroyAPIView):
    """
        delete staff individual shift

        delete staff individual shift
    """

    queryset = IndividualShiftModel.objects.all()

    @transaction.atomic
    def perform_destroy(self, instance):
        # yarından itibaren başlayacak olanlar silinsin
        today = datetime.datetime.today().date()
        if instance.start_dt.date() <= today:
            tomorrow = today + datetime.timedelta(days=1)
            msg = _('Those before %(date)s cannot be deleted') % {
                'date': tomorrow.strftime("%d %B %Y")
            }
            raise ValidationError({'detail': [msg]})

        start_date = instance.start_dt
        finish_date = instance.finish_dt
        staffs = [instance.staff]

        super().perform_destroy(instance)

        # özel vardiya silindikden sonra tarih çakışmalarını kontrol et
        validator = StaffBusinessDaysConflictValidator(start_date, finish_date, staffs)
        validator.validate(raise_exception=True)


class CustomShiftPaginateView(generics.ListAPIView):
    """
        paginate staff in individual shift rules

        paginate staff in individual shift rules
    """

    queryset = IndividualShiftModel.objects.all()
    serializer_class = CustomShiftSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = IndividualShiftStaffFilter
    ordering_fields = ['start_dt', 'finish_dt', 'staff__person__identity', 'staff__person__name',
                       'staff__person__last_name', 'staff__registration_number']
    ordering = ['-start_dt', 'staff__person__name', 'staff__person__last_name']

    def get_queryset(self):
        qs = super().get_queryset()

        start_dt_gte = self.kwargs.get('start_dt_gte')
        start_dt_lte = self.kwargs.get('start_dt_lte')
        qs = qs.filter(start_dt__gte=start_dt_gte)
        if start_dt_lte:
            qs = qs.filter(start_dt__lte=start_dt_lte)

        return qs
