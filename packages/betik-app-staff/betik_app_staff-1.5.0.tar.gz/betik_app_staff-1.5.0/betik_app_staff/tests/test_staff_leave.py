import datetime

from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils.translation import gettext as _

from betik_app_staff.enums import LeaveDurationTypeEnum, LeaveTypeEnum
from betik_app_staff.models import StaffLeaveModel
from betik_app_staff.serializers.staff_leave import StaffLeaveSerializer
from betik_app_staff.tests.base import TestBase


class TestStaffLeaveBase(TestBase):
    pass


class TestCRUD(TestStaffLeaveBase):
    def test_create_hour(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)
        start_date = datetime.datetime.combine(tomorrow, time)

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': start_date.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.HOUR
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_create_day(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)
        start_date = datetime.datetime.combine(tomorrow, time)

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': start_date.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.DAY
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_create_month(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)
        start_date = datetime.datetime.combine(tomorrow, time)

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': start_date.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.MONTH
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_create_year(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)
        start_date = datetime.datetime.combine(tomorrow, time)

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': start_date.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.YEAR
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_create_business_day(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)
        start_date = datetime.datetime.combine(tomorrow, time)

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': start_date.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.BUSINESS_DAY
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_update_hour(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)

        start_date = datetime.datetime.combine(tomorrow, time)
        finish_date = start_date + datetime.timedelta(days=1)

        inst_staff_leave = self._create_staff_leave(None, start_date, finish_date, LeaveDurationTypeEnum.HOUR)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff_leave.staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': (start_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
            'duration': 10,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 200, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_update_day(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)

        start_date = datetime.datetime.combine(tomorrow, time)
        finish_date = start_date + datetime.timedelta(days=1)

        inst_staff_leave = self._create_staff_leave(None, start_date, finish_date, LeaveDurationTypeEnum.DAY)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff_leave.staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': (start_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
            'duration': 10,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 200, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_update_month(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)

        start_date = datetime.datetime.combine(tomorrow, time)
        finish_date = start_date + datetime.timedelta(days=1)

        inst_staff_leave = self._create_staff_leave(None, start_date, finish_date, LeaveDurationTypeEnum.MONTH)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff_leave.staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': (start_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
            'duration': 10,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 200, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_update_year(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)

        start_date = datetime.datetime.combine(tomorrow, time)
        finish_date = start_date + datetime.timedelta(days=1)

        inst_staff_leave = self._create_staff_leave(None, start_date, finish_date, LeaveDurationTypeEnum.YEAR)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff_leave.staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': (start_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
            'duration': 10,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 200, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_update_business_day(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)

        start_date = datetime.datetime.combine(tomorrow, time)
        finish_date = start_date + datetime.timedelta(days=1)

        inst_staff_leave = self._create_staff_leave(None, start_date, finish_date, LeaveDurationTypeEnum.BUSINESS_DAY)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff_leave.staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': (start_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
            'duration': 10,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 200, response.data)

        instance = StaffLeaveModel.objects.get(id=1)
        serializer_dict = StaffLeaveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_delete(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)
        start_date = datetime.datetime.combine(tomorrow, time)

        inst_staff_leave = self._create_staff_leave(None, start_date)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff_leave.staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        url = reverse('betik_app_staff:staff-leave-delete', kwargs={'pk': inst_staff_leave.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

    def test_paginate(self):
        inst_staff_leave1 = self._create_staff_leave()
        inst_staff_leave2 = self._create_staff_leave()

        date_start = min(inst_staff_leave1.start_dt, inst_staff_leave2.start_dt)
        date_finish = max(inst_staff_leave1.finish_dt, inst_staff_leave2.finish_dt)

        kwargs = {
            'start_dt_gte': date_start.strftime("%Y-%m-%d %H:%M:%S"),
            'start_dt_lte': date_finish.strftime("%Y-%m-%d %H:%M:%S")
        }
        url = reverse('betik_app_staff:staff-leave-paginate', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = StaffLeaveModel.objects.all().order_by('-start_dt', 'staff__person__name',
                                                           'staff__person__last_name')
        serializer_data = StaffLeaveSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_data)


class TestCreateFail(TestStaffLeaveBase):
    def test_staff_is_passive(self):
        """
            pasif personele izin verilemez
        """
        today = datetime.datetime.today().date()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        inst_staff = self._create_staff()
        inst_staff.finish_date = yesterday
        inst_staff.save()

        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = today - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.DAY
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Staff is passive')
        self.assertDictEqual(response.data, {'staff_id': [msg]})

    def test_start_time_should_be_fifteen_minute_period(self):
        """
            saat izni alıncaksa, başlama saati 15 dakikalık periyotlarda olmalı(00,15,30,45)
        """
        now = datetime.datetime.today()
        tomorrow = now.date() + datetime.timedelta(days=1)
        tomorrow = datetime.datetime.combine(tomorrow, datetime.time(hour=9, minute=16))

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.HOUR
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('It should be in 15-minute periods')
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_start_time_should_be_hourly(self):
        """
            saat izni alınmayacaksa, başlama saati saat başı olmalı
        """
        now = datetime.datetime.today()
        tomorrow = now.date() + datetime.timedelta(days=1)
        tomorrow = datetime.datetime.combine(tomorrow, datetime.time(hour=9, minute=16))

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.DAY
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('It should be hourly')
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_if_hour_leave_start_time_bigger_than_now(self):
        """
            saat izni alınacaksa, başlama saati şimdiden sonra olmalı
        """
        now = datetime.datetime.today()
        yesterday = now.date() - datetime.timedelta(days=1)
        yesterday = datetime.datetime.combine(yesterday, datetime.time(hour=9, minute=15))

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': yesterday.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.HOUR
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Bigger than %(dt)s') % {'dt': datetime.datetime.today().strftime("%d %B %Y %H:%M")}
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_if_not_hour_leave_start_time_bigger_than_today(self):
        """
            saat izni alınmayacaksa, başlama tarihi bugünden sonra olmalı
        """
        now = datetime.datetime.today()
        yesterday = now.date() - datetime.timedelta(days=1)
        yesterday = datetime.datetime.combine(yesterday, datetime.time(hour=9, minute=0))

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': yesterday.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.DAY
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Bigger than today')
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_if_leave_type_is_annual_leave_duration_type_is_not_required(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)
        start_date = datetime.datetime.combine(tomorrow, time)

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()
        inst_leave_type.code = LeaveTypeEnum.ANNUAL_LEAVE
        inst_leave_type.save()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': start_date.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.DAY
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('If leave type is annual leave, not required')
        self.assertDictEqual(response.data, {'duration_type_code': [msg]})

    def test_if_leave_type_is_not_annual_leave_duration_type_is_required(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)
        start_date = datetime.datetime.combine(tomorrow, time)

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': start_date.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('If leave type is not annual leave, required')
        self.assertDictEqual(response.data, {'duration_type_code': [msg]})

    def test_conflict_other_leave(self):
        """
            aynı tarihlere başka izinleerle çakışma olmasın
        """
        now = datetime.datetime.today()
        tomorrow = now.date() + datetime.timedelta(days=1)
        next10day = now.date() + datetime.timedelta(days=10)
        yesterday = now.date() - datetime.timedelta(days=1)
        yesterday = datetime.datetime.combine(yesterday, datetime.time(hour=9, minute=0))

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        inst_leave = StaffLeaveModel.objects.create(
            start_dt=yesterday,
            finish_dt=next10day,
            work_start_dt=next10day,
            staff=inst_staff,
            leave_type=inst_leave_type,
            duration=10,
            duration_type=LeaveDurationTypeEnum.DAY
        )

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'duration': 5,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.DAY
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('There is conflict with another leave date(%(leave_type)s %(date1)s - %(date2)s)') % {
            'leave_type': inst_leave.leave_type.type,
            'date1': inst_leave.start_dt.strftime('%d %B %Y %H:%M'),
            'date2': inst_leave.finish_dt.strftime('%d %B %Y %H:%M')
        }
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_working_hours_were_not_determined_for_the_staff_type_on_date(self):
        """
            istenen tarihde, personel tipi için çalışma saatleri belirlenmedi
        """
        # genel iş kuralı 10 gün sonra başlayacak
        # ama izin yarın başlayacak

        now = datetime.datetime.today()
        tomorrow = now.date() + datetime.timedelta(days=1)
        tomorrow = datetime.datetime.combine(tomorrow, datetime.time(hour=9, minute=0))

        inst_staff = self._create_staff()
        inst_leave_type = self._create_leave_type()

        # genel iş kuralı 10 gün sonra başlayacak
        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now + datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_leave_type.id,
            'duration_type_code': LeaveDurationTypeEnum.DAY
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        # 1 günlük tatilin ardından, işe başlama tarihi buluncak.
        # ancak bir gün sonraki tarihde mesai saati kuralı bulunamayacak
        work_start_date = tomorrow + datetime.timedelta(days=1)
        msg = _('Working hours were not determined for the %(staff_type)s on %(date)s') % {
            'staff_type': inst_staff.staff_type.name,
            'date': work_start_date.strftime('%d %B %Y')
        }
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_annual_leave_rule_were_not_determined_for_the_staff_type_on_date(self):
        """
            istenilen tarihlerde, yıllık izin kuralı bu personel tipi için belirlenmemiş
        """
        now = datetime.datetime.today()
        tomorrow = now.date() + datetime.timedelta(days=1)
        yesterday = now.date() - datetime.timedelta(days=1)

        inst_staff = self._create_staff()

        inst_leave_type = self._create_leave_type()
        inst_leave_type.code = LeaveTypeEnum.ANNUAL_LEAVE
        inst_leave_type.save()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'duration': 5,
            'leave_type_id': inst_leave_type.id
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Annual leave rule were not determined for the %(staff_type)s on %(date)s') % {
            'staff_type': inst_staff.staff_type.name,
            'date': tomorrow.strftime('%d %B %Y')
        }
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_considering_the_date_of_employment_of_the_staff_they_have_not_yet_obtained_the_right_to_take_annual_leave(
            self):
        """
            personel yenüz yıllık izin hakkı kazanmamış
        """
        now = datetime.datetime.today()
        tomorrow = now.date() + datetime.timedelta(days=1)
        yesterday = now.date() - datetime.timedelta(days=1)

        # personelin işe başlama tarihi bugün. En az yıllık izin hakkı için 4 yıl çalışmalı

        inst_staff = self._create_staff()

        inst_leave_type = self._create_leave_type()
        inst_leave_type.code = LeaveTypeEnum.ANNUAL_LEAVE
        inst_leave_type.save()

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        inst_annual_leave_rule = self._create_annual_leave_rule()
        inst_annual_leave_rule.start_date = yesterday
        inst_annual_leave_rule.staff_type = inst_staff.staff_type
        inst_annual_leave_rule.save()

        post_data = {
            'staff_id': inst_staff.id,
            'start_dt': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'duration': 5,
            'leave_type_id': inst_leave_type.id
        }

        url = reverse('betik_app_staff:staff-leave-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _(
            'Considering the date of employment of the staff, they have not yet obtained the right to take annual leave.')
        self.assertDictEqual(response.data, {'detail': [msg]})


class TestUpdateFail(TestStaffLeaveBase):
    def test_if_duration_type_is_hour_the_start_dt_cannot_be_changed_because_the_leave_has_started(self):
        """
            saatlik iznin, başlama tarihi şimdiye eşit veya önceyse, başlama tarihi değiştirilemez
        """
        now = datetime.datetime.today()
        now = datetime.datetime.combine(now, datetime.time(hour=9))

        yesterday = now.date() - datetime.timedelta(days=1)
        tomorrow = now.date() + datetime.timedelta(days=2)

        inst_staff = self._create_staff()
        inst_staff_leave = self._create_staff_leave(inst_staff, yesterday, tomorrow, LeaveDurationTypeEnum.HOUR)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('The start date cannot be changed because the leave has started')
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_if_duration_type_is_not_hour_the_start_dt_cannot_be_changed_because_the_leave_has_started(self):
        """
            saatlik olmayan iznin, başlama tarihi bugüne eşit yada önceyse, başlama tarihi değiştirilemez
        """
        now = datetime.datetime.today()
        now = datetime.datetime.combine(now, datetime.time(hour=9))

        yesterday = now.date() - datetime.timedelta(days=1)
        tomorrow = now.date() + datetime.timedelta(days=2)

        inst_staff = self._create_staff()
        inst_staff_leave = self._create_staff_leave(inst_staff, yesterday, tomorrow, LeaveDurationTypeEnum.DAY)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('The start date cannot be changed because the leave has started')
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_if_duration_type_is_hour_the_start_dt_bigger_then_now(self):
        """
            saatlik iznin, başlama tarihi şimdiden sonra olmalı
        """
        now = datetime.datetime.today()
        now = datetime.datetime.combine(now, datetime.time(hour=9))

        yesterday = now.date() - datetime.timedelta(days=1)
        tomorrow = now.date() + datetime.timedelta(days=2)
        after1day = tomorrow + datetime.timedelta(days=2)

        inst_staff = self._create_staff()
        inst_staff_leave = self._create_staff_leave(inst_staff, tomorrow, after1day, LeaveDurationTypeEnum.HOUR)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': yesterday.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        now = datetime.datetime.today()
        msg = _('Bigger than %(dt)s') % {'dt': now.strftime("%d %B %Y %H:%M")}
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_if_duration_type_is_not_hour_the_start_dt_bigger_then_today(self):
        """
            saatlik olmayan iznin, başlama tarihi bugüne eşit yada önceyse, başlama tarihi değiştirilemez
        """
        now = datetime.datetime.today()
        now = datetime.datetime.combine(now, datetime.time(hour=9))

        today = now.date()
        yesterday = now.date() - datetime.timedelta(days=1)
        tomorrow = now.date() + datetime.timedelta(days=1)
        after1day = tomorrow + datetime.timedelta(days=1)

        inst_staff = self._create_staff()
        inst_staff_leave = self._create_staff_leave(inst_staff, tomorrow, after1day, LeaveDurationTypeEnum.DAY)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': today.strftime('%Y-%m-%d %H:%M'),
            'duration': 1,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Bigger than today')
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_if_duration_type_is_hour_the_finish_dt_cannot_be_changed_because_the_leave_has_finished(self):
        """
            saatlik iznin, bitiş tarihi şimdiye eşit veya önceyse, bitiş tarihi değiştirilemez
        """
        now = datetime.datetime.today()
        now = datetime.datetime.combine(now, datetime.time(hour=9))

        yesterday = now - datetime.timedelta(days=1)
        before2day = yesterday - datetime.timedelta(days=1)

        inst_staff = self._create_staff()
        inst_staff_leave = self._create_staff_leave(inst_staff, before2day, yesterday, LeaveDurationTypeEnum.HOUR)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': inst_staff_leave.start_dt.strftime("%Y-%m-%d %H:%M"),
            'duration': 10,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('The finish date cannot be changed because the leave has finished')
        self.assertDictEqual(response.data, {'finish_dt': [msg]})

    def test_if_duration_type_is_not_hour_the_finish_dt_cannot_be_changed_because_the_leave_has_finished(self):
        """
            saatlik olmayan iznin, bitiş tarihi bugüne eşit veya önceyse, bitiş tarihi değiştirilemez
        """
        now = datetime.datetime.today()
        now = datetime.datetime.combine(now, datetime.time(hour=9))

        yesterday = now - datetime.timedelta(days=1)
        before2day = yesterday - datetime.timedelta(days=1)

        inst_staff = self._create_staff()
        inst_staff_leave = self._create_staff_leave(inst_staff, before2day, yesterday, LeaveDurationTypeEnum.DAY)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': inst_staff_leave.start_dt.strftime("%Y-%m-%d %H:%M"),
            'duration': 10,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('The finish date cannot be changed because the leave has finished')
        self.assertDictEqual(response.data, {'finish_dt': [msg]})

    def test_if_duration_type_hour_the_finish_dt_bigger_than_now(self):
        """
            bitiş tarihi henüz gelmemiş saatlik iznin, bitiş tarihi şimdiden sonra olmalı
        """
        now = datetime.datetime.today()
        now = datetime.datetime.combine(now, datetime.time(hour=9))

        yesterday = now - datetime.timedelta(days=1)
        tomorrow = now + datetime.timedelta(days=1)
        before2day = yesterday - datetime.timedelta(days=1)

        inst_staff = self._create_staff()
        inst_staff_leave = self._create_staff_leave(inst_staff, before2day, tomorrow, LeaveDurationTypeEnum.HOUR)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': inst_staff_leave.start_dt.strftime("%Y-%m-%d %H:%M"),
            'duration': 1,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        now = datetime.datetime.today()
        msg = _('Bigger than %(dt)s') % {'dt': now.strftime("%d %B %Y %H:%M")}
        self.assertDictEqual(response.data, {'finish_dt': [msg]})

    def test_if_duration_type_is_not_hour_the_finish_dt_bigger_than_now(self):
        """
            bitiş tarihi henüz gelmemiş saatlik olmayan iznin, bitiş tarihi bugünden sonra olmalı
        """
        now = datetime.datetime.today()
        now = datetime.datetime.combine(now, datetime.time(hour=9))

        yesterday = now - datetime.timedelta(days=1)
        tomorrow = now + datetime.timedelta(days=1)
        before2day = yesterday - datetime.timedelta(days=1)

        inst_staff = self._create_staff()
        inst_staff_leave = self._create_staff_leave(inst_staff, before2day, tomorrow, LeaveDurationTypeEnum.DAY)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff.staff_type
        inst_bus_day.start_date = now - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        put_data = {
            'staff_id': inst_staff_leave.staff.id,
            'start_dt': inst_staff_leave.start_dt.strftime("%Y-%m-%d %H:%M"),
            'duration': 1,
            'leave_type_id': inst_staff_leave.leave_type.id,
            'duration_type_code': inst_staff_leave.duration_type
        }

        url = reverse('betik_app_staff:staff-leave-update', kwargs={'pk': inst_staff_leave.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Bigger than today')
        self.assertDictEqual(response.data, {'finish_dt': [msg]})


class TestDeleteFail(TestBase):
    def test_active_record_can_not_be_deleted(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        time = datetime.time(tomorrow.hour, 0, 0, 0)

        start_dt = datetime.datetime.combine(today, time)
        finish_dt = start_dt + datetime.timedelta(days=2)

        inst_staff_leave = self._create_staff_leave(None, start_dt, finish_dt)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff_leave.staff.staff_type
        inst_bus_day.start_date = tomorrow - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        url = reverse('betik_app_staff:staff-leave-delete', kwargs={'pk': inst_staff_leave.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('active record can not be deleted')
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_expired_record_can_not_be_deleted(self):
        today = datetime.datetime.now()
        today = datetime.datetime.combine(today, datetime.time(today.hour, 0, 0, 0))

        yesterday = today - datetime.timedelta(days=1)
        yesterday_before = yesterday - datetime.timedelta(days=1)

        start_dt = yesterday_before
        finish_dt = start_dt + datetime.timedelta(days=1)

        inst_staff_leave = self._create_staff_leave(None, start_dt, finish_dt)

        inst_bus_day = self._create_business_day()
        inst_bus_day.staff_type = inst_staff_leave.staff.staff_type
        inst_bus_day.start_date = yesterday_before - datetime.timedelta(days=10)
        inst_bus_day.finish_date = None
        inst_bus_day.monday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.tuesday = {'start_time': '09:00', 'work_hour': 8}
        inst_bus_day.save()

        url = reverse('betik_app_staff:staff-leave-delete', kwargs={'pk': inst_staff_leave.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('outdated record can not be deleted')
        self.assertDictEqual(response.data, {'detail': [msg]})


class TestAnnualLeaveReport(TestBase):
    def test_report_annual_leave_no_forward_next_year(self):
        """
            10 senelik çalışanın geçmişte kalan izinleri aktarılmıyor
        """
        today = datetime.datetime.today().date()
        start_date = today - relativedelta(years=10)

        # personel 10 yıl önce işe başladı
        inst_staff = self._create_staff()
        inst_staff.start_date = start_date
        inst_staff.save()

        inst_annual_leave_rule = self._create_annual_leave_rule()
        inst_annual_leave_rule.staff_type = inst_staff.staff_type
        inst_annual_leave_rule.start_date = today - relativedelta(years=20)
        inst_annual_leave_rule.forward_next_year = False
        inst_annual_leave_rule.periods = [
            {'start_year': 1, 'finish_year': 4, 'duration': 10},
            {'start_year': 4, 'finish_year': 8, 'duration': 15},
            {'start_year': 8, 'finish_year': None, 'duration': 20},
        ]
        inst_annual_leave_rule.save()

        url = reverse('betik_app_staff:annual-leave-report-staff-list', kwargs={'staff_id': inst_staff.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        self.assertEqual(len(response.data['leaves']), 11)
        self.assertEqual(response.data['leaves'][0]['day'], 0)
        self.assertEqual(response.data['leaves'][0]['total_unused_day'], 0)
        self.assertEqual(response.data['leaves'][10]['day'], 20)
        self.assertEqual(response.data['leaves'][10]['total_unused_day'], 20)

    def test_report_annual_leave_all_forward_next_year(self):
        """
            10 senelik çalışanın geçmişte kalan tüm izinleri aktarılıyor
        """
        today = datetime.datetime.today().date()
        start_date = today - relativedelta(years=10)

        # personel 10 yıl önce işe başladı
        inst_staff = self._create_staff()
        inst_staff.start_date = start_date
        inst_staff.save()

        # izin tipi oluştur
        inst_leave_type = self._create_leave_type()
        inst_leave_type.code = LeaveTypeEnum.ANNUAL_LEAVE
        inst_leave_type.save()

        inst_annual_leave_rule = self._create_annual_leave_rule()
        inst_annual_leave_rule.staff_type = inst_staff.staff_type
        inst_annual_leave_rule.start_date = today - relativedelta(years=20)
        inst_annual_leave_rule.forward_next_year = True
        inst_annual_leave_rule.forward_year = None
        inst_annual_leave_rule.periods = [
            {'start_year': 1, 'finish_year': 4, 'duration': 10},
            {'start_year': 4, 'finish_year': 8, 'duration': 15},
            {'start_year': 8, 'finish_year': None, 'duration': 20},
        ]
        inst_annual_leave_rule.save()

        url = reverse('betik_app_staff:annual-leave-report-staff-list', kwargs={'staff_id': inst_staff.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        self.assertEqual(len(response.data['leaves']), 11)
        self.assertEqual(response.data['leaves'][0]['day'], 0)
        self.assertEqual(response.data['leaves'][0]['total_unused_day'], 0)
        self.assertEqual(response.data['leaves'][10]['day'], 20)
        self.assertEqual(response.data['leaves'][10]['total_unused_day'], 150)
        self.assertEqual(response.data['total_unused_day'], 150)

        # 10 günlük izin al
        leave_start_date = today - relativedelta(years=5)
        leave_finish_date = leave_start_date + relativedelta(days=10)
        StaffLeaveModel.objects.create(
            start_dt=leave_start_date,
            finish_dt=leave_finish_date,
            work_start_dt=leave_finish_date,
            staff=inst_staff,
            leave_type=inst_leave_type,
            duration=10,
            duration_type=LeaveDurationTypeEnum.DAY
        )

        url = reverse('betik_app_staff:annual-leave-report-staff-list', kwargs={'staff_id': inst_staff.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        self.assertEqual(response.data['leaves'][5]['used_day'], 10)
        self.assertEqual(response.data['leaves'][5]['unused_day'], 5)
        self.assertEqual(response.data['leaves'][10]['total_unused_day'], 140)
        self.assertEqual(response.data['total_unused_day'], 140)

    def test_report_annual_leave_2_years_forward_next_year(self):
        """
            10 senelik çalışanın geçmişte kalan tüm izinleri aktarılıyor
        """
        today = datetime.datetime.today().date()
        start_date = today - relativedelta(years=10)

        # personel 10 yıl önce işe başladı
        inst_staff = self._create_staff()
        inst_staff.start_date = start_date
        inst_staff.save()

        inst_annual_leave_rule = self._create_annual_leave_rule()
        inst_annual_leave_rule.staff_type = inst_staff.staff_type
        inst_annual_leave_rule.start_date = today - relativedelta(years=20)
        inst_annual_leave_rule.forward_next_year = True
        inst_annual_leave_rule.forward_year = 2
        inst_annual_leave_rule.periods = [
            {'start_year': 1, 'finish_year': 4, 'duration': 10},
            {'start_year': 4, 'finish_year': 8, 'duration': 15},
            {'start_year': 8, 'finish_year': None, 'duration': 20},
        ]
        inst_annual_leave_rule.save()

        url = reverse('betik_app_staff:annual-leave-report-staff-list', kwargs={'staff_id': inst_staff.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        self.assertEqual(len(response.data['leaves']), 11)
        self.assertEqual(response.data['leaves'][0]['day'], 0)
        self.assertEqual(response.data['leaves'][0]['total_unused_day'], 0)
        self.assertEqual(response.data['leaves'][10]['day'], 20)
        self.assertEqual(response.data['leaves'][10]['total_unused_day'], 60)
        self.assertEqual(response.data['total_unused_day'], 60)
