import datetime
from copy import copy

from dateutil.relativedelta import relativedelta

from django.utils.translation import gettext_lazy as _

from betik_app_staff.enums import LeaveDurationTypeEnum
from betik_app_staff.models import HolidayModel, BankHolidayModel, BusinessDayModel, IndividualShiftModel, \
    ShiftRuleModel, AnnualLeaveRuleModel


def leave_calculate(staff, start_dt, duration, duration_type):
    """
        izin bitiş tarihini ve işe dönüş tarihini hesaplar
    """
    if duration_type == LeaveDurationTypeEnum.HOUR:
        finish_dt = start_dt + datetime.timedelta(hours=duration)
    elif duration_type == LeaveDurationTypeEnum.DAY:
        finish_dt = start_dt + datetime.timedelta(days=duration)
    elif duration_type == LeaveDurationTypeEnum.WEEK:
        finish_dt = start_dt + datetime.timedelta(weeks=duration)
    elif duration_type == LeaveDurationTypeEnum.MONTH:
        finish_dt = start_dt + relativedelta(months=duration)
    elif duration_type == LeaveDurationTypeEnum.YEAR:
        finish_dt = start_dt + relativedelta(years=duration)
    elif duration_type == LeaveDurationTypeEnum.BUSINESS_DAY:
        # iş gününe göre hesaplanacak
        finish_dt = _get_finish_date_for_business_day(start_dt, duration, staff)
    else:
        msg = _('%(duration_type)s duration type not found') % {
            'duration_type': duration_type
        }
        raise Exception(msg)

    # izinden sonra işe başlama tarihini bul
    current_dt = copy(finish_dt)
    while True:
        is_holiday = HolidayModel.objects.is_holiday(current_dt)
        is_bank_holiday = BankHolidayModel.objects.is_holiday(current_dt)

        if not is_holiday or not is_bank_holiday:
            # özel vardiyasına göre işe başlama tarih ve saatini bul
            is_working_time = IndividualShiftModel.objects.is_working_time(current_dt, staff)
            if is_working_time:
                break

            # vardiya sistemine göre işe başlama tarih ve saatini bul
            rule = ShiftRuleModel.objects.get_shift_rule_on_date(current_dt, staff)
            if rule:
                is_working_time = rule.is_working_time(current_dt, staff)
                if is_working_time:
                    break

            if not rule:
                # genel iş kuralına göre işe başlama tarih ve saatini bul
                rule = BusinessDayModel.objects.get_business_rule_on_date(current_dt, staff)
                if rule:
                    is_working_time = rule.is_working_time(current_dt)
                    if is_working_time:
                        break
                else:
                    msg = _('Working hours were not determined for the %(staff_type)s on %(date)s') % {
                        'staff_type': staff.staff_type.name,
                        'date': current_dt.strftime('%d %B %Y')
                    }
                    raise Exception(msg)

        current_dt += datetime.timedelta(minutes=15)

    work_start_dt = copy(current_dt)

    return {'work_start_dt': work_start_dt, 'finish_dt': finish_dt}


def get_annual_leave_right_of_leave(start_date, staff):
    """
        izin istenilen tarihde, bu personel tipi için belirlenmiş izin hakkını getir
    """
    if isinstance(start_date, datetime.datetime):
        start_date = start_date.date()

    rule = AnnualLeaveRuleModel.objects.get_rule_on_date(start_date, staff.staff_type)
    if not rule:
        msg = _('Annual leave rule were not determined for the %(staff_type)s on %(date)s') % {
            'staff_type': staff.staff_type.name,
            'date': start_date.strftime('%d %B %Y')
        }
        raise Exception(msg)

    # personelin işe giriş tarihini al
    staff_start_date = staff.start_date

    # giriş tarihinden, izin başlangıç tarihine kadar kaç yıl geçmiş
    date_diff = relativedelta(start_date, staff_start_date)
    working_year = date_diff.years
    working_year = 0 if working_year is None else working_year

    # kaç gün izin hakkı olduğunu bul
    right_of_leave = rule.get_duration_for_working_year(working_year)
    if right_of_leave == 0:
        msg = _(
            'Considering the date of employment of the staff, they have not yet obtained the right to take annual leave.')
        raise Exception(msg)

    return right_of_leave


def _get_finish_date_for_business_day(start_dt, duration, staff):
    """
        verilen tarihde başlayıp, [duration] kadar iş günü tatili için bitiş tarihini hesapla
        iş günü hesaplamak için tatiller ve genel iş kuralı baz alınır
    """
    current_duration = 0
    current_date = copy(start_dt)

    while current_duration < duration:
        is_holiday = HolidayModel.objects.is_holiday(current_date)
        is_bank_holiday = BankHolidayModel.objects.is_holiday(current_date)

        if not is_holiday or not is_bank_holiday:
            rule = BusinessDayModel.objects.get_business_rule_on_date(current_date, staff)
            if rule:
                day = rule.get_business_day_on_date(current_date)
                if day:
                    # çalışma günü
                    current_duration += 1
            else:
                msg = _('Working hours were not determined for the %(staff_type)s on %(date)s') % {
                    'staff_type': staff.staff_type.name,
                    'date': current_date.strftime('%d %B %Y')
                }
                raise Exception(msg)

        current_date += datetime.timedelta(days=1)

    finish_dt = copy(current_date)

    return finish_dt
