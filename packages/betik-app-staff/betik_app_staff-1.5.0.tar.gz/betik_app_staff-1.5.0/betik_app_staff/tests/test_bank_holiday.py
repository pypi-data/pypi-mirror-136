from django.urls import reverse

from betik_app_staff.models import BankHolidayModel
from betik_app_staff.serializers.bank_holiday import BankHolidaySerializer
from betik_app_staff.tests.base import TestBase


class TestBankHoliday(TestBase):
    def test_create(self):
        post_data = {
            'name': 'Name',
            'month': 2,
            'day': 1,
            'start_date': '2020-01-01'
        }

        url = reverse('betik_app_staff:bank-holiday-create')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201, response.data)

        instance = BankHolidayModel.objects.get(id=1)
        serializer_dict = BankHolidaySerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_update(self):
        instance = self._create_bank_holiday()

        put_data = {
            'name': 'New Name',
            'month': 2,
            'day': 1,
            'start_date': '2020-01-01'
        }

        url = reverse('betik_app_staff:bank-holiday-update', kwargs={'pk': instance.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200, response.data)

        model = BankHolidayModel.objects.get(id=1)
        serializer_dict = BankHolidaySerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_delete(self):
        instance = self._create_bank_holiday()

        url = reverse('betik_app_staff:bank-holiday-delete', kwargs={'pk': instance.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

        count = BankHolidayModel.objects.count()
        self.assertEqual(0, count)

    def test_paginate(self):
        self._create_bank_holiday()
        self._create_bank_holiday()

        url = reverse('betik_app_staff:bank-holiday-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = BankHolidayModel.objects.all().order_by('name')
        serializer_dict = BankHolidaySerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        self._create_bank_holiday(name='first holiday')
        self._create_bank_holiday(name='second holiday')

        url = reverse('betik_app_staff:bank-holiday-paginate') + '?name=first'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        count = 1
        self.assertEqual(count, response.data['count'])
