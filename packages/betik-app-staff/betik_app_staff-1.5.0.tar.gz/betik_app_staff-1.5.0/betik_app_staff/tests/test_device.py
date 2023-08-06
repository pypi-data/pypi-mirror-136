import datetime

from betik_app_acs.enums import DeviceTypeEnum, UsingModuleEnum
from betik_app_acs.models import DeviceModel, PersonDevicePermissionModel, PersonDeviceLogModel
from betik_app_acs.serializers import DeviceSerializer, DeviceActivePassiveSerializer, DevicePermissionSerializer, \
    PersonDeviceLogSerializer
from django.urls import reverse

from betik_app_staff.tests.base import TestBase


class TestDeviceCRUD(TestBase):
    def test_create(self):
        post_data = {
            'name': 'Device Name',
            'ip': '192.168.1.1',
            'port': 4370,
            'type_code': DeviceTypeEnum.TEST
        }

        url = reverse('betik_app_staff:device-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        instance = DeviceModel.objects.get(id=1)
        serializer_data = DeviceSerializer(instance).data

        self.assertDictEqual(response.data, serializer_data)

    def test_update(self):
        device_model = DeviceModel.objects.create(
            ip='192.168.1.1',
            port=4370,
            name='Device Name',
            status=False,
            type=DeviceTypeEnum.TEST
        )
        put_data = {
            'name': 'New Device Name',
        }

        url = reverse('betik_app_staff:device-update', kwargs={'pk': device_model.id})
        response = self.client.patch(url, put_data)
        self.assertEqual(response.status_code, 200, response.data)

        instance = DeviceModel.objects.get(id=1)
        serializer_data = DeviceSerializer(instance).data

        self.assertDictEqual(response.data, serializer_data)

    def test_paginate(self):
        DeviceModel.objects.create(
            ip='192.168.1.1',
            port=4370,
            name='Device Name',
            status=False,
            type=DeviceTypeEnum.TEST,
            using_module=UsingModuleEnum.STAFF
        )
        DeviceModel.objects.create(
            ip='192.168.1.2',
            port=4370,
            name='Device Name1',
            type=DeviceTypeEnum.TEST
        )

        url = reverse('betik_app_staff:device-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = DeviceModel.objects.filter(using_module=UsingModuleEnum.STAFF)
        serializer_data = DeviceSerializer(instances, many=True).data

        self.assertListEqual(response.data, serializer_data)


class TestDeviceStatus(TestBase):
    def test_passive(self):
        device_model = DeviceModel.objects.create(
            ip='192.168.1.1',
            port=4370,
            name='Device Name',
            type=DeviceTypeEnum.TEST,
            using_module=UsingModuleEnum.STAFF
        )

        put_data = {
            'status': False,
        }

        url = reverse('betik_app_staff:device-status-change', kwargs={'pk': device_model.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200)

        instance = DeviceModel.objects.get(id=1)
        serializer_data = DeviceActivePassiveSerializer(instance).data

        self.assertDictEqual(response.data, serializer_data)

    def test_active(self):
        device_model = DeviceModel.objects.create(
            ip='192.168.1.1',
            port=4370,
            status=False,
            name='Device Name',
            type=DeviceTypeEnum.TEST,
            using_module=UsingModuleEnum.STAFF
        )

        put_data = {
            'status': True
        }

        url = reverse('betik_app_staff:device-status-change', kwargs={'pk': device_model.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200)

        instance = DeviceModel.objects.get(id=1)

        serializer_data = DeviceActivePassiveSerializer(instance).data
        self.assertDictEqual(response.data, serializer_data)


class TestStaffPermission(TestBase):
    def test_update_from_query(self):
        self._create_staff()
        self._create_staff()

        inst_device = DeviceModel.objects.create(
            ip='192.168.1.1',
            port=4560,
            name='Device Name',
            type=DeviceTypeEnum.TEST,
            using_module=UsingModuleEnum.STAFF
        )

        post_data = {
            'device_perms': [{
                'device_id': inst_device.id,
                'enable_card': True,
                'enable_password': False,
                'enable_finger': True
            }],
            'save_old_permission': True,
            'using_module_code': UsingModuleEnum.STAFF
        }

        url = reverse('betik_app_staff:device-permission-assign-bulk-staff')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 202, response.data)

        self.assertDictEqual(response.data, {'result': True})

        count = PersonDevicePermissionModel.objects.count()
        self.assertEqual(2, count)

    def test_permission_list_by_person(self):
        inst_staff = self._create_staff()

        inst_device = DeviceModel.objects.create(
            ip='192.168.1.1',
            port=4560,
            name='Device Name',
            type=DeviceTypeEnum.TEST,
            using_module=UsingModuleEnum.STAFF
        )

        PersonDevicePermissionModel.objects.create(
            person=inst_staff.person,
            device=inst_device,
            enable_card=True,
            enable_finger=True,
            enable_password=True
        )

        url = reverse('betik_app_staff:device-permission-list-by-person',
                      kwargs={'person_id': inst_staff.person.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        instances = PersonDevicePermissionModel.objects.filter(person=inst_staff.person)
        serializer_data = DevicePermissionSerializer(instances, many=True).data

        self.assertListEqual(response.data, serializer_data)


class TestDeviceLog(TestBase):
    def test_paginate(self):
        now = datetime.datetime.now()
        inst_staff = self._create_staff()
        inst_device = DeviceModel.objects.create(
            ip='192.168.1.1',
            port=4560,
            name='Device Name',
            type=DeviceTypeEnum.TEST,
            using_module=UsingModuleEnum.STAFF
        )

        PersonDeviceLogModel.objects.create(
            person=inst_staff.person,
            device_name=inst_device.name,
            device_module=inst_device.using_module,
            time=now
        )

        datetime_gte = now - datetime.timedelta(days=10)
        datetime_lte = now + datetime.timedelta(days=10)

        url = reverse('betik_app_staff:device-log-paginate',
                      kwargs={
                          'datetime_gte': datetime_gte.strftime("%Y-%m-%d %H:%M:%S"),
                          'datetime_lte': datetime_lte.strftime("%Y-%m-%d %H:%M:%S")
                      })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        inst = PersonDeviceLogModel.objects.filter(time__lte=datetime_lte, time__gte=datetime_gte)
        ser_data = PersonDeviceLogSerializer(inst, many=True).data

        self.assertListEqual(response.data['results'], ser_data)
