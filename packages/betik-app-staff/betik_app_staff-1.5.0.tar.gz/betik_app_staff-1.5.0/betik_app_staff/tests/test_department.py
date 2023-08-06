import json

from django.urls import reverse

from betik_app_staff.models import DepartmentModel, StaffModel
from betik_app_staff.serializers.staff import DepartmentSerializer
from betik_app_staff.tests.base import TestBase


class TestCRUD(TestBase):

    def test_paginate(self):
        self._create_department()
        self._create_department()

        url = reverse('betik_app_staff:department-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = DepartmentModel.objects.all().order_by('name')
        serializer_dict = DepartmentSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        self._create_department()
        inst = self._create_department()

        url = reverse('betik_app_staff:department-paginate') + '?name=' + inst.name
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        instances = DepartmentModel.objects.filter(name__icontains=inst.name).order_by('name')
        serializer_dict = DepartmentSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = 1
        self.assertEqual(count, response.data['count'])

    def test_create(self):
        post_data = {
            'name': 'Department'
        }

        url = reverse('betik_app_staff:department-create')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201, response.data)

        model = DepartmentModel.objects.get(id=1)
        serializer_data = DepartmentSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_data)

    def test_update(self):
        model = self._create_department()

        put_data = {
            'name': 'New Department'
        }

        url = reverse('betik_app_staff:department-update', kwargs={'pk': model.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200, response.data)

        model = DepartmentModel.objects.get(id=1)
        serializer_data = DepartmentSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_data)

    def test_delete(self):
        model = DepartmentModel.objects.create(name='Department')

        url = reverse('betik_app_staff:department-delete', kwargs={'pk': model.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_merge(self):
        # bu method içinde department oluşturuluyor pk=1
        self._create_staff()
        model_target = DepartmentModel.objects.create(name='Department')

        put_data = {
            'source_ids': [1]
        }

        url = reverse('betik_app_staff:department-merge', kwargs={'pk': model_target.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        self.assertDictEqual(content_json, {'result': True})

        staff_instance = StaffModel.objects.get(id=1)
        self.assertEqual(staff_instance.department.id, model_target.id)

        count = DepartmentModel.objects.count()
        self.assertEqual(1, count)
