from django.urls import reverse

from betik_app_staff.models import TitleModel
from betik_app_staff.serializers.staff import TitleSerializer
from betik_app_staff.tests.base import TestBase


class TestTitle(TestBase):
    def test_paginate(self):
        self._create_title()
        self._create_title()

        url = reverse('betik_app_staff:title-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = TitleModel.objects.all().order_by('name')
        serializer_dict = TitleSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        self._create_title()
        inst = self._create_title()

        url = reverse('betik_app_staff:title-paginate') + '?name=' + inst.name
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = TitleModel.objects.filter(name__icontains=inst.name).order_by('name')
        serializer_dict = TitleSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = 1
        self.assertEqual(count, response.data['count'])

    def test_create(self):
        post_data = {
            'name': 'Title'
        }

        response = self.client.post(reverse('betik_app_staff:title-create'), post_data)
        self.assertEqual(response.status_code, 201, response.data)

        model = TitleModel.objects.get(id=1)
        serializer_data = TitleSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_data)

    def test_update(self):
        model = self._create_title()

        put_data = {
            'name': 'New Title'
        }

        url = reverse('betik_app_staff:title-update', kwargs={'pk': model.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200, response.data)

        model = TitleModel.objects.get(id=1)
        serializer_data = TitleSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_data)

    def test_delete(self):
        model = TitleModel.objects.create(name='Title')

        url = reverse('betik_app_staff:title-delete', kwargs={'pk': model.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)
