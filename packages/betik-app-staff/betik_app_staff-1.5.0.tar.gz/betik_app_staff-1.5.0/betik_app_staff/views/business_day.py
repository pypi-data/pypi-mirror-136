import datetime

from django_filters.rest_framework import DjangoFilterBackend

from django.utils.translation import gettext_lazy as _
from django.db import transaction

from rest_framework.filters import OrderingFilter
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from betik_app_util.paginations import StandardPagination
from betik_app_staff.filters import BusinessDayFilter
from betik_app_staff.models import BusinessDayModel, IndividualShiftModel, ShiftRuleModel, StaffModel
from betik_app_staff.serializers.business_day import BusinessDaySerializer
from betik_app_staff.validators import StaffBusinessDaysConflictValidator


class BusinessDayCreateView(generics.CreateAPIView):
    """
        create a business day

        create a business day
    """
    queryset = BusinessDayModel.objects.all()
    serializer_class = BusinessDaySerializer


class BusinessDayUpdateView(generics.UpdateAPIView):
    """
        update a business day

        update a business day
    """
    queryset = BusinessDayModel.objects.all()
    serializer_class = BusinessDaySerializer


class BusinessDayDeleteView(generics.DestroyAPIView):
    """
        delete a business day

        delete a business day
    """
    queryset = BusinessDayModel.objects.all()

    @transaction.atomic
    def perform_destroy(self, instance):
        today = datetime.datetime.today().date()
        start_date = instance.start_date
        finish_date = instance.finish_date
        staff_type = instance.staff_type

        # şu an aktif olan kayıt silinemez
        if instance.active:
            msg = _('active record can not be deleted')
            raise ValidationError({'detail': [msg]})

        # geçmiş kayıtlar silinemez
        if instance.finish_date and instance.finish_date <= today:
            msg = _('outdated record can not be deleted')
            raise ValidationError({'detail': [msg]})

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

                staffs = StaffModel.objects.filter(staff_type=staff_type)
                validator = StaffBusinessDaysConflictValidator(start_date, finish_date, staffs)
                validator.validate(raise_exception=True)


class BusinessDayPaginateView(generics.ListAPIView):
    """
        paginate business days

        paginate business day
    """
    queryset = BusinessDayModel.objects.all()
    serializer_class = BusinessDaySerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = BusinessDayFilter
    ordering_fields = ['staff_type']
    ordering = ['staff_type']
