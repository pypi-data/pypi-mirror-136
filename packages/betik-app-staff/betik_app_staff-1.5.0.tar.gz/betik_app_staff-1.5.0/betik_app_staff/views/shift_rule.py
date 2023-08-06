import datetime

from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from django.utils.translation import gettext_lazy as _
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema

from rest_framework.filters import OrderingFilter
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from betik_app_staff.filters import ShiftRuleFilter, ShiftRuleStaffFilter, StaffFilter
from betik_app_staff.models import ShiftRuleModel, IndividualShiftModel, BusinessDayModel, ShiftRuleStaffModel, \
    StaffModel
from betik_app_staff.serializers.shift_rule import ShiftRuleSerializer, ShiftRuleStaffSerializer, \
    StaffAssignToShiftRuleFromQuerySerializer
from betik_app_staff.validators import StaffBusinessDaysConflictValidator


class ShiftRuleCreateView(generics.CreateAPIView):
    """
        create a shift rule

        create a shift rule
    """
    queryset = ShiftRuleModel.objects.all()
    serializer_class = ShiftRuleSerializer


class ShiftRuleUpdateView(generics.UpdateAPIView):
    """
        update a shift rule

        update a shift rule
    """
    queryset = ShiftRuleModel.objects.all()
    serializer_class = ShiftRuleSerializer


class ShiftRuleDeleteView(generics.DestroyAPIView):
    """
        delete a shift rule

        delete a shift rule
    """
    queryset = ShiftRuleModel.objects.all()

    @transaction.atomic
    def perform_destroy(self, instance):
        today = datetime.datetime.today().date()

        # şu an aktif olan kayıt silinemez
        if instance.active:
            msg = _('active record can not be deleted')
            raise ValidationError({'detail': [msg]})

        # geçmiş kayıtlar silinemez
        if instance.finish_date and instance.finish_date <= today:
            msg = _('outdated record can not be deleted')
            raise ValidationError({'detail': [msg]})

        start_date = instance.start_date
        finish_date = instance.finish_date
        staffs = [item.staff for item in instance.shift_staffs.all()]

        super().perform_destroy(instance)

        # sildikden sonra mesai saati çakışmalarını kontrol et
        # kaydın başlangıç ve bitiş tarihi arasındaki çakışmalara bak
        # çıkış tarihi None ise sistemdeki en büyük tarihi al
        # en büyük tarih şu şekilde seçilir
        # kişisel vardiya, vardiya kuralı ve genel iş kurallarından en büyük tarih bulunur

        if finish_date is None:
            max_date1 = IndividualShiftModel.objects.get_max_date_in_all_records()
            max_date2 = BusinessDayModel.objects.get_max_date_in_all_records()
            max_date3 = ShiftRuleModel.objects.get_max_date_in_all_records()

            dates = [
                max_date1,
                max_date2,
                max_date3,
                finish_date
            ]
            dates = sorted(dates, key=lambda x: datetime.datetime.min.date() if x is None else x)
            try:
                finish_date = dates[-1:][0]
            except:
                finish_date = None

        if finish_date:
            if isinstance(finish_date, datetime.datetime):
                finish_date = finish_date.date()

            if today < finish_date:
                # başlama tarihi seçerken şuna dikkat edilmeli
                # kuralın başlama tarihi geçmiş olabilir, bu sebeple çakışmaları
                # geçmiş tarihde değil, yarından itibaren kontrol etmek gerekir
                tomorrow = today + datetime.timedelta(days=1)
                start_date = max(start_date, tomorrow)

                validator = StaffBusinessDaysConflictValidator(start_date, finish_date, staffs)
                validator.validate(raise_exception=True)


class ShiftRulePaginateView(generics.ListAPIView):
    """
        paginate shift rules

        paginate shift rules
    """

    queryset = ShiftRuleModel.objects.all()
    serializer_class = ShiftRuleSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ShiftRuleFilter
    ordering_fields = ['start_date', 'id']
    ordering = ['-start_date', '-id']


class BulkStaffAssignToShiftRuleView(generics.CreateAPIView):
    """
        bulk staff assign to shift rule

        bulk staff assign to shift rule
    """

    queryset = StaffModel.objects.all()
    serializer_class = StaffAssignToShiftRuleFromQuerySerializer
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

    @swagger_auto_schema(request_body=StaffAssignToShiftRuleFromQuerySerializer,
                         responses={202: StaffAssignToShiftRuleFromQuerySerializer})
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response


class ShiftRuleStaffPaginateView(generics.ListAPIView):
    """
        paginate staff in shift rules

        paginate staff in shift rules
    """

    queryset = ShiftRuleStaffModel.objects.all()
    serializer_class = ShiftRuleStaffSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ShiftRuleStaffFilter
    ordering_fields = ['shift_rule__start_date', 'staff__person__identity', 'staff__person__name',
                       'staff__person__last_name', 'staff__registration_number']
    ordering = ['shift_rule__start_date', 'staff__person__name', 'staff__person__last_name']


class StaffRemoveFromShiftView(generics.DestroyAPIView):
    """
        remove staff from the shift

        remove staff from the shift
    """
    queryset = ShiftRuleStaffModel.objects.all()

    def get_queryset(self):
        staff_id = self.kwargs['staff_id']
        shift_rule_id = self.kwargs['shift_rule_id']

        return super().get_queryset().filter(shift_rule=shift_rule_id, staff=staff_id)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    @transaction.atomic
    def perform_destroy(self, instance):
        today = datetime.datetime.today().date()

        # eski vardiyadan, personel çıkarılamaz
        if instance.shift_rule.expiry:
            msg = _('outdated record can not be deleted')
            raise ValidationError({'detail': [msg]})

        start_date = instance.shift_rule.start_date
        finish_date = instance.shift_rule.finish_date
        staffs = [instance.staff]

        super().perform_destroy(instance)

        # sildikden sonra mesai saati çakışmalarını kontrol et
        # kaydın başlangıç ve bitiş tarihi arasındaki çakışmalara bak
        # çıkış tarihi None ise sistemdeki en büyük tarihi al
        # en büyük tarih şu şekilde seçilir
        # kişisel vardiya, vardiya kuralı ve genel iş kurallarından en büyük tarih bulunur

        if finish_date is None:
            max_date1 = IndividualShiftModel.objects.get_max_date_in_all_records()
            max_date2 = BusinessDayModel.objects.get_max_date_in_all_records()
            max_date3 = ShiftRuleModel.objects.get_max_date_in_all_records()

            dates = [
                max_date1,
                max_date2,
                max_date3,
                finish_date
            ]
            dates = sorted(dates, key=lambda x: datetime.datetime.min.date() if x is None else x)
            try:
                finish_date = dates[-1:][0]
            except:
                finish_date = None

        if finish_date:
            if isinstance(finish_date, datetime.datetime):
                finish_date = finish_date.date()

            if today < finish_date:
                # başlama tarihi seçerken şuna dikkat edilmeli
                # kuralın başlama tarihi geçmiş olabilir, bu sebeple çakışmaları
                # geçmiş tarihde değil, yarından itibaren kontrol etmek gerekir
                tomorrow = today + datetime.timedelta(days=1)
                start_date = max(start_date, tomorrow)

                validator = StaffBusinessDaysConflictValidator(start_date, finish_date, staffs)
                validator.validate(raise_exception=True)
