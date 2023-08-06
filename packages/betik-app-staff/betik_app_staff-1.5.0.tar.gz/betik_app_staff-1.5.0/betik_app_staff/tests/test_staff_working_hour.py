import datetime

from betik_app_acs.enums import UsingModuleEnum
from betik_app_acs.models import PersonDeviceLogModel
from django.urls import reverse
from freezegun import freeze_time

from betik_app_staff.enums import ShiftTypeEnum
from betik_app_staff.models import WorkingHourModel, ShiftRuleStaffModel
from betik_app_staff.serializers.working_hour import WorkingHourSerializer
from betik_app_staff.tasks import apply_working_hours, find_in_out_times
from betik_app_staff.tests.base import TestBase


@freeze_time("2021-12-06")
class TestApplyBusinessDay(TestBase):

    def test_normal_working_hour(self):
        """
            normal mesai
        """
        today = datetime.datetime.today().date()

        inst_business_day = self._create_business_day()
        inst_business_day.start_date = today - datetime.timedelta(weeks=20)
        inst_business_day.finish_date = None
        inst_business_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.wednesday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.thursday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.friday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.saturday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.save()

        inst_staff = self._create_staff()
        inst_staff.staff_type = inst_business_day.staff_type
        inst_staff.save()

        apply_working_hours()

        inst_working_hour = WorkingHourModel.objects.get(staff=inst_staff)
        start_dt = datetime.datetime(2021, 12, 6, 9, 0)
        finish_dt = start_dt + datetime.timedelta(hours=8)
        self.assertEqual(start_dt, inst_working_hour.start_dt)
        self.assertEqual(finish_dt, inst_working_hour.finish_dt)
        self.assertEqual(ShiftTypeEnum.NORMAL, inst_working_hour.type)

    def test_no_normal_work_on_a_holiday(self):
        """
            tatil günü normal mesai olmaması lazım
        """
        today = datetime.datetime.today().date()

        inst_holiday = self._create_holiday()
        inst_holiday.start_date = today - datetime.timedelta(days=1)
        inst_holiday.finish_date = today + datetime.timedelta(days=1)
        inst_holiday.save()

        inst_business_day = self._create_business_day()
        inst_business_day.start_date = today - datetime.timedelta(weeks=20)
        inst_business_day.finish_date = None
        inst_business_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.wednesday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.thursday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.friday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.saturday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.save()

        inst_staff = self._create_staff()
        inst_staff.staff_type = inst_business_day.staff_type
        inst_staff.save()

        apply_working_hours()

        count = WorkingHourModel.objects.count()
        self.assertEqual(0, count)

    def test_no_normal_work_on_a_bank_holiday(self):
        """
            resmi tatil günü normal mesai olmaması lazım
        """
        today = datetime.datetime.today().date()

        inst_holiday = self._create_bank_holiday()
        inst_holiday.start_date = today - datetime.timedelta(days=1)
        inst_holiday.finish_date = today + datetime.timedelta(days=1)
        inst_holiday.month = 12
        inst_holiday.day = 6
        inst_holiday.save()

        inst_business_day = self._create_business_day()
        inst_business_day.start_date = today - datetime.timedelta(weeks=20)
        inst_business_day.finish_date = None
        inst_business_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.wednesday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.thursday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.friday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.saturday = {'start_time': '09:00', 'work_hour': 8}
        inst_business_day.save()

        inst_staff = self._create_staff()
        inst_staff.staff_type = inst_business_day.staff_type
        inst_staff.save()

        apply_working_hours()

        count = WorkingHourModel.objects.count()
        self.assertEqual(0, count)


@freeze_time("2021-12-06")
class TestApplyShiftRule(TestBase):
    def test_shift_working_hour(self):
        """
            vardiya mesaisi
        """
        today = datetime.datetime.today().date()

        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.start_date = today - datetime.timedelta(weeks=20)
        inst_shift_rule.finish_date = None
        inst_shift_rule.period_start_date = inst_shift_rule.start_date
        inst_shift_rule.period_end_date = inst_shift_rule.period_start_date + datetime.timedelta(
            weeks=inst_shift_rule.period_duration)
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '23:00', 'work_hour': 8},
                'tuesday': {'start_time': '23:00', 'work_hour': 8},
                'wednesday': {'start_time': '23:00', 'work_hour': 8},
                'thursday': {'start_time': '23:00', 'work_hour': 8},
                'friday': {'start_time': '23:00', 'work_hour': 8},
                'saturday': {'start_time': '23:00', 'work_hour': 8}
            },
            {
                'shift_no': 2,
                'monday': {'start_time': '09:00', 'work_hour': 8},
                'tuesday': {'start_time': '09:00', 'work_hour': 8},
                'wednesday': {'start_time': '09:00', 'work_hour': 8},
                'thursday': {'start_time': '09:00', 'work_hour': 8},
                'friday': {'start_time': '09:00', 'work_hour': 8},
                'saturday': {'start_time': '09:00', 'work_hour': 8}
            }]
        inst_shift_rule.save()

        inst_staff = self._create_staff()

        ShiftRuleStaffModel.objects.create(shift_no=1, staff=inst_staff, shift_rule=inst_shift_rule)

        apply_working_hours()

        inst_working_hour = WorkingHourModel.objects.get(staff=inst_staff)
        start_dt = datetime.datetime(2021, 12, 6, 23, 0)
        finish_dt = start_dt + datetime.timedelta(hours=8)
        self.assertEqual(start_dt, inst_working_hour.start_dt)
        self.assertEqual(finish_dt, inst_working_hour.finish_dt)
        self.assertEqual(ShiftTypeEnum.NORMAL, inst_working_hour.type)

    def test_no_shift_on_a_holiday(self):
        """
            tatil günü vardiya mesai olmaması lazım
        """
        today = datetime.datetime.today().date()

        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.start_date = today - datetime.timedelta(weeks=20)
        inst_shift_rule.finish_date = None
        inst_shift_rule.period_start_date = inst_shift_rule.start_date
        inst_shift_rule.period_end_date = inst_shift_rule.period_start_date + datetime.timedelta(
            weeks=inst_shift_rule.period_duration)
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '23:00', 'work_hour': 8},
                'tuesday': {'start_time': '23:00', 'work_hour': 8},
                'wednesday': {'start_time': '23:00', 'work_hour': 8},
                'thursday': {'start_time': '23:00', 'work_hour': 8},
                'friday': {'start_time': '23:00', 'work_hour': 8},
                'saturday': {'start_time': '23:00', 'work_hour': 8}
            },
            {
                'shift_no': 2,
                'monday': {'start_time': '09:00', 'work_hour': 8},
                'tuesday': {'start_time': '09:00', 'work_hour': 8},
                'wednesday': {'start_time': '09:00', 'work_hour': 8},
                'thursday': {'start_time': '09:00', 'work_hour': 8},
                'friday': {'start_time': '09:00', 'work_hour': 8},
                'saturday': {'start_time': '09:00', 'work_hour': 8}
            }]
        inst_shift_rule.save()

        inst_holiday = self._create_holiday()
        inst_holiday.start_date = today - datetime.timedelta(days=1)
        inst_holiday.finish_date = today + datetime.timedelta(days=1)
        inst_holiday.save()

        inst_staff = self._create_staff()

        ShiftRuleStaffModel.objects.create(shift_no=1, staff=inst_staff, shift_rule=inst_shift_rule)

        apply_working_hours()

        count = WorkingHourModel.objects.count()
        self.assertEqual(0, count)

    def test_no_shift_on_a_bank_holiday(self):
        """
            tatil günü vardiya mesai olmaması lazım
        """
        today = datetime.datetime.today().date()

        inst_holiday = self._create_bank_holiday()
        inst_holiday.start_date = today - datetime.timedelta(days=1)
        inst_holiday.finish_date = today + datetime.timedelta(days=1)
        inst_holiday.month = 12
        inst_holiday.day = 6
        inst_holiday.save()

        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.start_date = today - datetime.timedelta(weeks=20)
        inst_shift_rule.finish_date = None
        inst_shift_rule.period_start_date = inst_shift_rule.start_date
        inst_shift_rule.period_end_date = inst_shift_rule.period_start_date + datetime.timedelta(
            weeks=inst_shift_rule.period_duration)
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '23:00', 'work_hour': 8},
                'tuesday': {'start_time': '23:00', 'work_hour': 8},
                'wednesday': {'start_time': '23:00', 'work_hour': 8},
                'thursday': {'start_time': '23:00', 'work_hour': 8},
                'friday': {'start_time': '23:00', 'work_hour': 8},
                'saturday': {'start_time': '23:00', 'work_hour': 8}
            },
            {
                'shift_no': 2,
                'monday': {'start_time': '09:00', 'work_hour': 8},
                'tuesday': {'start_time': '09:00', 'work_hour': 8},
                'wednesday': {'start_time': '09:00', 'work_hour': 8},
                'thursday': {'start_time': '09:00', 'work_hour': 8},
                'friday': {'start_time': '09:00', 'work_hour': 8},
                'saturday': {'start_time': '09:00', 'work_hour': 8}
            }]
        inst_shift_rule.save()

        inst_staff = self._create_staff()

        ShiftRuleStaffModel.objects.create(shift_no=1, staff=inst_staff, shift_rule=inst_shift_rule)

        apply_working_hours()

        count = WorkingHourModel.objects.count()
        self.assertEqual(0, count)


@freeze_time("2021-12-06")
class TestApplyCustomShift(TestBase):

    def test_custom_shift_working_hour(self):
        """
            özel vardiya mesaisi
        """
        today = datetime.datetime.today().date()
        start_dt = datetime.datetime.combine(today, datetime.time(12))
        working_hour = 8

        inst_custom_shift = self._create_individual_shift()
        inst_custom_shift.start_dt = start_dt
        inst_custom_shift.finish_dt = start_dt + datetime.timedelta(hours=working_hour)
        inst_custom_shift.type = ShiftTypeEnum.NORMAL
        inst_custom_shift.save()

        apply_working_hours()

        inst_working_hour = WorkingHourModel.objects.get(staff=inst_custom_shift.staff)
        start_dt = datetime.datetime(2021, 12, 6, 12, 0)
        finish_dt = start_dt + datetime.timedelta(hours=working_hour)

        self.assertEqual(start_dt, inst_working_hour.start_dt)
        self.assertEqual(finish_dt, inst_working_hour.finish_dt)
        self.assertEqual(ShiftTypeEnum.NORMAL, inst_working_hour.type)

    def test_custom_shift_on_a_holiday(self):
        """
            tatilde özel vardiya mesaisi yazılır
        """
        today = datetime.datetime.today().date()
        start_dt = datetime.datetime.combine(today, datetime.time(12))
        working_hour = 8

        inst_holiday = self._create_holiday()
        inst_holiday.start_date = today - datetime.timedelta(days=1)
        inst_holiday.finish_date = today + datetime.timedelta(days=1)
        inst_holiday.save()

        inst_custom_shift = self._create_individual_shift()
        inst_custom_shift.start_dt = start_dt
        inst_custom_shift.finish_dt = start_dt + datetime.timedelta(hours=working_hour)
        inst_custom_shift.type = ShiftTypeEnum.NORMAL
        inst_custom_shift.save()

        apply_working_hours()

        inst_working_hour = WorkingHourModel.objects.get(staff=inst_custom_shift.staff)
        start_dt = datetime.datetime(2021, 12, 6, 12, 0)
        finish_dt = start_dt + datetime.timedelta(hours=working_hour)

        self.assertEqual(start_dt, inst_working_hour.start_dt)
        self.assertEqual(finish_dt, inst_working_hour.finish_dt)
        self.assertEqual(ShiftTypeEnum.NORMAL, inst_working_hour.type)

    def test_custom_on_a_bank_holiday(self):
        """
            resmi tatilde özel vardiya mesaisi yazılır
        """
        today = datetime.datetime.today().date()
        start_dt = datetime.datetime.combine(today, datetime.time(12))
        working_hour = 8

        inst_holiday = self._create_bank_holiday()
        inst_holiday.start_date = today - datetime.timedelta(days=1)
        inst_holiday.finish_date = today + datetime.timedelta(days=1)
        inst_holiday.month = 12
        inst_holiday.day = 6
        inst_holiday.save()

        inst_custom_shift = self._create_individual_shift()
        inst_custom_shift.start_dt = start_dt
        inst_custom_shift.finish_dt = start_dt + datetime.timedelta(hours=working_hour)
        inst_custom_shift.type = ShiftTypeEnum.NORMAL
        inst_custom_shift.save()

        apply_working_hours()

        inst_working_hour = WorkingHourModel.objects.get(staff=inst_custom_shift.staff)
        start_dt = datetime.datetime(2021, 12, 6, 12, 0)
        finish_dt = start_dt + datetime.timedelta(hours=working_hour)

        self.assertEqual(start_dt, inst_working_hour.start_dt)
        self.assertEqual(finish_dt, inst_working_hour.finish_dt)
        self.assertEqual(ShiftTypeEnum.NORMAL, inst_working_hour.type)


@freeze_time("2021-12-06")
class TestInOutTime(TestBase):
    def test_find_the_nearest_job_start_time(self):
        work_hour = 8
        start_dt = datetime.datetime.today() - datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        inst_staff = self._create_staff()

        # mesai oluştur
        WorkingHourModel.objects.create(
            start_dt=start_dt,
            finish_dt=finish_dt,
            work_hour=work_hour,
            type=ShiftTypeEnum.NORMAL,
            staff=inst_staff
        )

        time_before_20_minute = start_dt - datetime.timedelta(minutes=20)
        time_before_10_minute = start_dt - datetime.timedelta(minutes=10)
        time_after_5_minute = start_dt + datetime.timedelta(minutes=5)
        time_after_20_minute = start_dt + datetime.timedelta(minutes=20)

        # log oluştur
        # mesai saati girişinden, 20 dakika önce, 10 dakika önce ve 5 dakika sonra ve 20 dakika sonra 4 tane log olsun
        PersonDeviceLogModel.objects.bulk_create([
            PersonDeviceLogModel(
                person=inst_staff.person,
                device_name='Device name',
                device_module=UsingModuleEnum.STAFF,
                time=time_before_20_minute
            ),
            PersonDeviceLogModel(
                person=inst_staff.person,
                device_name='Device name',
                device_module=UsingModuleEnum.STAFF,
                time=time_before_10_minute
            ),
            PersonDeviceLogModel(
                person=inst_staff.person,
                device_name='Device name',
                device_module=UsingModuleEnum.STAFF,
                time=time_after_5_minute
            ),
            PersonDeviceLogModel(
                person=inst_staff.person,
                device_name='Device name',
                device_module=UsingModuleEnum.STAFF,
                time=time_after_20_minute
            )
        ])

        # görev çalıştıkdan sonra 10 dakika önceki logu giriş saati olarak alması gerekiyor
        find_in_out_times()

        inst_working_hour = WorkingHourModel.objects.get()
        self.assertEqual(inst_working_hour.in_dt, time_before_10_minute)
        self.assertIsNone(inst_working_hour.out_dt)

    def test_find_the_nearest_job_finish_time(self):
        work_hour = 8
        start_dt = datetime.datetime.today() - datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        inst_staff = self._create_staff()

        # mesai oluştur
        WorkingHourModel.objects.create(
            start_dt=start_dt,
            finish_dt=finish_dt,
            work_hour=work_hour,
            type=ShiftTypeEnum.NORMAL,
            staff=inst_staff
        )

        time_before_20_minute = finish_dt - datetime.timedelta(minutes=20)
        time_before_10_minute = finish_dt - datetime.timedelta(minutes=10)
        time_after_5_minute = finish_dt + datetime.timedelta(minutes=5)
        time_after_20_minute = finish_dt + datetime.timedelta(minutes=20)

        # log oluştur
        # mesai saati çıkışından, 20 dakika önce, 10 dakika önce ve 5 dakika sonra ve 20 dakika sonra 4 tane log olsun
        PersonDeviceLogModel.objects.bulk_create([
            PersonDeviceLogModel(
                person=inst_staff.person,
                device_name='Device name',
                device_module=UsingModuleEnum.STAFF,
                time=time_before_20_minute
            ),
            PersonDeviceLogModel(
                person=inst_staff.person,
                device_name='Device name',
                device_module=UsingModuleEnum.STAFF,
                time=time_before_10_minute
            ),
            PersonDeviceLogModel(
                person=inst_staff.person,
                device_name='Device name',
                device_module=UsingModuleEnum.STAFF,
                time=time_after_5_minute
            ),
            PersonDeviceLogModel(
                person=inst_staff.person,
                device_name='Device name',
                device_module=UsingModuleEnum.STAFF,
                time=time_after_20_minute
            )
        ])

        # görev çalıştıkdan sonra 5 dakika sonraki logu çıkış saati olarak alması gerekiyor
        find_in_out_times()

        inst_working_hour = WorkingHourModel.objects.get()
        self.assertEqual(inst_working_hour.out_dt, time_after_5_minute)
        self.assertIsNone(inst_working_hour.in_dt)


@freeze_time("2021-12-06")
class TestAbsenteeStaff(TestBase):
    def test_absentee_staff_paginate_on_date(self):
        work_hour = 8
        today = datetime.datetime.today().date()
        start_dt = datetime.datetime.combine(today, datetime.time(9, 0, 0))
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        inst_staff = self._create_staff()

        # mesai oluştur
        WorkingHourModel.objects.create(
            start_dt=start_dt,
            finish_dt=finish_dt,
            work_hour=work_hour,
            type=ShiftTypeEnum.NORMAL,
            staff=inst_staff
        )

        date_str = start_dt.strftime("%Y-%m-%d")
        url = reverse('betik_app_staff:absentee-staff-paginate-on-date', kwargs={'date': date_str})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = WorkingHourModel.objects.all()
        serializer_dict = WorkingHourSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        self.assertEqual(response.data['count'], 1)


@freeze_time("2021-12-06")
class TestLateStaff(TestBase):
    def test_late_staff_paginate_on_date(self):
        work_hour = 8
        today = datetime.datetime.today().date()
        start_dt = datetime.datetime.combine(today, datetime.time(9, 0, 0))
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        inst_staff = self._create_staff()

        # mesai oluştur
        WorkingHourModel.objects.create(
            start_dt=start_dt,
            finish_dt=finish_dt,
            work_hour=work_hour,
            type=ShiftTypeEnum.NORMAL,
            staff=inst_staff
        )

        time_after_20_minute = start_dt + datetime.timedelta(minutes=20)

        # log oluştur
        # mesai saatine 20dak. geç kaldı
        PersonDeviceLogModel.objects.bulk_create([
            PersonDeviceLogModel(
                person=inst_staff.person,
                device_name='Device name',
                device_module=UsingModuleEnum.STAFF,
                time=time_after_20_minute
            )
        ])

        # görev çalıştıkdan sonra 20 dakika sonraki logu giriş saati olarak alması gerekiyor
        find_in_out_times()

        inst_working_hour = WorkingHourModel.objects.get()
        self.assertEqual(inst_working_hour.late_minute, 20)

        date_str = start_dt.strftime("%Y-%m-%d")
        url = reverse('betik_app_staff:late-staff-paginate-on-date', kwargs={'date': date_str})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = WorkingHourModel.objects.all()
        serializer_dict = WorkingHourSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        self.assertEqual(response.data['count'], 1)