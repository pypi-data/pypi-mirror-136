import datetime
import json

from betik_app_person.enums import GenderTypeEnum
from betik_app_person.models import NaturalPersonModel
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from betik_app_staff.models import DepartmentModel, TitleModel, StaffTypeModel, StaffModel
from betik_app_staff.serializers import DepartmentSerializer, TitleSerializer, StaffTypeSerializer, StaffSerializer


class TestBase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        super().setUp()
        self.client = APIClient()


class TestDepartment(TestBase):
    def test_list(self):
        DepartmentModel.objects.create(name='Department')
        department_qs = DepartmentModel.objects.all()
        department_list = DepartmentSerializer(instance=department_qs, many=True).data

        response = self.client.get(reverse('department-list'))
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        self.assertListEqual(content_json, department_list)

    def test_create(self):
        post_data = {
            'name': 'Department'
        }

        response = self.client.post(reverse('department-create'), post_data)
        self.assertEqual(response.status_code, 201)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        model = DepartmentModel.objects.get(id=1)
        serializer_data = DepartmentSerializer(instance=model).data
        self.assertEqual(content_json, serializer_data)

    def test_update(self):
        model = DepartmentModel.objects.create(name='Department')

        put_data = {
            'name': 'New Department'
        }

        response = self.client.put(reverse('department-update', kwargs={'pk': model.id}), put_data)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        model = DepartmentModel.objects.get(id=1)
        serializer_data = DepartmentSerializer(instance=model).data
        self.assertEqual(content_json, serializer_data)

    def test_delete(self):
        model = DepartmentModel.objects.create(name='Department')

        response = self.client.delete(reverse('department-delete', kwargs={'pk': model.id}))
        self.assertEqual(response.status_code, 204)


class TestTitle(TestBase):
    def test_list(self):
        TitleModel.objects.create(name='Title')
        title_qs = TitleModel.objects.all()
        title_list = TitleSerializer(instance=title_qs, many=True).data

        response = self.client.get(reverse('title-list'))
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        self.assertListEqual(content_json, title_list)

    def test_create(self):
        post_data = {
            'name': 'Title'
        }

        response = self.client.post(reverse('title-create'), post_data)
        self.assertEqual(response.status_code, 201)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        model = TitleModel.objects.get(id=1)
        serializer_data = TitleSerializer(instance=model).data
        self.assertEqual(content_json, serializer_data)

    def test_update(self):
        model = TitleModel.objects.create(name='Title')

        put_data = {
            'name': 'New Title'
        }

        response = self.client.put(reverse('title-update', kwargs={'pk': model.id}), put_data)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        model = TitleModel.objects.get(id=1)
        serializer_data = TitleSerializer(instance=model).data
        self.assertEqual(content_json, serializer_data)

    def test_delete(self):
        model = TitleModel.objects.create(name='Title')

        response = self.client.delete(reverse('title-delete', kwargs={'pk': model.id}))
        self.assertEqual(response.status_code, 204)


class TestStaffType(TestBase):
    def test_list(self):
        StaffTypeModel.objects.create(name='Title')
        staff_type_qs = StaffTypeModel.objects.all()
        staff_type_list = StaffTypeSerializer(instance=staff_type_qs, many=True).data

        response = self.client.get(reverse('staff-type-list'))
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        self.assertListEqual(content_json, staff_type_list)

    def test_create(self):
        post_data = {
            'name': 'Staff Type'
        }

        response = self.client.post(reverse('staff-type-create'), post_data)
        self.assertEqual(response.status_code, 201)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        model = StaffTypeModel.objects.get(id=1)
        serializer_data = StaffTypeSerializer(instance=model).data
        self.assertEqual(content_json, serializer_data)

    def test_update(self):
        model = StaffTypeModel.objects.create(name='staff Type')

        put_data = {
            'name': 'New Staff Type'
        }

        response = self.client.put(reverse('staff-type-update', kwargs={'pk': model.id}), put_data)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        model = StaffTypeModel.objects.get(id=1)
        serializer_data = StaffTypeSerializer(instance=model).data
        self.assertEqual(content_json, serializer_data)

    def test_delete(self):
        model = StaffTypeModel.objects.create(name='Staff Type')

        response = self.client.delete(reverse('staff-type-delete', kwargs={'pk': model.id}))
        self.assertEqual(response.status_code, 204)


class TestStaff(TestBase):
    def test_paginate(self):
        now = datetime.datetime.now()
        person_model = NaturalPersonModel.objects.create(identity="1234567890", name="Person Name",
                                                         last_name="Person Last Name", gender=GenderTypeEnum.MALE)
        department_model = DepartmentModel.objects.create(name="Department")
        staff_type_model = StaffTypeModel.objects.create(name="Staff Type")

        StaffModel.objects.create(person=person_model, registration_number="1", department=department_model,
                                  staff_type=staff_type_model, start_date=now)
        staff_qs = StaffModel.objects.all()
        staff_list = StaffSerializer(instance=staff_qs, many=True).data

        response = self.client.get(reverse('staff-paginate'))
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        self.assertListEqual(content_json['results'], staff_list)

    def test_create(self):
        now = datetime.datetime.now()
        person_model = NaturalPersonModel.objects.create(identity="1234567890", name="Person Name",
                                                         last_name="Person Last Name", gender=GenderTypeEnum.MALE)
        department_model = DepartmentModel.objects.create(name="Department")
        staff_type_model = StaffTypeModel.objects.create(name="Staff Type")
        title_model = TitleModel.objects.create(name="Title")

        post_data = {
            'person_id': person_model.id,
            'registration_number': '1',
            'start_date': now.strftime('%Y-%m-%d'),
            'department_id': department_model.id,
            'staff_type_id': staff_type_model.id,
            'title_id': title_model.id
        }

        response = self.client.post(reverse('staff-create'), post_data)
        self.assertEqual(response.status_code, 201)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        model = StaffModel.objects.get(id=1)
        serializer_data = StaffSerializer(instance=model).data
        self.assertEqual(content_json, serializer_data)

    def test_update(self):
        now = datetime.datetime.now()
        person_model = NaturalPersonModel.objects.create(identity="1234567890", name="Person Name",
                                                         last_name="Person Last Name", gender=GenderTypeEnum.MALE)
        department_model = DepartmentModel.objects.create(name="Department")
        staff_type_model = StaffTypeModel.objects.create(name="Staff Type")
        title_model = TitleModel.objects.create(name="Title")
        staff_model = StaffModel.objects.create(person=person_model, registration_number="1",
                                                department=department_model,
                                                staff_type=staff_type_model, start_date=now)

        patch_data = {
            'title_id': title_model.id
        }

        response = self.client.patch(reverse('staff-update', kwargs={'pk': staff_model.id}), patch_data)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        model = StaffModel.objects.get(id=1)
        serializer_data = StaffSerializer(instance=model).data
        self.assertEqual(content_json, serializer_data)
