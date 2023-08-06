import datetime

from django.urls import reverse
from django.utils.translation import gettext as _

from betik_app_staff.models import BusinessDayModel
from betik_app_staff.serializers.business_day import BusinessDaySerializer
from betik_app_staff.tests.base import TestBase


class TestBusinessDayBase(TestBase):
    def _create_post_data(self):
        name = self.faker.bothify(text='Business Day-????-###')
        today = datetime.datetime.today().date()
        future = today + datetime.timedelta(days=10)
        staff_type = self._create_staff_type()

        return {
            'name': name,
            'start_date': future.strftime('%Y-%m-%d'),
            'finish_date': None,
            'staff_type_id': staff_type.id,
            'monday': {'start_time': '09:00', 'work_hour': 8},
            'tuesday': {'start_time': '09:00', 'work_hour': 8},
            'wednesday': {'start_time': '09:00', 'work_hour': 8},
            'thursday': {'start_time': '09:00', 'work_hour': 8},
            'friday': {'start_time': '09:00', 'work_hour': 8}
        }


class TestCRUD(TestBusinessDayBase):
    def test_create(self):
        post_data = self._create_post_data()

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        instance = BusinessDayModel.objects.get(id=1)
        serializer_dict = BusinessDaySerializer(instance=instance).data

        self.assertDictEqual(response.data, serializer_dict)

    def test_update(self):
        instance = self._create_business_day(with_finish_date=False)
        put_data = self._create_post_data()

        url = reverse('betik_app_staff:business-day-update', kwargs={'pk': instance.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 200, response.data)

        model = BusinessDayModel.objects.get(id=1)
        serializer_dict = BusinessDaySerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_delete(self):
        today = datetime.datetime.today()
        start_date = today + datetime.timedelta(days=5)
        finish_date = today + datetime.timedelta(days=10)

        instance = self._create_business_day()
        instance.start_date = start_date
        instance.finish_date = finish_date
        instance.save()

        url = reverse('betik_app_staff:business-day-delete', kwargs={'pk': instance.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

        count = BusinessDayModel.objects.count()
        self.assertEqual(0, count)

    def test_paginate(self):
        self._create_business_day()
        self._create_business_day()

        url = reverse('betik_app_staff:business-day-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        instances = BusinessDayModel.objects.all()
        serializer_dict = BusinessDaySerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        self._create_business_day()
        self._create_business_day()

        url = reverse('betik_app_staff:business-day-paginate') + '?staff_type_id=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        count = 1
        self.assertEqual(count, response.data['count'])


class TestCreateFail(TestBusinessDayBase):

    def test_day_start_time_required(self):
        staff_type = self._create_staff_type()
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        post_data = {
            'name': 'Business Day Name',
            'start_date': tomorrow.strftime("%Y-%m-%d"),
            'finish_date': None,
            'staff_type_id': staff_type.id,
            'monday': {'work_hour': 8}
        }

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        msg = _('required')
        self.assertDictEqual(response.data, {'monday': {'start_time': [msg]}})

    def test_day_work_hour_required(self):
        staff_type = self._create_staff_type()
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        post_data = {
            'name': 'Business Day Name',
            'start_date': tomorrow.strftime("%Y-%m-%d"),
            'finish_date': None,
            'staff_type_id': staff_type.id,
            'monday': {'start_time': '10:00'}
        }

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        msg = _('required')
        self.assertDictEqual(response.data, {'monday': {'work_hour': [msg]}})

    def test_day_data_is_incorrect(self):
        staff_type = self._create_staff_type()
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        post_data = {
            'name': 'Business Day Name',
            'start_date': tomorrow.strftime("%Y-%m-%d"),
            'finish_date': None,
            'staff_type_id': staff_type.id,
            'monday': 'w'
        }

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Incorrect type. Expected a dict, but got %s') % type('w').__name__
        self.assertDictEqual(response.data, {'monday': [msg]})

    def test_day_work_hour_must_be_number(self):
        post_data = self._create_post_data()
        post_data['monday']['work_hour'] = 'e'

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must be a number')
        self.assertDictEqual(response.data, {'monday': {'work_hour': [msg]}})

    def test_day_work_hour_bigger_than_zero(self):
        post_data = self._create_post_data()
        post_data['monday']['work_hour'] = 0

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than zero')
        self.assertDictEqual(response.data, {'monday': {'work_hour': [msg]}})

        post_data['monday']['work_hour'] = -1
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'monday': {'work_hour': [msg]}})

    def test_day_work_hour_less_than_25(self):
        post_data = self._create_post_data()
        post_data['monday']['work_hour'] = 25

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('less than 25')
        self.assertDictEqual(response.data, {'monday': {'work_hour': [msg]}})

    def test_day_start_time_is_incorrect_format(self):
        post_data = self._create_post_data()
        post_data['monday']['start_time'] = 25

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Incorrect time format. Expected `%H:%M`')
        self.assertDictEqual(response.data, {'monday': {'start_time': [msg]}})

    def test_require_at_least_one_day(self):
        post_data = self._create_post_data()
        post_data['monday'] = None
        post_data['tuesday'] = None
        post_data['wednesday'] = None
        post_data['thursday'] = None
        post_data['friday'] = None
        post_data['saturday'] = None
        post_data['sunday'] = None

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('required a day at least')
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_finish_date_bigger_then_start_date(self):
        post_data = self._create_post_data()
        start_date = post_data['start_date']
        start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        finish_date = start_date_obj - datetime.timedelta(days=1)
        post_data['finish_date'] = finish_date.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than start date(%(date)s)') % {'date': start_date_obj.strftime('%d %B %Y')}
        self.assertDictEqual(response.data, {'finish_date': [msg]})

    def test_start_date_bigger_than_today(self):
        today = datetime.datetime.today().date()

        post_data = self._create_post_data()
        post_data['start_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'start_date': [msg]})

    def test_finish_date_bigger_than_today(self):
        today = datetime.datetime.today().date()

        post_data = self._create_post_data()
        post_data['finish_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'finish_date': [msg]})

    def test_start_date_of_added_terminated_record_conflicts_with_dates_of_another_previously_added_terminated_record(
            self):
        """
            yeni eklenen sonlandırılmış kaydın başlangıç tarihi, daha önce eklenen başka bir sonlandırılmış kaydın tarihleriyle çakışıyor
        """

        inst = self._create_business_day(with_finish_date=True)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date + datetime.timedelta(days=1)
        finish_date_obj = inst.finish_date + datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:business-day-create')
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

        inst = self._create_business_day(with_finish_date=False)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date + datetime.timedelta(days=1)
        finish_date_obj = inst.start_date + datetime.timedelta(days=100)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:business-day-create')
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

        inst = self._create_business_day(with_finish_date=True)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)
        finish_date_obj = inst.start_date + datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:business-day-create')
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

        inst = self._create_business_day(with_finish_date=False)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)
        finish_date_obj = inst.start_date + datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:business-day-create')
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
        inst = self._create_business_day(with_finish_date=True)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)
        finish_date_obj = inst.finish_date + datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['finish_date'] = finish_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:business-day-create')
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
        inst = self._create_business_day(with_finish_date=True)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:business-day-create')
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
        inst = self._create_business_day(with_finish_date=False)
        post_data = self._create_post_data()

        start_date_obj = inst.start_date - datetime.timedelta(days=1)

        post_data['start_date'] = start_date_obj.strftime("%Y-%m-%d")
        post_data['staff_type_id'] = inst.staff_type.id

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Contains with the dates(%(date1)s and later) of record #%(id)s') % {
            'id': inst.id,
            'date1': inst.start_date.strftime("%d %B %Y")
        }
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_n_finish_time_of_day_n1_conflicts_with_start_time_of_day(self):
        """
            n. günün bitiş saati, (n+1). günün başlangıç saati ile çakışıyor
        """
        post_data = self._create_post_data()

        post_data['monday']['start_time'] = '23:00'
        post_data['monday']['work_hour'] = 20
        post_data['tuesday']['start_time'] = '06:00'

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than or equal %(time)s') % {'time': '19:00'}
        self.assertDictEqual(response.data, {'tuesday': {'start_time': [msg]}})

    def test_finish_time_of_last_day_first_conflicts_with_start_time_of_first_day(self):
        """
            son günün bitiş saati, ilk günün başlangıç saati ile çakışıyor
        """
        post_data = self._create_post_data()

        post_data['sunday'] = {}
        post_data['sunday']['start_time'] = '23:00'
        post_data['sunday']['work_hour'] = 20
        post_data['monday']['start_time'] = '06:00'

        url = reverse('betik_app_staff:business-day-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than or equal %(time)s') % {'time': '19:00'}
        self.assertDictEqual(response.data, {'monday': {'start_time': [msg]}})


class TestUpdateFail(TestBusinessDayBase):
    def test_anything_other_than_finish_date_of_active_registrations_cannot_be_changed(self):
        """
            aktif kayıtların sadece bitiş tarihleri değiştirilebilir
        """
        today = datetime.datetime.today().date()

        inst = self._create_business_day()
        inst.start_date = today
        inst.save()

        put_data = self._create_post_data()
        url = reverse('betik_app_staff:business-day-update', kwargs={'pk': inst.id})
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

        inst = self._create_business_day()
        inst.start_date = yesterday
        inst.finish_date = today
        inst.save()

        put_data = self._create_post_data()
        url = reverse('betik_app_staff:business-day-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('expired records cannot be changed in any way')
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_start_date_bigger_than_today(self):
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        inst = self._create_business_day(with_finish_date=False)
        inst.start_date = tomorrow
        inst.save()

        put_data = self._create_post_data()
        put_data['start_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:business-day-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'start_date': [msg]})

    def test_finish_date_bigger_than_today(self):
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        inst = self._create_business_day(with_finish_date=False)
        inst.start_date = tomorrow
        inst.save()

        put_data = self._create_post_data()
        put_data['finish_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:business-day-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'finish_date': [msg]})


class TestDeleteFail(TestBusinessDayBase):
    def test_active_record_can_not_be_deleted(self):
        """
            aktif kayıt silinemez
        """
        today = datetime.datetime.today().date()

        inst = self._create_business_day()
        inst.start_date = today
        inst.save()

        url = reverse('betik_app_staff:business-day-delete', kwargs={'pk': inst.id})
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

        inst = self._create_business_day()
        inst.start_date = yesterday
        inst.finish_date = today
        inst.save()

        url = reverse('betik_app_staff:business-day-delete', kwargs={'pk': inst.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('outdated record can not be deleted')
        self.assertDictEqual(response.data, {'detail': [msg]})
