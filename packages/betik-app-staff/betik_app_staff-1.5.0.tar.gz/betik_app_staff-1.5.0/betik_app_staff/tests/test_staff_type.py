from django.urls import reverse
from django.utils.translation import gettext as _

from betik_app_staff.models import StaffTypeModel
from betik_app_staff.serializers.staff import StaffTypeSerializer
from betik_app_staff.tests.base import TestBase


class TestStaffType(TestBase):
    def test_paginate(self):
        self._create_staff_type()
        self._create_staff_type()

        url = reverse('betik_app_staff:staff-type-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = StaffTypeModel.objects.all().order_by('name')
        serializer_dict = StaffTypeSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        self._create_staff_type()
        inst = self._create_staff_type()

        url = reverse('betik_app_staff:staff-type-paginate') + '?name=' + inst.name
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = StaffTypeModel.objects.filter(name__icontains=inst.name).order_by('name')
        serializer_dict = StaffTypeSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_create(self):
        post_data = {
            'name': 'Staff Type'
        }

        url = reverse('betik_app_staff:staff-type-create')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201, response.data)

        model = StaffTypeModel.objects.get(id=1)
        serializer_data = StaffTypeSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_data)

    def test_update(self):
        model = self._create_staff_type()

        put_data = {
            'name': 'New Staff Type'
        }

        url = reverse('betik_app_staff:staff-type-update', kwargs={'pk': model.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200, response.data)

        model = StaffTypeModel.objects.get(id=1)
        serializer_data = StaffTypeSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_data)

    def test_delete(self):
        model = self._create_staff_type()

        url = reverse('betik_app_staff:staff-type-delete', kwargs={'pk': model.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

    def test_merge(self):
        inst_staff1 = self._create_staff()
        inst_staff2 = self._create_staff()
        inst_staff3 = self._create_staff()

        put_data = {
            'source_ids': [
                inst_staff2.staff_type.id,
                inst_staff3.staff_type.id
            ]
        }

        url = reverse('betik_app_staff:staff-type-merge', kwargs={'pk': inst_staff1.staff_type.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200, response.data)

        self.assertDictEqual(response.data, {'result': True})

        count = StaffTypeModel.objects.count()
        self.assertEqual(1, count)


class TestMergeFail(TestBase):
    def test_conflict_business_day(self):
        """
            çakışan tarihlere sahip, farklı tipte personel tipleri için oluşturulmuş genel iş kurallarının,
            birleşmeden sonra tarih çakışma hatası atması
        """
        inst_staff1 = self._create_staff()
        inst_staff2 = self._create_staff()
        inst_staff3 = self._create_staff()

        inst_business_day1 = self._create_business_day()
        inst_business_day1.finish_date = None
        inst_business_day1.staff_type = inst_staff2.staff_type
        inst_business_day1.save()

        inst_business_day2 = self._create_business_day()
        inst_business_day2.finish_date = None
        inst_business_day2.staff_type = inst_staff3.staff_type
        inst_business_day2.save()

        put_data = {
            'source_ids': [
                inst_staff2.staff_type.id,
                inst_staff3.staff_type.id
            ]
        }

        url = reverse('betik_app_staff:staff-type-merge', kwargs={'pk': inst_staff1.staff_type.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('There is a general business rule conflict after this merge.')
        msg += ' ' + _(
            'Business rule id #%(id1)d(%(date_range1)s) conflicts with business rule id #%(id2)d(%(date_range2)s)') % {
                   'id1': inst_business_day1.id,
                   'id2': inst_business_day2.id,
                   'date_range1': inst_business_day1.get_formatted_date_range(),
                   'date_range2': inst_business_day2.get_formatted_date_range(),
               }

        self.assertDictEqual(response.data, {'detail': msg})

    def test_conflict_annual_leave_rule(self):
        """
            çakışan tarihlere sahip, farklı tipte personel tipleri için oluşturulmuş yıllık izin kurallarının,
            birleşmeden sonra tarih çakışma hatası atması
        """
        inst_staff1 = self._create_staff()
        inst_staff2 = self._create_staff()
        inst_staff3 = self._create_staff()

        inst_annual_leave_rule1 = self._create_annual_leave_rule()
        inst_annual_leave_rule1.finish_date = None
        inst_annual_leave_rule1.staff_type = inst_staff2.staff_type
        inst_annual_leave_rule1.save()

        inst_annual_leave_rule2 = self._create_annual_leave_rule()
        inst_annual_leave_rule2.finish_date = None
        inst_annual_leave_rule2.staff_type = inst_staff3.staff_type
        inst_annual_leave_rule2.save()

        put_data = {
            'source_ids': [
                inst_staff2.staff_type.id,
                inst_staff3.staff_type.id
            ]
        }

        url = reverse('betik_app_staff:staff-type-merge', kwargs={'pk': inst_staff1.staff_type.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('There is a annual leave rule conflict after this merge.')
        msg += ' ' + _(
            'Annual leave rule id #%(id1)d(%(date_range1)s) conflicts with annual leave rule id #%(id2)d(%(date_range2)s)') % {
                   'id1': inst_annual_leave_rule1.id,
                   'id2': inst_annual_leave_rule2.id,
                   'date_range1': inst_annual_leave_rule1.get_formatted_date_range(),
                   'date_range2': inst_annual_leave_rule2.get_formatted_date_range(),
               }

        self.assertDictEqual(response.data, {'detail': msg})