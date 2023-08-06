import datetime

from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils.translation import gettext as _

from betik_app_staff.enums import ShiftTypeEnum
from betik_app_staff.models import IndividualShiftModel, ShiftRuleStaffModel
from betik_app_staff.serializers.custom_shift import CustomShiftSerializer
from betik_app_staff.tests.base import TestBase


class TestCustomShift(TestBase):
    def _create_post_data(self):
        start_dt = self.faker.future_date()
        start_dt = datetime.datetime.combine(start_dt, datetime.time(hour=8, minute=0, second=0, microsecond=0))

        return {
            'start_dt': start_dt.strftime("%Y-%m-%d %H:%M"),
            'work_hour': 8,
            'shift_type': ShiftTypeEnum.OVERTIME
        }


class TestCRUD(TestCustomShift):
    def test_assign(self):
        url = reverse('betik_app_staff:custom-shift-create-bulk')
        data = self._create_post_data()
        start_dt = datetime.datetime.strptime(data['start_dt'], '%Y-%m-%d %H:%M')

        # pazartesi gününe denk gelsin
        while start_dt.weekday() != 0:
            start_dt += datetime.timedelta(days=1)
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 202, response.data)

        self.assertDictEqual(response.data, {'result': True})

    def test_paginate(self):
        inst_staff = self._create_staff()
        inst_ind_shift = self._create_individual_shift()

        start_dt = inst_ind_shift.start_dt
        before_start_dt = start_dt - datetime.timedelta(days=1)
        after_start_dt = start_dt + datetime.timedelta(days=1)

        kwarg = {
            'start_dt_gte': before_start_dt.strftime("%Y-%m-%d %H:%M:%S"),
            'start_dt_lte': after_start_dt.strftime("%Y-%m-%d %H:%M:%S")
        }
        url = reverse('betik_app_staff:custom-shift-paginate', kwargs=kwarg)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        inst = IndividualShiftModel.objects.all()
        serializer_data = CustomShiftSerializer(instance=inst, many=True).data
        self.assertListEqual(response.data['results'], serializer_data)

    def test_delete(self):
        inst_ind_shift = self._create_individual_shift()

        url = reverse('betik_app_staff:custom-shift-delete', kwargs={'pk': inst_ind_shift.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

        count = IndividualShiftModel.objects.count()
        self.assertEqual(count, 0)


class TestDeleteFail(TestCustomShift):
    def test_those_before_tomorrow_cannot_be_deleted(self):
        """
            sadece yarından itibaren başlayacak olan özel vardiyalar silinebilir
        """
        inst_ind_shift = self._create_individual_shift()
        inst_ind_shift.start_dt -= relativedelta(years=1)
        inst_ind_shift.finish_dt = inst_ind_shift.start_dt + datetime.timedelta(days=1)
        inst_ind_shift.save()

        url = reverse('betik_app_staff:custom-shift-delete', kwargs={'pk': inst_ind_shift.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400, response.data)

        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        msg = _('Those before %(date)s cannot be deleted') % {
            'date': tomorrow.strftime("%d %B %Y")
        }
        self.assertDictEqual(response.data, {'detail': [msg]})


class TestAssignFail(TestCustomShift):
    def test_start_dt_is_bigger_than_today(self):
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)

        data = self._create_post_data()
        data['start_dt'] = yesterday.strftime("%Y-%m-%d %H:%M")

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_for_weekend_shift_type_only_sunday_shift_can_be_entered(self):
        start_dt = self.faker.future_date()
        if start_dt.weekday() == 6:
            start_dt += datetime.timedelta(days=1)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['shift_type'] = ShiftTypeEnum.WEEKEND

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('for this shift type, only sunday shift can be entered')
        self.assertDictEqual(response.data, {'shift_type': [msg]})

    def test_for_holiday_shift_type_only_holiday_days_can_be_entered(self):
        data = self._create_post_data()
        data['shift_type'] = ShiftTypeEnum.HOLIDAY

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('for this shift type, only holiday days can be entered')
        self.assertDictEqual(response.data, {'shift_type': [msg]})

    def test_overtime_shift_type_cannot_be_used_on_holidays(self):
        inst_holiday = self._create_holiday()

        data = self._create_post_data()
        data['start_dt'] = inst_holiday.start_date.strftime("%Y-%m-%d %H:%M")
        data['shift_type'] = ShiftTypeEnum.OVERTIME

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('this shift type cannot be used on holidays')
        self.assertDictEqual(response.data, {'shift_type': [msg]})

    def test_start_date_overlaps_with_another_individual_shift_on_the_same_dates(self):
        inst_ind_shift = self._create_individual_shift()
        staff = inst_ind_shift.staff

        data = self._create_post_data()
        data['start_dt'] = inst_ind_shift.start_dt.strftime("%Y-%m-%d %H:%M")

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _(
            'staff who has %(identity)s identity, %(name)s %(last_name)s names, conflict with individual shift which has #%(id)d no. Conflicting shift\'s dates are %(date1)s - %(date2)s') % {
                  'identity': staff.person.identity,
                  'name': staff.person.name,
                  'last_name': staff.person.last_name,
                  'id': inst_ind_shift.id,
                  'date1': inst_ind_shift.start_dt.strftime("%d %B %Y %H:%M"),
                  'date2': inst_ind_shift.finish_dt.strftime("%d %B %Y %H:%M")
              }
        self.assertDictEqual(response.data, {'start_dt': [msg]})

    def test_finish_date_overlaps_with_another_individual_shift_on_the_same_dates(self):
        inst_ind_shift = self._create_individual_shift()
        staff = inst_ind_shift.staff

        data = self._create_post_data()
        start_dt = inst_ind_shift.start_dt - datetime.timedelta(hours=1)
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _(
            'staff who has %(identity)s identity, %(name)s %(last_name)s names, conflict with individual shift which has #%(id)d no. Conflicting shift\'s dates are %(date1)s - %(date2)s') % {
                  'identity': staff.person.identity,
                  'name': staff.person.name,
                  'last_name': staff.person.last_name,
                  'id': inst_ind_shift.id,
                  'date1': inst_ind_shift.start_dt.strftime("%d %B %Y %H:%M"),
                  'date2': inst_ind_shift.finish_dt.strftime("%d %B %Y %H:%M")
              }
        self.assertDictEqual(response.data, {'work_hour': [msg]})

    def test_start_and_finish_dates_do_not_contain_the_dates_of_another_individual_shift(self):
        """
            başlangıç ve bitiş tarihleri, başka bir bireysel vardiyanın tarihlerini kapsamasın
        """
        inst_ind_shift = self._create_individual_shift()
        staff = inst_ind_shift.staff

        if inst_ind_shift.start_dt.weekday() == 6:
            inst_ind_shift.start_dt += datetime.timedelta(days=1)
        inst_ind_shift.save()

        data = self._create_post_data()
        start_dt = inst_ind_shift.start_dt - datetime.timedelta(hours=1)

        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = 20

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _(
            'staff who has with %(identity)s identity, %(name)s %(last_name)s named, individual shift which has #%(id)d ID, is covered. Shift\'s covered dates: %(date1)s to %(date2)s') % {
                  'identity': staff.person.identity,
                  'name': staff.person.name,
                  'last_name': staff.person.last_name,
                  'id': inst_ind_shift.id,
                  'date1': inst_ind_shift.start_dt.strftime("%d %B %Y %H:%M"),
                  'date2': inst_ind_shift.finish_dt.strftime("%d %B %Y %H:%M")
              }
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_the_start_time_of_the_individual_shift_coincides_with_the_working_hours_of_the_shift_the_day_before(self):
        """
            özel vardiyanın başlama saatinin, bir gün önceki vardiyanın çalışma saatleri ile çakışması
        """
        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '23:00', 'work_hour': 8},
                'tuesday': {'start_time': '23:00', 'work_hour': 8},
                'wednesday': {'start_time': '23:00', 'work_hour': 8},
                'thursday': {'start_time': '23:00', 'work_hour': 8},
                'friday': {'start_time': '23:00', 'work_hour': 8},
                'saturday': {'start_time': '23:00', 'work_hour': 8}
            }
        ]
        inst_shift_rule.save()

        inst_staff = self._create_staff()
        ShiftRuleStaffModel.objects.create(
            shift_rule=inst_shift_rule,
            staff=inst_staff,
            shift_no=1
        )

        # salı günü saat 05:00 - 13:00'da  özel vardiya ekle
        work_hour = 8
        start_dt = datetime.datetime.combine(inst_shift_rule.start_date + datetime.timedelta(days=1),
                                             datetime.time(5))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        prev_day_start_dt = start_dt - datetime.timedelta(days=1)
        before_business_day = inst_shift_rule.get_business_day_on_date(prev_day_start_dt, inst_staff)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the shift rule name %(name)s(%(date1)s - %(date2)s)') % {
            'name': inst_shift_rule.name,
            'date1': before_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
            'date2': before_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_start_time_of_the_individual_shift_coincides_with_the_working_hours_of_the_shift_the_same_day(self):
        """
            özel vardiyanın başlama saatinin, aynı gün başlayan vardiyanın çalışma saatleri ile çakışması
        """
        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '23:00', 'work_hour': 8},
                'tuesday': {'start_time': '23:00', 'work_hour': 8},
                'wednesday': {'start_time': '23:00', 'work_hour': 8},
                'thursday': {'start_time': '23:00', 'work_hour': 8},
                'friday': {'start_time': '23:00', 'work_hour': 8},
                'saturday': {'start_time': '23:00', 'work_hour': 8}
            }
        ]
        inst_shift_rule.save()

        inst_staff = self._create_staff()
        ShiftRuleStaffModel.objects.create(
            shift_rule=inst_shift_rule,
            staff=inst_staff,
            shift_no=1
        )

        # salı günü saat 23:00 - çarşamba günü saat 07:00'da  özel vardiya ekle
        work_hour = 8
        start_dt = datetime.datetime.combine(inst_shift_rule.start_date + datetime.timedelta(days=1),
                                             datetime.time(23))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        today_business_day = inst_shift_rule.get_business_day_on_date(start_dt, inst_staff)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _('working hours depending on the shift rule name %(name)s(%(date1)s - %(date2)s)') % {
            'name': inst_shift_rule.name,
            'date1': today_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
            'date2': today_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
        }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_finish_time_of_the_individual_shift_coincides_with_the_working_hours_of_the_shift_the_same_day(self):
        """
            özel vardiyanın çıkış saatinin, aynı gün başlayan vardiyanın çalışma saatleri ile çakışması
        """
        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '23:00', 'work_hour': 8},
                'tuesday': {'start_time': '23:00', 'work_hour': 8},
                'wednesday': {'start_time': '23:00', 'work_hour': 8},
                'thursday': {'start_time': '23:00', 'work_hour': 8},
                'friday': {'start_time': '23:00', 'work_hour': 8},
                'saturday': {'start_time': '23:00', 'work_hour': 8}
            }
        ]
        inst_shift_rule.save()

        inst_staff = self._create_staff()
        ShiftRuleStaffModel.objects.create(
            shift_rule=inst_shift_rule,
            staff=inst_staff,
            shift_no=1
        )

        # salı günü saat 16:00 - çarşamba günü saat 00:00'da  özel vardiya ekle
        work_hour = 8
        start_dt = datetime.datetime.combine(inst_shift_rule.start_date + datetime.timedelta(days=1),
                                             datetime.time(16))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        today_business_day = inst_shift_rule.get_business_day_on_date(start_dt, inst_staff)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _('working hours depending on the shift rule name %(name)s(%(date1)s - %(date2)s)') % {
            'name': inst_shift_rule.name,
            'date1': today_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
            'date2': today_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
        }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_finish_time_of_the_individual_shift_coincides_with_the_working_hours_of_the_shift_the_day_after(self):
        """
            özel vardiyanın çıkış saatinin, bir gün sonraki vardiyanın çalışma saatleri ile çakışması
        """
        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '09:00', 'work_hour': 8},
                'tuesday': {'start_time': '09:00', 'work_hour': 8},
                'wednesday': {'start_time': '09:00', 'work_hour': 8},
                'thursday': {'start_time': '09:00', 'work_hour': 8},
                'friday': {'start_time': '09:00', 'work_hour': 8},
                'saturday': {'start_time': '09:00', 'work_hour': 8}
            }
        ]
        inst_shift_rule.save()

        inst_staff = self._create_staff()
        ShiftRuleStaffModel.objects.create(
            shift_rule=inst_shift_rule,
            staff=inst_staff,
            shift_no=1
        )

        # salı günü saat 23:00 - çarşamba günü saat 11:00'da  özel vardiya ekle
        work_hour = 12
        start_dt = datetime.datetime.combine(inst_shift_rule.start_date + datetime.timedelta(days=1),
                                             datetime.time(23))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        next_day = start_dt + datetime.timedelta(days=1)
        next_business_day = inst_shift_rule.get_business_day_on_date(next_day, inst_staff)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _('working hours depending on the shift rule name %(name)s(%(date1)s - %(date2)s)') % {
            'name': inst_shift_rule.name,
            'date1': next_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
            'date2': next_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
        }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_entry_and_exit_times_of_the_special_shift_cover_the_working_hours_of_the_shift_that_starts_on_the_same_day(
            self):
        """
            özel vardiyanın giriş ve çıkış saatlerinin, aynı gün başlayan vardiyanın çalışma saatlerini kapsaması
        """
        inst_shift_rule = self._create_shift_rule()
        inst_staff = self._create_staff()
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '09:00', 'work_hour': 8},
                'tuesday': {'start_time': '09:00', 'work_hour': 8},
                'wednesday': {'start_time': '09:00', 'work_hour': 8},
                'thursday': {'start_time': '09:00', 'work_hour': 8},
                'friday': {'start_time': '09:00', 'work_hour': 8},
                'saturday': {'start_time': '09:00', 'work_hour': 8}
            }
        ]
        inst_shift_rule.save()

        ShiftRuleStaffModel.objects.create(
            shift_rule=inst_shift_rule,
            staff=inst_staff,
            shift_no=1
        )

        # salı günü saat 07:00 - çarşamba günü saat 22:00'da  özel vardiya ekle
        work_hour = 15
        start_dt = datetime.datetime.combine(inst_shift_rule.start_date + datetime.timedelta(days=1),
                                             datetime.time(7))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        today_business_day = inst_shift_rule.get_business_day_on_date(start_dt, inst_staff)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _('working hours depending on the shift rule name %(name)s(%(date1)s - %(date2)s)') % {
            'name': inst_shift_rule.name,
            'date1': today_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
            'date2': today_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
        }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_entry_and_exit_times_of_the_special_shift_cover_the_working_hours_of_the_shift_that_starts_on_the_day_after(
            self):
        """
            özel vardiyanın giriş ve çıkış saatlerinin, bir gün sonra başlayan vardiyanın çalışma saatlerini kapsaması
        """
        inst_shift_rule = self._create_shift_rule()
        inst_staff = self._create_staff()
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '09:00', 'work_hour': 8},
                'tuesday': {'start_time': '09:00', 'work_hour': 8},
                'wednesday': {'start_time': '09:00', 'work_hour': 8},
                'thursday': {'start_time': '09:00', 'work_hour': 8},
                'friday': {'start_time': '09:00', 'work_hour': 8},
                'saturday': {'start_time': '09:00', 'work_hour': 8}
            }
        ]
        inst_shift_rule.save()

        ShiftRuleStaffModel.objects.create(
            shift_rule=inst_shift_rule,
            staff=inst_staff,
            shift_no=1
        )

        # salı günü saat 23:00 - çarşamba günü saat 19:00'da  özel vardiya ekle
        work_hour = 20
        start_dt = datetime.datetime.combine(inst_shift_rule.start_date + datetime.timedelta(days=1),
                                             datetime.time(23))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        next_day = start_dt + datetime.timedelta(days=1)

        after_business_day = inst_shift_rule.get_business_day_on_date(next_day, inst_staff)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _('working hours depending on the shift rule name %(name)s(%(date1)s - %(date2)s)') % {
            'name': inst_shift_rule.name,
            'date1': after_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
            'date2': after_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
        }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_start_time_of_the_individual_shift_coincides_with_the_working_hours_of_the_business_day_before_day(
            self):
        """
            özel vardiyanın başlama saatinin, bir gün önceki genel mesai çalışma saatleri ile çakışması
        """
        inst_business_day = self._create_business_day()
        monday = {'start_time': '23:00', 'work_hour': 8}
        tuesday = {'start_time': '23:00', 'work_hour': 8}
        wednesday = {'start_time': '23:00', 'work_hour': 8}
        thursday = {'start_time': '23:00', 'work_hour': 8}
        friday = {'start_time': '23:00', 'work_hour': 8}

        inst_business_day.monday = monday
        inst_business_day.tuesday = tuesday
        inst_business_day.wednesday = wednesday
        inst_business_day.thursday = thursday
        inst_business_day.friday = friday
        inst_business_day.save()

        inst_staff = self._create_staff()
        inst_staff.staff_type = inst_business_day.staff_type
        inst_staff.save()

        # salı günü saat 06:00 - 14:00'da başlayan özel vardiya ekle
        start_dt = datetime.datetime.combine(inst_business_day.start_date + datetime.timedelta(days=1),
                                             datetime.time(6))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=8)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = 8

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        before_day_start_dt = start_dt - datetime.timedelta(days=1)
        before_business_day = inst_business_day.get_business_day_on_date(before_day_start_dt)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _(
            'working hours depending on the general business rule name %(name)s(%(date1)s - %(date2)s)') % {
                        'name': inst_business_day.name,
                        'date1': before_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
                        'date2': before_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
                    }

        msg_item += " " + _("with")

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_start_time_of_the_individual_shift_coincides_with_the_working_hours_of_the_business_day_the_same_day(
            self):
        """
            özel vardiyanın başlama saatinin, aynı gün başlayan normal mesai saatleri ile çakışması
        """
        inst_business_day = self._create_business_day()
        monday = {'start_time': '09:00', 'work_hour': 8}
        tuesday = {'start_time': '09:00', 'work_hour': 8}
        wednesday = {'start_time': '09:00', 'work_hour': 8}
        thursday = {'start_time': '09:00', 'work_hour': 8}
        friday = {'start_time': '09:00', 'work_hour': 8}

        inst_business_day.monday = monday
        inst_business_day.tuesday = tuesday
        inst_business_day.wednesday = wednesday
        inst_business_day.thursday = thursday
        inst_business_day.friday = friday
        inst_business_day.save()

        inst_staff = self._create_staff()
        inst_staff.staff_type = inst_business_day.staff_type
        inst_staff.save()

        # salı günü saat 10:00 - 18:00 başlayan özel vardiya ekle
        start_dt = datetime.datetime.combine(inst_business_day.start_date, datetime.time(10))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=8)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = 8

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        today_business_day = inst_business_day.get_business_day_on_date(start_dt)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _(
            'working hours depending on the general business rule name %(name)s(%(date1)s - %(date2)s)') % {
                        'name': inst_business_day.name,
                        'date1': today_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
                        'date2': today_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
                    }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_finish_time_of_the_individual_shift_coincides_with_the_working_hours_of_the_business_day_the_same_day(
            self):
        """
            özel vardiyanın çıkış saatinin, aynı gün başlayan mesai saatleri ile çakışması
        """
        inst_business_day = self._create_business_day()
        monday = {'start_time': '09:00', 'work_hour': 8}
        tuesday = {'start_time': '09:00', 'work_hour': 8}
        wednesday = {'start_time': '09:00', 'work_hour': 8}
        thursday = {'start_time': '09:00', 'work_hour': 8}
        friday = {'start_time': '09:00', 'work_hour': 8}

        inst_business_day.monday = monday
        inst_business_day.tuesday = tuesday
        inst_business_day.wednesday = wednesday
        inst_business_day.thursday = thursday
        inst_business_day.friday = friday
        inst_business_day.save()

        inst_staff = self._create_staff()
        inst_staff.staff_type = inst_business_day.staff_type
        inst_staff.save()

        # salı günü saat 05:00 - 13:00'da başlayan özel vardiya ekle
        work_hour = 8
        start_dt = datetime.datetime.combine(inst_business_day.start_date, datetime.time(5))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        today_business_day = inst_business_day.get_business_day_on_date(start_dt)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _(
            'working hours depending on the general business rule name %(name)s(%(date1)s - %(date2)s)') % {
                        'name': inst_business_day.name,
                        'date1': today_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
                        'date2': today_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
                    }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_finish_time_of_the_individual_shift_coincides_with_the_working_hours_of_the_business_day_after_day(
            self):
        """
            özel vardiyanın çıkış saatinin, bir gün sonraki genel iş günü saatleri ile çakışması
        """
        inst_business_day = self._create_business_day()
        monday = {'start_time': '06:00', 'work_hour': 8}
        tuesday = {'start_time': '06:00', 'work_hour': 8}
        wednesday = {'start_time': '06:00', 'work_hour': 8}
        thursday = {'start_time': '06:00', 'work_hour': 8}
        friday = {'start_time': '06:00', 'work_hour': 8}

        inst_business_day.monday = monday
        inst_business_day.tuesday = tuesday
        inst_business_day.wednesday = wednesday
        inst_business_day.thursday = thursday
        inst_business_day.friday = friday
        inst_business_day.save()

        inst_staff = self._create_staff()
        inst_staff.staff_type = inst_business_day.staff_type
        inst_staff.save()

        # salı günü saat 23:00 - 07:00 özel vardiya ekle
        work_hour = 8
        start_dt = datetime.datetime.combine(inst_business_day.start_date, datetime.time(23))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        next_day = start_dt + datetime.timedelta(days=1)
        next_business_day = inst_business_day.get_business_day_on_date(next_day)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _(
            'working hours depending on the general business rule name %(name)s(%(date1)s - %(date2)s)') % {
                        'name': inst_business_day.name,
                        'date1': next_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
                        'date2': next_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
                    }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_entry_and_exit_times_of_the_special_shift_cover_the_working_hours_of_the_business_day_that_starts_on_the_same_day(
            self):
        """
            özel vardiyanın giriş ve çıkış saatlerinin, aynı gün başlayan genel çalışma saatlerini kapsaması
        """
        inst_business_day = self._create_business_day()
        monday = {'start_time': '09:00', 'work_hour': 8}
        tuesday = {'start_time': '09:00', 'work_hour': 8}
        wednesday = {'start_time': '09:00', 'work_hour': 8}
        thursday = {'start_time': '09:00', 'work_hour': 8}
        friday = {'start_time': '09:00', 'work_hour': 8}

        inst_business_day.monday = monday
        inst_business_day.tuesday = tuesday
        inst_business_day.wednesday = wednesday
        inst_business_day.thursday = thursday
        inst_business_day.friday = friday
        inst_business_day.save()

        inst_staff = self._create_staff()
        inst_staff.staff_type = inst_business_day.staff_type
        inst_staff.save()

        # salı günü saat 08:00 - 00:00 arası özel vardiya ekle
        work_hour = 16
        start_dt = datetime.datetime.combine(inst_business_day.start_date, datetime.time(8))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        today_business_day = inst_business_day.get_business_day_on_date(start_dt)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _(
            'working hours depending on the general business rule name %(name)s(%(date1)s - %(date2)s)') % {
                        'name': inst_business_day.name,
                        'date1': today_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
                        'date2': today_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
                    }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})

    def test_the_entry_and_exit_times_of_the_individual_shift_cover_the_working_hours_of_the_business_day_that_starts_on_the_day_after(
            self):
        """
            özel vardiyanın giriş ve çıkış saatlerinin, bir gün sonra başlayan genel çalışma saatlerini kapsaması
        """
        inst_business_day = self._create_business_day()
        monday = {'start_time': '01:00', 'work_hour': 8}
        tuesday = {'start_time': '01:00', 'work_hour': 8}
        wednesday = {'start_time': '01:00', 'work_hour': 8}
        thursday = {'start_time': '01:00', 'work_hour': 8}
        friday = {'start_time': '01:00', 'work_hour': 8}

        inst_business_day.monday = monday
        inst_business_day.tuesday = tuesday
        inst_business_day.wednesday = wednesday
        inst_business_day.thursday = thursday
        inst_business_day.friday = friday
        inst_business_day.save()

        inst_staff = self._create_staff()
        inst_staff.staff_type = inst_business_day.staff_type
        inst_staff.save()

        # salı günü saat 23:00'da başlayıp, çarşamba 15:00'de biten özel vardiya ekle
        work_hour = 16
        start_dt = datetime.datetime.combine(inst_business_day.start_date, datetime.time(23))
        while start_dt.weekday() != 1:
            start_dt += datetime.timedelta(days=1)
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        data = self._create_post_data()
        data['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M")
        data['work_hour'] = work_hour

        url = reverse('betik_app_staff:custom-shift-create-bulk')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        next_day = start_dt + datetime.timedelta(days=1)
        next_business_day = inst_business_day.get_business_day_on_date(next_day)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
            'id': 1,
            'date1': start_dt.strftime("%d %B %Y %H:%M"),
            'date2': finish_dt.strftime("%d %B %Y %H:%M")
        }

        msg_item += " " + _("with")

        msg_item += " " + _(
            'working hours depending on the general business rule name %(name)s(%(date1)s - %(date2)s)') % {
                        'name': inst_business_day.name,
                        'date1': next_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
                        'date2': next_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
                    }
        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})
