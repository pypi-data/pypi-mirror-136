import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Max


class BankHolidayManager(models.Manager):
    def is_holiday(self, date):
        if isinstance(date, datetime.datetime):
            date = date.date()

        try:
            inst = self.filter(start_date__lte=date, finish_date__isnull=True).get()
        except ObjectDoesNotExist:
            try:
                inst = self.filter(start_date__lte=date, finish_date__gt=date).get()
            except ObjectDoesNotExist:
                inst = None

        return inst is not None and inst.day == date.day and inst.month == date.month


class HolidayManager(models.Manager):
    def is_holiday(self, date):
        if isinstance(date, datetime.datetime):
            date = date.date()

        try:
            inst = self.filter(start_date__lte=date, finish_date__isnull=True).get()
        except ObjectDoesNotExist:
            try:
                inst = self.filter(start_date__lte=date, finish_date__gt=date).get()
            except ObjectDoesNotExist:
                inst = None

        return inst is not None


class ShiftRuleManager(models.Manager):
    def filter_shift_rule_on_date_for_change(self, date):
        """
            verilen tarihdeki geçerli vardiya kurallarından, bu tarihde değişim zamanı gelenleri listeler
        """
        if isinstance(date, datetime.datetime):
            date = date.date()

        qs1 = self.filter(start_date__lte=date, finish_date__isnull=True, period_end_date__lte=date)
        qs2 = self.filter(start_date__lte=date, finish_date__gt=date, period_end_date__lte=date)

        return qs1 | qs2

    def get_shift_rule_on_date(self, date, staff):
        """
            personelin, verilen tarihdeki vardiya kuralını getirir
        """
        if isinstance(date, datetime.datetime):
            date = date.date()

        try:
            inst = self.filter(start_date__lte=date, finish_date__isnull=True, shift_staffs__staff=staff).get()
        except ObjectDoesNotExist:
            try:
                inst = self.filter(start_date__lte=date, finish_date__gt=date, shift_staffs__staff=staff).get()
            except ObjectDoesNotExist:
                inst = None

        return inst

    def get_max_date_in_all_records(self):
        """
            kayıtlar arasında en büyük bitiş vyea başlangıç tarihine sahip kayıt bulunur. Geriye o kaydın tarihi döner
        """
        max_dates = self.aggregate(max_value1=Max('finish_date'), max_value2=Max('start_date'))

        if max_dates:
            d1 = max_dates.get('max_value1')
            d2 = max_dates.get('max_value2')
            if d1 and d2:
                return max(d1, d2)
            elif d1:
                return d1
            elif d2:
                return d2

        return None


class BusinessDayManager(models.Manager):
    def get_business_rule_on_date(self, date, staff):
        """
            personelin, verilen tarihdeki iş günü kuralını getirir
        """
        if isinstance(date, datetime.datetime):
            date = date.date()

        try:
            inst = self.filter(start_date__lte=date, finish_date__isnull=True, staff_type=staff.staff_type).get()
        except ObjectDoesNotExist:
            try:
                inst = self.filter(start_date__lte=date, finish_date__gt=date, staff_type=staff.staff_type).get()
            except ObjectDoesNotExist:
                inst = None

        return inst

    def get_max_date_in_all_records(self):
        """
            kayıtlar arasında en büyük bitiş vyea başlangıç tarihine sahip kayıt bulunur. Geriye o kaydın tarihi döner
        """
        max_dates = self.aggregate(max_value1=Max('finish_date'), max_value2=Max('start_date'))

        if max_dates:
            d1 = max_dates.get('max_value1')
            d2 = max_dates.get('max_value2')
            if d1 and d2:
                return max(d1, d2)
            elif d1:
                return d1
            elif d2:
                return d2

        return None


class IndividualShiftManager(models.Manager):
    def list_business_day_on_date(self, date, staff):
        """
            personelin verilen tarihde, özel vardiyalarını döndürür
        """
        return list(self.filter(start_dt__date=date, staff=staff))

    def is_working_time(self, date_time, staff):
        """
            verilen tarih ve saatte mesai var mı?
        """
        working_days = self.list_business_day_on_date(date_time, staff)
        for working_date in working_days:
            if working_date.start_dt <= date_time < working_date.finish_dt:
                return True

        return False

    def get_max_date_in_all_records(self):
        """
            kayıtlar arasında en büyük bitiş tarihine sahip kayıt bulunur. Geriye o kaydın bitiş tarihi döner
        """
        ret_val = self.aggregate(max_value=Max('finish_dt__date'))
        if ret_val:
            max_date = ret_val.get('max_value')
            if max_date:
                return max_date.date()
        return None


class AnnualLeaveRuleManager(models.Manager):
    def get_rule_on_date(self, date, staff_type):
        """
            personel tipinin, verilen tarihdeki yıllık izin kuralını getirir
        """
        if isinstance(date, datetime.datetime):
            date = date.date()

        try:
            inst = self.filter(start_date__lte=date, finish_date__isnull=True, staff_type=staff_type).get()
        except ObjectDoesNotExist:
            try:
                inst = self.filter(start_date__lte=date, finish_date__gt=date, staff_type=staff_type).get()
            except ObjectDoesNotExist:
                inst = None

        return inst


class StaffLeaveManager(models.Manager):
    def filter_staff_leave_on_date_range(self, start_dt, finish_dt, staff):
        """
            personelin verilen tarihlerine denk gelen izinlerini getir
        """
        qs1 = self.filter(staff=staff, start_dt__lte=start_dt, finish_dt__gt=start_dt)
        qs2 = self.filter(staff=staff, start_dt__lte=finish_dt, finish_dt__gt=finish_dt)
        qs3 = self.filter(staff=staff, start_dt__gte=start_dt, finish_dt__lte=finish_dt)

        return qs1 | qs2 | qs3
