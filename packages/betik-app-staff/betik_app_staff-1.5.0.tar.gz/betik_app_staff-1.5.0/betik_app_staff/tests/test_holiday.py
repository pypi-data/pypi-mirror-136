from django.urls import reverse

from betik_app_staff.models import HolidayModel
from betik_app_staff.serializers.holiday import HolidaySerializer
from betik_app_staff.tests.base import TestBase


class TestHoliday(TestBase):
    def test_create(self):
        post_data = {
            'name': 'Name',
            'start_date': '2020-01-01',
            'finish_date': '2020-01-02'
        }

        url = reverse('betik_app_staff:holiday-create')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201, response.data)

        instance = HolidayModel.objects.get(id=1)
        serializer_dict = HolidaySerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_update(self):
        instance = self._create_holiday()

        put_data = {
            'name': 'New Name',
            'start_date': '2020-01-01',
            'finish_date': '2020-01-02'
        }

        url = reverse('betik_app_staff:holiday-update', kwargs={'pk': instance.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200, response.data)

        model = HolidayModel.objects.get(id=1)
        serializer_dict = HolidaySerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_delete(self):
        instance = self._create_holiday()

        url = reverse('betik_app_staff:holiday-delete', kwargs={'pk': instance.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

        count = HolidayModel.objects.count()
        self.assertEqual(0, count)

    def test_paginate(self):
        self._create_holiday()
        self._create_holiday()

        url = reverse('betik_app_staff:holiday-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = HolidayModel.objects.all().order_by('-start_date', 'name')
        serializer_dict = HolidaySerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        self._create_holiday(name='first holiday')
        self._create_holiday(name='second holiday')

        url = reverse('betik_app_staff:holiday-paginate') + '?name=first'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        count = 1
        self.assertEqual(count, response.data['count'])
