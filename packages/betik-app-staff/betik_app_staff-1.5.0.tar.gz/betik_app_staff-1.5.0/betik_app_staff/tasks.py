import datetime

from betik_app_acs.enums import UsingModuleEnum
from betik_app_acs.models import PersonDeviceLogModel
from celery import shared_task
from dateutil.relativedelta import relativedelta

from django.db import transaction
from django.db.models import F, Q

from betik_app_staff.enums import ShiftTypeEnum
from betik_app_staff.models import ShiftRuleModel, StaffModel, IndividualShiftModel, WorkingHourModel
from betik_app_staff.working_day import find_working_hour_in_date


@shared_task
def change_shift_period_and_apply_working_hours():
    with transaction.atomic():
        change_shift_period()
        apply_working_hours()


@shared_task
def change_shift_period():
    """
        should be run once every day at 00:00
    """
    today = datetime.datetime.today().date()

    qs_shift_rule = ShiftRuleModel.objects.filter_shift_rule_on_date_for_change(today)

    with transaction.atomic():
        for inst_shift_rule in qs_shift_rule:
            # periyot tarihlerini kaydır

            inst_shift_rule.period_start_date = inst_shift_rule.period_end_date
            inst_shift_rule.period_end_date += datetime.timedelta(weeks=inst_shift_rule.period_duration)
            inst_shift_rule.save()

            # vardiyaya bağlı personelleri kaydır
            max_shift_no = len(inst_shift_rule.business_days)

            # her bir vardiya, bir sonraki vardiyaya geçicek
            inst_shift_rule.shift_staffs.update(shift_no=F('shift_no') + 1)

            # en son vardiya, 1 nolu vardiyaya geçicek
            # her bir vardiya, bir sonrakine kaydırıldığı için, son vardiya numarası,
            # max vardiya numarasından +1 fazla olur. Bu fazla olan vardiyalar, 1 nolu vardiyaya kaydırılmalı
            inst_shift_rule.shift_staffs.filter(shift_no=max_shift_no + 1).update(shift_no=1)


@shared_task
def apply_working_hours():
    today = datetime.datetime.today().date()

    # aktif personelleri ve bugün izinli olmayanları al
    qs_staff = StaffModel.objects.filter(finish_date__isnull=True).exclude(leaves__start_dt__date__lte=today,
                                                                           leaves__finish_dt__date__gt=today)

    with transaction.atomic():
        for inst_staff in qs_staff:
            working_hours = find_working_hour_in_date(today, inst_staff)
            for working_hour in working_hours:

                shift_type = ShiftTypeEnum.NORMAL
                if isinstance(working_hour['_instance'], IndividualShiftModel):
                    shift_type = working_hour['_instance'].type

                WorkingHourModel.objects.create(
                    start_dt=working_hour['start_dt'],
                    finish_dt=working_hour['finish_dt'],
                    work_hour=working_hour['work_hour'],
                    type=shift_type,
                    staff=inst_staff
                )


@shared_task
def find_in_out_times():
    """
        mesaisi olupda, giriş-çıkış saatleri belirlenmemiş personellrin giriş-çıkış saatlerini tespit eder.
        Aynı gün içinde birden fazla mesai varsa, her mesainin ayrı ayrı giriş-çıkış saatini tespit et. Eğer
        mesaisine geç geldiyse, ne kadar geciktiğini dakika cinsinden hesaplayıp kaydet.
        Örneğin sabah normal mesaiden sonra, personelin fazla mesaisi olabilir

        mesai saatleri aranırken, en fazla 2 hafta öncesinden bugüne bakılır

        Bu task saate bir çalıştırılmalı
    """
    limit = datetime.datetime.today().date() - datetime.timedelta(weeks=2)

    list_working_hour = WorkingHourModel.objects. \
        filter(Q(in_dt__isnull=True) | Q(out_dt__isnull=True)). \
        filter(start_dt__date__gte=limit)

    for working_hour in list_working_hour:
        # giriş saati yoksa, bul
        if working_hour.in_dt is None:
            in_time = _get_device_log(working_hour.staff, working_hour.start_dt, 1)
            if in_time:
                working_hour.in_dt = in_time

                if in_time > working_hour.start_dt:
                    diff_time = relativedelta(in_time, working_hour.start_dt)
                    late_minute = diff_time.minutes
                    working_hour.late_minute = late_minute

                working_hour.save()

        # çıkış saati yoksa, bul
        if working_hour.out_dt is None:
            out_time = _get_device_log(working_hour.staff, working_hour.finish_dt, 0)
            if out_time:
                working_hour.out_dt = out_time
                working_hour.save()


def _get_device_log(staff, time, in_out) -> [datetime.datetime, None]:
    """
        in=1
        out=0
    """
    time_before_1_hour = time - datetime.timedelta(hours=1)
    time_after_1_hour = time + datetime.timedelta(hours=1)

    # eğer giriş için saat talep ediliyorsa, istenen zamandan bir saat öncesine kadar bakılır.
    # aralarından en büyük olan alınır. Eğer 1 saat öncesinden kayıt yoksa, 1 saat sonrasına bakılır.
    # burada da aralarından en küçük olan alınır

    # eğer çıkış için saat talep ediliyorsa, istenen zamandan bir saat sonrasına kadar bakılır.
    # aralarından en küçük olan alınır. Eğer 1 saat sonrasından kayıt yoksa, 1 saat öncesine bakılır.
    # burada da aralarından en büyük olan alınır

    if in_out == 1:
        try:
            inst_person_log = PersonDeviceLogModel.objects.filter(
                device_module=UsingModuleEnum.STAFF,
                time__gte=time_before_1_hour,
                time__lte=time,
                person=staff.person
            ).order_by('-time')[:1].get()

            return inst_person_log.time
        except PersonDeviceLogModel.DoesNotExist:
            try:
                inst_person_log = PersonDeviceLogModel.objects.filter(
                    device_module=UsingModuleEnum.STAFF,
                    time__gte=time,
                    time__lte=time_after_1_hour,
                    person=staff.person
                ).order_by('time')[:1].get()

                return inst_person_log.time
            except PersonDeviceLogModel.DoesNotExist:
                return None
    else:
        try:
            inst_person_log = PersonDeviceLogModel.objects.filter(
                device_module=UsingModuleEnum.STAFF,
                time__gte=time,
                time__lte=time_after_1_hour,
                person=staff.person
            ).order_by('time')[:1].get()

            return inst_person_log.time
        except PersonDeviceLogModel.DoesNotExist:
            try:
                inst_person_log = PersonDeviceLogModel.objects.filter(
                    device_module=UsingModuleEnum.STAFF,
                    time__lte=time,
                    time__gte=time_before_1_hour,
                    person=staff.person
                ).order_by('-time')[:1].get()

                return inst_person_log.time
            except PersonDeviceLogModel.DoesNotExist:
                return None
