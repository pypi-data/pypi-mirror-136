import datetime

from django.urls import reverse
from django.utils.translation import gettext as _

from betik_app_staff.enums import AnnualLeaveDurationEnum
from betik_app_staff.models import AnnualLeaveRuleModel
from betik_app_staff.serializers.annual_leave_rule import AnnualLeaveRuleSerializer
from betik_app_staff.tests.base import TestBase


class TestAnnualLeaveRuleBase(TestBase):
    def _create_post_data(self, with_finish_date=False):
        today = datetime.datetime.today().date()
        start_date = today + datetime.timedelta(days=10)
        staff_type = self._create_staff_type()

        finish_date = None
        if with_finish_date:
            finish_date = start_date + datetime.timedelta(days=10)
            finish_date = finish_date.strftime('%Y-%m-%d')

        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'finish_date': finish_date,
            'staff_type_id': staff_type.id,
            'periods': [
                {'start_year': 1, 'finish_year': 5, 'duration': 10},
                {'start_year': 5, 'finish_year': None, 'duration': 10}
            ],
            'duration_type_code': AnnualLeaveDurationEnum.DAY,
            'forward_next_year': True,
            'forward_year': 1
        }


class TestCRUD(TestAnnualLeaveRuleBase):
    def test_create(self):
        post_data = self._create_post_data()

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        instance = AnnualLeaveRuleModel.objects.get(id=1)
        serializer_dict = AnnualLeaveRuleSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_update(self):
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        instance = self._create_annual_leave_rule()
        instance.start_date = tomorrow
        instance.save()

        put_data = self._create_post_data()
        put_data['staff_type_id'] = instance.staff_type.id

        url = reverse('betik_app_staff:annual-leave-rule-update', kwargs={'pk': instance.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 200, response.data)

        model = AnnualLeaveRuleModel.objects.get(id=1)
        serializer_dict = AnnualLeaveRuleSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_delete(self):
        instance = self._create_annual_leave_rule(with_finish_date=False)

        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)
        instance.start_date = tomorrow
        instance.save()

        url = reverse('betik_app_staff:annual-leave-rule-delete', kwargs={'pk': instance.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

        count = AnnualLeaveRuleModel.objects.count()
        self.assertEqual(0, count)

    def test_paginate(self):
        self._create_annual_leave_rule()
        self._create_annual_leave_rule()

        url = reverse('betik_app_staff:annual-leave-rule-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = AnnualLeaveRuleModel.objects.all().order_by('-start_date', 'staff_type')
        serializer_dict = AnnualLeaveRuleSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        self._create_annual_leave_rule()
        self._create_annual_leave_rule()

        url = reverse('betik_app_staff:annual-leave-rule-paginate') + '?staff_type_id=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        count = 1
        self.assertEqual(count, response.data['count'])


class TestCreateFail(TestAnnualLeaveRuleBase):
    def test_period_start_year_required(self):
        post_data = self._create_post_data()
        post_data['periods'][0]['start_year'] = None

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('required')
        self.assertDictEqual(response.data, {'periods': {0: {'start_year': [msg]}}})

    def test_period_duration_required(self):
        post_data = self._create_post_data()
        post_data['periods'][0]['duration'] = None

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('required')
        self.assertDictEqual(response.data, {'periods': {0: {'duration': [msg]}}})

    def test_period_start_year_must_be_number(self):
        post_data = self._create_post_data()
        post_data['periods'][0]['start_year'] = 'we'

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must be number')
        self.assertDictEqual(response.data, {'periods': {0: {'start_year': [msg]}}})

    def test_period_finish_year_must_be_number(self):
        post_data = self._create_post_data()
        post_data['periods'][0]['finish_year'] = 'we'

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must be number')
        self.assertDictEqual(response.data, {'periods': {0: {'finish_year': [msg]}}})

    def test_period_duration_must_be_number(self):
        post_data = self._create_post_data()
        post_data['periods'][0]['duration'] = 'we'

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must be number')
        self.assertDictEqual(response.data, {'periods': {0: {'duration': [msg]}}})

    def test_period_start_year_must_be_bigger_than_or_equal_zero(self):
        post_data = self._create_post_data()
        post_data['periods'][0]['start_year'] = -1

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must be bigger than or equal zero')
        self.assertDictEqual(response.data, {'periods': {0: {'start_year': [msg]}}})

    def test_period_finish_year_must_be_bigger_than_zero(self):
        post_data = self._create_post_data()
        post_data['periods'][0]['finish_year'] = 0

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must be bigger than 0')
        self.assertDictEqual(response.data, {'periods': {0: {'finish_year': [msg]}}})

    def test_period_duration_must_be_bigger_than_or_equal_zero(self):
        post_data = self._create_post_data()
        post_data['periods'][0]['duration'] = -1

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must be bigger than or equal 0')
        self.assertDictEqual(response.data, {'periods': {0: {'duration': [msg]}}})

    def test_period_finish_year_must_be_bigger_than_start_year(self):
        post_data = self._create_post_data()
        post_data['periods'] = [
            {'start_year': 10, 'finish_year': 5, 'duration': 10}
        ]

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must be bigger than start year(%(v)d)') % {'v': 10}
        self.assertDictEqual(response.data, {'periods': {0: {'finish_year': [msg]}}})

    def test_period_finish_year_must_be_set(self):
        post_data = self._create_post_data()
        post_data['periods'] = [
            {'start_year': 10, 'finish_year': None, 'duration': 10},
            {'start_year': 1, 'finish_year': 5, 'duration': 10}
        ]

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _("must be set a year")
        self.assertDictEqual(response.data, {'periods': {0: {'finish_year': [msg]}}})

    def test_period_n_with_finish_year_of_period_n1_starting_year_of_period_must_be_the_same(self):
        """
            n. dönemin bitiş yılı ile (n+1). dönemin başlangıç yılı aynı olmalıdır
        """
        post_data = self._create_post_data()
        post_data['periods'] = [
            {'start_year': 1, 'finish_year': 5, 'duration': 10},
            {'start_year': 6, 'finish_year': None, 'duration': 10}
        ]

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _("must be equal to %(p)d. period's finish year(%(year)d)") % {
            'p': 1,
            'year': 5
        }
        self.assertDictEqual(response.data, {'periods': {1: {'start_year': [msg]}}})

    def test_finish_date_bigger_then_start_date(self):
        post_data = self._create_post_data()
        start_date = post_data['start_date']
        start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        finish_date = start_date_obj - datetime.timedelta(days=1)
        post_data['finish_date'] = finish_date.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than start date(%(date)s)') % {'date': start_date_obj.strftime('%d %B %Y')}
        self.assertDictEqual(response.data, {'finish_date': [msg]})

    def test_start_date_bigger_than_today(self):
        today = datetime.datetime.today().date()

        post_data = self._create_post_data()
        post_data['start_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'start_date': [msg]})

    def test_finish_date_bigger_than_today(self):
        today = datetime.datetime.today().date()

        post_data = self._create_post_data()
        post_data['finish_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'finish_date': [msg]})

    def test_start_date_of_added_terminated_record_conflicts_with_dates_of_another_previously_added_terminated_record(
            self):
        """
            yeni eklenen sonlandırılmış kaydın başlangıç tarihi, daha önce eklenen başka bir sonlandırılmış kaydın tarihleriyle çakışıyor
        """

        inst = self._create_annual_leave_rule(with_finish_date=True)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date + datetime.timedelta(days=1)
        finish_date_obj = inst.finish_date + datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Conflicts with the dates(%(date1)s - %(date1)s) of record #%(id)s') % {
            'id': inst.id,
            'date1': inst.start_date.strftime("%d %B %Y"),
            'date2': inst.finish_date.strftime("%d %B %Y")
        }
        self.assertDictEqual(response.data, {'start_date': [msg]})

    def test_start_date_of_added_terminated_record_conflicts_with_dates_of_another_previously_added_not_terminated_record(
            self):
        """
            yeni eklenen sonlandırılmış kaydın başlangıç tarihi, daha önce eklenen başka bir sonlandırılmamış kaydın tarihleriyle çakışıyor
        """

        inst = self._create_annual_leave_rule(with_finish_date=False)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date + datetime.timedelta(days=1)
        finish_date_obj = inst.start_date + datetime.timedelta(days=100)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Conflicts with the dates(%(date1)s and later) of record #%(id)s') % {
            'id': inst.id,
            'date1': inst.start_date.strftime("%d %B %Y")
        }
        self.assertDictEqual(response.data, {'start_date': [msg]})

    def test_finish_date_of_added_terminated_record_conflicts_with_dates_of_another_previously_added_terminated_record(
            self):
        """
            yeni eklenen sonlandırılmış kaydın bitiş tarihi, daha önce eklenen başka bir sonlandırılmış kaydın tarihleriyle çakışıyor
        """

        inst = self._create_annual_leave_rule(with_finish_date=True)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)
        finish_date_obj = inst.start_date + datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Conflicts with the dates(%(date1)s - %(date1)s) of record #%(id)s') % {
            'id': inst.id,
            'date1': inst.start_date.strftime("%d %B %Y"),
            'date2': inst.finish_date.strftime("%d %B %Y")
        }
        self.assertDictEqual(response.data, {'finish_date': [msg]})

    def test_finish_date_of_added_terminated_record_conflicts_with_dates_of_another_previously_added_not_terminated_record(
            self):
        """
            yeni eklenen sonlandırılmış kaydın bitiş tarihi, daha önce eklenen başka bir sonlandırılmamış kaydın tarihleriyle çakışıyor
        """

        inst = self._create_annual_leave_rule(with_finish_date=False)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)
        finish_date_obj = inst.start_date + datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Conflicts with the dates(%(date1)s and later) of record #%(id)s') % {
            'id': inst.id,
            'date1': inst.start_date.strftime("%d %B %Y")
        }
        self.assertDictEqual(response.data, {'finish_date': [msg]})

    def test_dates_of_added_terminated_record_contain_dates_of_another_previously_added_terminated_record(self):
        """
            eklenen sonlandırılmış kaydın tarihleri, daha önce eklenen sonlandırılmış başka bir kaydın tarihlerini içerir
        """
        inst = self._create_annual_leave_rule(with_finish_date=True)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)
        finish_date_obj = inst.finish_date + datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Contains with the dates(%(date1)s - %(date2)s) of record #%(id)s') % {
            'id': inst.id,
            'date1': inst.start_date.strftime("%d %B %Y"),
            'date2': inst.finish_date.strftime("%d %B %Y")
        }
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_dates_of_added_not_terminated_record_contain_dates_of_another_previously_added_terminated_record(self):
        """
            eklenen sonlandırılmamış kaydın tarihleri, daha önce eklenen sonlandırılmış başka bir kaydın tarihlerini içerir
        """
        inst = self._create_annual_leave_rule(with_finish_date=True)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Contains with the dates(%(date1)s - %(date2)s) of record #%(id)s') % {
            'id': inst.id,
            'date1': inst.start_date.strftime("%d %B %Y"),
            'date2': inst.finish_date.strftime("%d %B %Y")
        }
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_dates_of_added_not_terminated_record_contain_dates_of_another_previously_added_not_terminated_record(self):
        """
            eklenen sonlandırılmamış kaydın tarihleri, daha önce eklenen sonlandırılmamış başka bir kaydın tarihlerini içerir
        """
        inst = self._create_annual_leave_rule(with_finish_date=False)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:annual-leave-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Contains with the dates(%(date1)s and later) of record #%(id)s') % {
            'id': inst.id,
            'date1': inst.start_date.strftime("%d %B %Y")
        }
        self.assertDictEqual(response.data, {'detail': [msg]})


class TestUpdateFail(TestAnnualLeaveRuleBase):
    def test_anything_other_than_finish_date_of_active_registrations_cannot_be_changed(self):
        """
            aktif kayıtların sadece bitiş tarihleri değiştirilebilir
        """
        today = datetime.datetime.today().date()

        inst = self._create_annual_leave_rule()
        inst.start_date = today
        inst.save()

        put_data = self._create_post_data()
        url = reverse('betik_app_staff:annual-leave-rule-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Anything other than the finish date of active registrations cannot be changed')
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_expired_records_cannot_be_changed_in_any_way(self):
        """
            geçmişte kalan kayıtlar değiştirilemez
        """
        today = datetime.datetime.today().date()
        yesterday = today - datetime.timedelta(days=1)

        inst = self._create_annual_leave_rule()
        inst.start_date = yesterday
        inst.finish_date = today
        inst.save()

        put_data = self._create_post_data()
        url = reverse('betik_app_staff:annual-leave-rule-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('expired records cannot be changed in any way')
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_start_date_bigger_than_today(self):
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        inst = self._create_annual_leave_rule(with_finish_date=False)
        inst.start_date = tomorrow
        inst.save()

        put_data = self._create_post_data()
        put_data['start_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:annual-leave-rule-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'start_date': [msg]})

    def test_finish_date_bigger_than_today(self):
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        inst = self._create_annual_leave_rule(with_finish_date=False)
        inst.start_date = tomorrow
        inst.save()

        put_data = self._create_post_data()
        put_data['finish_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:annual-leave-rule-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'finish_date': [msg]})


class TestDeleteFail(TestBase):
    def test_active_record_can_not_be_deleted(self):
        """
            aktif kayıt silinemez
        """
        today = datetime.datetime.today().date()

        inst = self._create_annual_leave_rule()
        inst.start_date = today
        inst.save()

        url = reverse('betik_app_staff:annual-leave-rule-delete', kwargs={'pk': inst.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('active record can not be deleted')
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_outdated_record_can_not_be_deleted(self):
        """
            geçmişte kalan kayıt silinemez
        """
        today = datetime.datetime.today().date()
        yesterday = today - datetime.timedelta(days=1)

        inst = self._create_annual_leave_rule()
        inst.start_date = yesterday
        inst.finish_date = today
        inst.save()

        url = reverse('betik_app_staff:annual-leave-rule-delete', kwargs={'pk': inst.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('outdated record can not be deleted')
        self.assertDictEqual(response.data, {'detail': [msg]})
