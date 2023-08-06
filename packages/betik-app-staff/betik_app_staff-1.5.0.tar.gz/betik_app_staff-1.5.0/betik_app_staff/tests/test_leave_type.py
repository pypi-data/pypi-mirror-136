from django.urls import reverse
from django.utils.translation import gettext as _

from betik_app_staff.enums import LeaveTypeEnum
from betik_app_staff.models import LeaveTypeModel
from betik_app_staff.serializers.staff_leave import LeaveTypeSerializer
from betik_app_staff.tests.base import TestBase


class TestLeaveType(TestBase):
    def test_paginate(self):
        LeaveTypeModel.objects.create(type='Type')
        LeaveTypeModel.objects.create(type='Type1')

        url = reverse('betik_app_staff:leave-type-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = LeaveTypeModel.objects.all()
        serializer_dict = LeaveTypeSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        LeaveTypeModel.objects.create(type='Type')
        LeaveTypeModel.objects.create(type='Type1')

        url = reverse('betik_app_staff:leave-type-paginate') + '?type=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = LeaveTypeModel.objects.filter(type__icontains='1')
        serializer_dict = LeaveTypeSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_create(self):
        post_data = {
            'type': 'Type'
        }

        response = self.client.post(reverse('betik_app_staff:leave-type-create'), post_data)
        self.assertEqual(response.status_code, 201, response.data)

        model = LeaveTypeModel.objects.get(id=1)
        serializer_data = LeaveTypeSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_data)

    def test_update(self):
        model = LeaveTypeModel.objects.create(type='Type')

        put_data = {
            'type': 'New Type'
        }

        response = self.client.put(reverse('betik_app_staff:leave-type-update', kwargs={'pk': model.id}), put_data)
        self.assertEqual(response.status_code, 200, response.data)

        model = LeaveTypeModel.objects.get(id=1)
        serializer_data = LeaveTypeSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_data)

    def test_delete(self):
        model = LeaveTypeModel.objects.create(type='type')

        response = self.client.delete(reverse('betik_app_staff:leave-type-delete', kwargs={'pk': model.id}))
        self.assertEqual(response.status_code, 204, response.data)


class TestLeaveTypeFailDelete(TestBase):
    def test_can_not_be_deleted(self):
        model = LeaveTypeModel.objects.create(type='type', code=LeaveTypeEnum.ANNUAL_LEAVE)

        response = self.client.delete(reverse('betik_app_staff:leave-type-delete', kwargs={'pk': model.id}))
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('This leave type can not be deleted')
        self.assertDictEqual(response.data, {'detail': msg})
