import datetime

from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils.translation import gettext as _
from freezegun import freeze_time

from betik_app_staff.models import ShiftRuleStaffModel, StaffModel
from betik_app_staff.serializers.staff import StaffSerializer
from betik_app_staff import tasks
from betik_app_staff.tests.base import TestBase


class TestShiftRuleStaff(TestBase):
    pass


class TestAssignPaginateRemove(TestShiftRuleStaff):
    def test_assign(self):
        inst_staff = self._create_staff()
        inst_shift_rule = self._create_shift_rule()

        url = reverse('betik_app_staff:shift-rule-assign-bulk-staff')
        data = {
            'shift_no': 1,
            'shift_rule_id': inst_shift_rule.id
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 202, response.data)

        self.assertDictEqual(response.data, {'result': True})

    def test_paginate_staff_who_depends_on_shift_rule(self):
        """
            vardiya kuralına bağlı personelleri sayfala
        """
        inst_staff1 = self._create_staff()
        inst_staff2 = self._create_staff()
        inst_shift_rule = self._create_shift_rule()

        ShiftRuleStaffModel.objects.bulk_create([
            ShiftRuleStaffModel(staff=inst_staff1, shift_rule=inst_shift_rule, shift_no=1),
            ShiftRuleStaffModel(staff=inst_staff2, shift_rule=inst_shift_rule, shift_no=2)
        ])

        kwarg = {
            'shift_rule_id': inst_shift_rule.id,
            'shift_no': 1
        }
        url = reverse('betik_app_staff:staff-paginate-by-shift', kwargs=kwarg)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        list_staffs = StaffModel.objects.filter(id=inst_staff1.id)
        ser_data = StaffSerializer(instance=list_staffs, many=True).data
        self.assertListEqual(response.data['results'], ser_data)

    def test_remove_staff_from_shift_rule(self):
        """
            personeli vardiyadan çıkar
        """
        inst_staff1 = self._create_staff()
        inst_staff2 = self._create_staff()
        inst_shift_rule = self._create_shift_rule()

        ShiftRuleStaffModel.objects.bulk_create([
            ShiftRuleStaffModel(staff=inst_staff1, shift_rule=inst_shift_rule, shift_no=1),
            ShiftRuleStaffModel(staff=inst_staff2, shift_rule=inst_shift_rule, shift_no=2)
        ])

        kwarg = {
            'shift_rule_id': inst_shift_rule.id,
            'staff_id': inst_staff1.id
        }
        url = reverse('betik_app_staff:shift-rule-remove-staff', kwargs=kwarg)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

        count = ShiftRuleStaffModel.objects.count()
        self.assertEqual(count, 1)


class TestAssignFail(TestShiftRuleStaff):
    def test_no_action_can_be_taken_for_an_out_of_date_shift_rule(self):
        """
            tarihi geçmiş vardiya kuralına personel eklenemez
        """
        inst_staff = self._create_staff()

        today = datetime.datetime.today().date()
        yesterday = today - datetime.timedelta(days=1)
        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.start_date = yesterday
        inst_shift_rule.finish_date = today
        inst_shift_rule.save()

        url = reverse('betik_app_staff:shift-rule-assign-bulk-staff')
        data = {
            'shift_no': 1,
            'shift_rule_id': inst_shift_rule.id
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('No action can be taken for an out-of-date shift rule')
        self.assertDictEqual(response.data, {'shift_rule_id': [msg]})

    def test_shift_number_should_have_these_values(self):
        """
            personelin atandığı vardiya numarası, seçilen vardiya kuralında olmalı
        """
        inst_staff = self._create_staff()
        inst_shift_rule = self._create_shift_rule()

        url = reverse('betik_app_staff:shift-rule-assign-bulk-staff')
        data = {
            'shift_no': 10,
            'shift_rule_id': inst_shift_rule.id
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        shift_nos = []
        for bd in inst_shift_rule.business_days:
            shift_nos.append(bd.get('shift_no'))
        msg = _('The shift number should have the these values; %(values)s') % {
            'values': ", ".join(str(shift_nos))
        }
        self.assertDictEqual(response.data, {'shift_no': [msg]})

    def test_if_staff_is_in_same_shifts_another_period_do_not_allow_change_if_shift_rule_is_active(self):
        """
            Personel aynı vardiyanın başka bir döneminde ise, vardiya kuralı aktif ise, dönem değişikliğine izin verme.
        """
        inst_staff = self._create_staff()

        today = datetime.datetime.today().date()
        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.start_date = today
        inst_shift_rule.finish_date = None
        inst_shift_rule.save()

        inst_shift_staff = ShiftRuleStaffModel.objects.create(
            staff=inst_staff,
            shift_rule=inst_shift_rule,
            shift_no=1
        )

        url = reverse('betik_app_staff:shift-rule-assign-bulk-staff')
        data = {
            'shift_no': 2,
            'shift_rule_id': inst_shift_rule.id
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _(
            'Staff who %(identity)s identity, named %(name)s %(last_name)s, are already registered in the %(shift_no)d. shift no of this shift.') % {
                  'shift_no': inst_shift_staff.shift_no,
                  'identity': inst_shift_staff.staff.person.identity,
                  'name': inst_shift_staff.staff.person.name,
                  'last_name': inst_shift_staff.staff.person.last_name
              }
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_if_staff_is_registered_in_another_shift_dates_of_this_shift_and_shift_to_be_assigned_should_not_conflict(
            self):
        """
            Personel başka bir vardiyada kayıtlı ise bu vardiya ile atanacak vardiya tarihleri çakışmamalıdır.
        """
        inst_staff = self._create_staff()

        today = datetime.datetime.today().date()
        yesterday = today - datetime.timedelta(days=1)
        inst_shift_rule1 = self._create_shift_rule()
        inst_shift_rule1.start_date = yesterday
        inst_shift_rule1.finish_date = None
        inst_shift_rule1.save()

        inst_shift_rule2 = self._create_shift_rule()
        inst_shift_rule2.start_date = today
        inst_shift_rule2.finish_date = None
        inst_shift_rule2.save()

        inst_shift_staff = ShiftRuleStaffModel.objects.create(
            staff=inst_staff,
            shift_rule=inst_shift_rule1,
            shift_no=1
        )

        url = reverse('betik_app_staff:shift-rule-assign-bulk-staff')
        data = {
            'shift_no': 2,
            'shift_rule_id': inst_shift_rule2.id
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _(
            'Staff who %(identity)s identity, named %(name)s %(last_name)s, is registered to the shift named %(registered_shift_name)s. the dates of this shift conflict with the dates of the shift named %(new_shift_name)s') % {
                  'identity': inst_shift_staff.staff.person.identity,
                  'name': inst_shift_staff.staff.person.name,
                  'last_name': inst_shift_staff.staff.person.last_name,
                  'registered_shift_name': inst_shift_staff.shift_rule.name,
                  'new_shift_name': inst_shift_rule2.name
              }
        self.assertDictEqual(response.data, {'detail': [msg]})


class TestRemoveStaffFail(TestShiftRuleStaff):
    def test_outdated_record_can_not_be_deleted(self):
        """
            eski vardiyadan personel çıkarılmaz
        """
        today = datetime.datetime.today()
        start_date = today - relativedelta(months=1)
        finish_date = start_date + datetime.timedelta(days=1)

        inst_staff1 = self._create_staff()
        inst_staff2 = self._create_staff()

        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.start_date = start_date
        inst_shift_rule.finish_date = finish_date
        inst_shift_rule.save()

        ShiftRuleStaffModel.objects.bulk_create([
            ShiftRuleStaffModel(staff=inst_staff1, shift_rule=inst_shift_rule, shift_no=1),
            ShiftRuleStaffModel(staff=inst_staff2, shift_rule=inst_shift_rule, shift_no=2)
        ])

        kwarg = {
            'shift_rule_id': inst_shift_rule.id,
            'staff_id': inst_staff1.id
        }
        url = reverse('betik_app_staff:shift-rule-remove-staff', kwargs=kwarg)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('outdated record can not be deleted')
        self.assertDictEqual(response.data, {'detail': [msg]})


@freeze_time("2021-12-06")
class TestChangeShiftRulePeriod(TestShiftRuleStaff):
    def test_change_period_on_date(self):
        today = datetime.datetime.today().date()

        inst_staff1 = self._create_staff()
        inst_staff2 = self._create_staff()
        inst_staff3 = self._create_staff()
        inst_staff4 = self._create_staff()

        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.start_date = today - datetime.timedelta(weeks=5)
        inst_shift_rule.finish_date = None
        inst_shift_rule.period_start_date = today - datetime.timedelta(weeks=1)
        inst_shift_rule.period_end_date = today
        inst_shift_rule.save()

        ShiftRuleStaffModel.objects.bulk_create([
            ShiftRuleStaffModel(shift_rule=inst_shift_rule, staff=inst_staff1, shift_no=1),
            ShiftRuleStaffModel(shift_rule=inst_shift_rule, staff=inst_staff2, shift_no=2),
            ShiftRuleStaffModel(shift_rule=inst_shift_rule, staff=inst_staff3, shift_no=3),
            ShiftRuleStaffModel(shift_rule=inst_shift_rule, staff=inst_staff4, shift_no=4)
        ])

        self.assertEqual(datetime.date(2021, 11, 29), inst_shift_rule.period_start_date)
        self.assertEqual(datetime.date(2021, 12, 6), inst_shift_rule.period_end_date)

        tasks.change_shift_period()
        inst_shift_rule.refresh_from_db()

        staff1_shift_no = ShiftRuleStaffModel.objects.get(shift_rule=inst_shift_rule, staff=inst_staff1).shift_no
        staff2_shift_no = ShiftRuleStaffModel.objects.get(shift_rule=inst_shift_rule, staff=inst_staff2).shift_no
        staff3_shift_no = ShiftRuleStaffModel.objects.get(shift_rule=inst_shift_rule, staff=inst_staff3).shift_no
        staff4_shift_no = ShiftRuleStaffModel.objects.get(shift_rule=inst_shift_rule, staff=inst_staff4).shift_no

        self.assertEqual(2, staff1_shift_no)
        self.assertEqual(3, staff2_shift_no)
        self.assertEqual(4, staff3_shift_no)
        self.assertEqual(1, staff4_shift_no)
        self.assertEqual(datetime.date(2021, 12, 6), inst_shift_rule.period_start_date)
        self.assertEqual(datetime.date(2021, 12, 20), inst_shift_rule.period_end_date)

        tasks.change_shift_period()
        inst_shift_rule.refresh_from_db()

        staff1_shift_no = ShiftRuleStaffModel.objects.get(shift_rule=inst_shift_rule, staff=inst_staff1).shift_no
        staff2_shift_no = ShiftRuleStaffModel.objects.get(shift_rule=inst_shift_rule, staff=inst_staff2).shift_no
        staff3_shift_no = ShiftRuleStaffModel.objects.get(shift_rule=inst_shift_rule, staff=inst_staff3).shift_no
        staff4_shift_no = ShiftRuleStaffModel.objects.get(shift_rule=inst_shift_rule, staff=inst_staff4).shift_no

        self.assertEqual(2, staff1_shift_no)
        self.assertEqual(3, staff2_shift_no)
        self.assertEqual(4, staff3_shift_no)
        self.assertEqual(1, staff4_shift_no)
        self.assertEqual(datetime.date(2021, 12, 6), inst_shift_rule.period_start_date)
        self.assertEqual(datetime.date(2021, 12, 20), inst_shift_rule.period_end_date)
