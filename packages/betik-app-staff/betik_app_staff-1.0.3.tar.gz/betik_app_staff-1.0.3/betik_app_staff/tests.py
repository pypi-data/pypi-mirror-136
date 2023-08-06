import datetime
import json

from betik_app_person.enums import GenderTypeEnum
from betik_app_person.faker_providers import IdentityProvider
from betik_app_person.models import NaturalPersonModel
from django.contrib.auth import get_user_model
from django.db.models import Value, Q
from django.db.models.functions import Concat
from django.test import TransactionTestCase
from django.urls import reverse
from faker import Faker
from faker.providers import person
from rest_framework.test import APIClient

from betik_app_staff.enums import StaffStatusEnum
from betik_app_staff.models import DepartmentModel, TitleModel, StaffTypeModel, StaffModel, PassiveReasonModel, \
    PassiveStaffLogModel, DismissReasonModel, DismissStaffLogModel
from betik_app_staff.serializers import DepartmentSerializer, TitleSerializer, StaffTypeSerializer, StaffSerializer, \
    PassiveReasonSerializer, StaffSetPassiveSerializer, PassiveStaffLogSerializer, DismissReasonSerializer, \
    StaffSetDismissSerializer, DismissStaffLogSerializer


class TestBase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.faker = Faker()
        self._login()

    def _login(self):
        user = get_user_model().objects.create(email="test@test.com", is_staff=True)
        user.set_password("123")
        user.save()

        self.client.force_authenticate(user)
        return user

    def _create_person(self):
        self.faker.add_provider(person)
        self.faker.add_provider(IdentityProvider)

        return NaturalPersonModel.objects.create(
            identity=self.faker.identity(),
            name=self.faker.first_name(),
            last_name=self.faker.last_name(),
            gender=GenderTypeEnum.MALE
        )

    def _create_staff(self):
        person_model = self._create_person()

        department = self.faker.bothify(text='Dep-????-###')
        department_model = DepartmentModel.objects.create(name=department)

        staff_type = self.faker.bothify(text='Staff-????-###')
        staff_type_model = StaffTypeModel.objects.create(name=staff_type)

        title = self.faker.bothify(text='Staff-????-###')
        title_model = TitleModel.objects.create(name=title)

        staff_model = StaffModel.objects.create(
            person=person_model,
            registration_number=StaffModel.objects.count() + 1,
            department=department_model,
            staff_type=staff_type_model,
            start_date=datetime.datetime.now(),
            title=title_model
        )

        return staff_model


class TestDepartment(TestBase):
    def test_paginate(self):
        DepartmentModel.objects.create(name='Depart')
        DepartmentModel.objects.create(name='Depart1')

        url = reverse('department-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = DepartmentModel.objects.all()
        serializer_dict = DepartmentSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])

    def test_filter_paginate(self):
        DepartmentModel.objects.create(name='Depart')
        DepartmentModel.objects.create(name='Depart1')

        url = reverse('department-paginate') + '?name=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = DepartmentModel.objects.filter(name__icontains='1')
        serializer_dict = DepartmentSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])

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

    def test_merge(self):
        # bu method içinde department oluşturuluyor pk=1
        self._create_staff()
        model_target = DepartmentModel.objects.create(name='Department')

        put_data = {
            'source_ids': [1]
        }

        url = reverse('department-merge', kwargs={'pk': model_target.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        self.assertDictEqual(content_json, {'result': True})

        staff_instance = StaffModel.objects.get(id=1)
        self.assertEqual(staff_instance.department.id, model_target.id)

        count = DepartmentModel.objects.count()
        self.assertEqual(1, count)


class TestTitle(TestBase):
    def test_paginate(self):
        TitleModel.objects.create(name='Title')
        TitleModel.objects.create(name='Title1')

        url = reverse('title-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = TitleModel.objects.all()
        serializer_dict = TitleSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])

    def test_filter_paginate(self):
        TitleModel.objects.create(name='Title')
        TitleModel.objects.create(name='Title1')

        url = reverse('title-paginate') + '?name=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = TitleModel.objects.filter(name__icontains='1')
        serializer_dict = TitleSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])

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
    def test_paginate(self):
        StaffTypeModel.objects.create(name='Staff Type')
        StaffTypeModel.objects.create(name='Staff Type1')

        url = reverse('staff-type-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = StaffTypeModel.objects.all()
        serializer_dict = StaffTypeSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])

    def test_filter_paginate(self):
        StaffTypeModel.objects.create(name='Staff Type')
        StaffTypeModel.objects.create(name='Staff Type1')

        url = reverse('staff-type-paginate') + '?name=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = StaffTypeModel.objects.filter(name__icontains='1')
        serializer_dict = StaffTypeSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])

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
        self._create_staff()

        staff_qs = StaffModel.objects.all()
        staff_list = StaffSerializer(instance=staff_qs, many=True).data

        response = self.client.get(reverse('staff-paginate'))
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)
        self.assertListEqual(content_json['results'], staff_list)

    def test_create(self):
        now = datetime.datetime.now()
        person_model = self._create_person()
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
        person_model = self._create_person()
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

    def test_set_passive(self):
        staff = self._create_staff()
        reason = PassiveReasonModel.objects.create(explain='Reason')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d')

        }
        response = self.client.post(reverse('staff-set-passive'), post_data)
        self.assertEqual(response.status_code, 201)

        content = str(response.content, encoding="utf8")
        content_dict = json.loads(content)

        instance = PassiveStaffLogModel.objects.get(id=1)
        serializer_dict = StaffSetPassiveSerializer(instance=instance).data
        self.assertDictEqual(content_dict, serializer_dict)

        staff_instance = StaffModel.objects.get(id=1)
        self.assertEqual(StaffStatusEnum.PASSIVE, staff_instance.status)

    def test_set_dismiss(self):
        staff = self._create_staff()
        reason = DismissReasonModel.objects.create(explain='Reason')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d')

        }
        response = self.client.post(reverse('staff-set-dismiss'), post_data)
        self.assertEqual(response.status_code, 201)

        content = str(response.content, encoding="utf8")
        content_dict = json.loads(content)

        instance = DismissStaffLogModel.objects.get(id=1)
        serializer_dict = StaffSetDismissSerializer(instance=instance).data
        self.assertDictEqual(content_dict, serializer_dict)

        staff_instance = StaffModel.objects.get(id=1)
        self.assertEqual(StaffStatusEnum.DISMISS, staff_instance.status)


class TestPassiveReason(TestBase):
    def test_create(self):
        post_data = {
            'explain': 'Reason'
        }

        url = reverse('passive-reason-create')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)

        content = str(response.content, encoding="utf8")
        content_dict = json.loads(content)

        instance = PassiveReasonModel.objects.get(id=1)
        serializer_dict = PassiveReasonSerializer(instance=instance).data
        self.assertDictEqual(content_dict, serializer_dict)

    def test_update(self):
        instance = PassiveReasonModel.objects.create(explain='Reason')

        put_data = {
            'explain': 'New Reason'
        }

        url = reverse('passive-reason-update', kwargs={'pk': instance.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_dict = json.loads(content)

        model = PassiveReasonModel.objects.get(id=1)
        serializer_dict = PassiveReasonSerializer(instance=model).data
        self.assertDictEqual(content_dict, serializer_dict)

    def test_delete(self):
        instance = PassiveReasonModel.objects.create(explain='Reason')

        url = reverse('passive-reason-delete', kwargs={'pk': instance.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        count = PassiveReasonModel.objects.count()
        self.assertEqual(0, count)

    def test_paginate(self):
        PassiveReasonModel.objects.create(explain='Explain')
        PassiveReasonModel.objects.create(explain='Explain1')

        url = reverse('passive-reason-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = PassiveReasonModel.objects.all()
        serializer_dict = PassiveReasonSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])

    def test_filter_paginate(self):
        PassiveReasonModel.objects.create(explain='Explain')
        PassiveReasonModel.objects.create(explain='Explain1')

        url = reverse('passive-reason-paginate') + '?explain=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = PassiveReasonModel.objects.filter(explain__icontains='1')
        serializer_dict = PassiveReasonSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])


class TestPassiveStaffLog(TestBase):
    def test_paginate(self):
        staff = self._create_staff()
        reason = PassiveReasonModel.objects.create(explain='Explain')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d')

        }
        self.client.post(reverse('staff-set-passive'), post_data)

        url = reverse('passive-staff-log-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = PassiveStaffLogModel.objects.all()
        serializer_dict = PassiveStaffLogSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])

    def test_filter_paginate(self):
        staff = self._create_staff()
        reason = PassiveReasonModel.objects.create(explain='Explain')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d')

        }
        self.client.post(reverse('staff-set-passive'), post_data)

        today = datetime.datetime.today()
        url = reverse('passive-staff-log-paginate')
        url += '?identity=1' \
               '&tax_number=1' \
               '&name=a' \
               '&last_name=a' \
               '&gender=' + str(GenderTypeEnum.MALE) + \
               '&registration_number=1' \
               '&reason_id=1' \
               '&date_gte=' + today.strftime('%Y-%m-%d') + \
               '&date_lte=' + today.strftime('%Y-%m-%d') + \
               '&quick_search=a'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        value = 'a'
        qs = NaturalPersonModel.objects. \
            annotate(full_name=Concat('name', Value(' '), 'last_name')). \
            filter(full_name__icontains=value)

        instances = PassiveStaffLogModel.objects.filter(
            staff__person__identity__icontains='1',
            staff__person__tax_number__icontains='1',
            staff__person__name__icontains='a',
            staff__person__last_name__icontains='a',
            staff__person__gender=GenderTypeEnum.MALE,
            staff__registration_number=1,
            reason=1,
            date__gte=today,
            date__lte=today
        ).filter(
            Q(staff__person__name__icontains=value) |
            Q(staff__person__last_name__icontains=value) |
            Q(staff__person__identity__icontains=value) |
            Q(staff__person__tax_number__icontains=value) |
            Q(staff__person__id__in=qs)
        ).order_by('-date')
        serializer_dict = PassiveStaffLogSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])


class TestDismissReason(TestBase):
    def test_create(self):
        post_data = {
            'explain': 'Reason'
        }

        url = reverse('dismiss-reason-create')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)

        content = str(response.content, encoding="utf8")
        content_dict = json.loads(content)

        instance = DismissReasonModel.objects.get(id=1)
        serializer_dict = DismissReasonSerializer(instance=instance).data
        self.assertDictEqual(content_dict, serializer_dict)

    def test_update(self):
        instance = DismissReasonModel.objects.create(explain='Reason')

        put_data = {
            'explain': 'New Reason'
        }

        url = reverse('dismiss-reason-update', kwargs={'pk': instance.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_dict = json.loads(content)

        model = DismissReasonModel.objects.get(id=1)
        serializer_dict = DismissReasonSerializer(instance=model).data
        self.assertDictEqual(content_dict, serializer_dict)

    def test_delete(self):
        instance = DismissReasonModel.objects.create(explain='Reason')

        url = reverse('dismiss-reason-delete', kwargs={'pk': instance.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        count = DismissReasonModel.objects.count()
        self.assertEqual(0, count)

    def test_paginate(self):
        DismissReasonModel.objects.create(explain='Explain')
        DismissReasonModel.objects.create(explain='Explain1')

        url = reverse('dismiss-reason-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = DismissReasonModel.objects.all()
        serializer_dict = DismissReasonSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])

    def test_filter_paginate(self):
        DismissReasonModel.objects.create(explain='Explain')
        DismissReasonModel.objects.create(explain='Explain1')

        url = reverse('dismiss-reason-paginate') + '?explain=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = DismissReasonModel.objects.filter(explain__icontains='1').order_by('explain')
        serializer_dict = DismissReasonSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])


class TestDismissStaffLog(TestBase):
    def test_paginate(self):
        staff = self._create_staff()
        reason = DismissReasonModel.objects.create(explain='Explain')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d')

        }
        self.client.post(reverse('staff-set-dismiss'), post_data)

        url = reverse('dismiss-staff-log-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = str(response.content, encoding="utf8")
        content_json = json.loads(content)

        instances = DismissStaffLogModel.objects.all()
        serializer_dict = DismissStaffLogSerializer(instance=instances, many=True).data
        self.assertListEqual(content_json['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, content_json['count'])
