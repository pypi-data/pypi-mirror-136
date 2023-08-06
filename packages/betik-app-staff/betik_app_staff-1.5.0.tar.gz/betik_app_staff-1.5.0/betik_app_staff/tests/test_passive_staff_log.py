import datetime

from betik_app_person.enums import GenderTypeEnum
from betik_app_person.models import NaturalPersonModel
from django.db.models import Value, Q
from django.db.models.functions import Concat
from django.urls import reverse

from betik_app_staff.models import PassiveReasonModel, PassiveStaffLogModel
from betik_app_staff.serializers.staff_passive import PassiveStaffLogSerializer
from betik_app_staff.tests.base import TestBase


class TestPassiveStaffLog(TestBase):
    def test_paginate(self):
        staff = self._create_staff()
        reason = PassiveReasonModel.objects.create(explain='Explain')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d'),
            'detail': self.faker.text(max_nb_chars=1000)

        }

        url = reverse('betik_app_staff:staff-set-passive')
        self.client.post(url, post_data)

        url = reverse('betik_app_staff:passive-staff-log-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = PassiveStaffLogModel.objects.all()
        serializer_dict = PassiveStaffLogSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        staff = self._create_staff()
        reason = PassiveReasonModel.objects.create(explain='Explain')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d'),
            'detail': self.faker.text(max_nb_chars=1000)

        }

        url = reverse('betik_app_staff:staff-set-passive')
        self.client.post(url, post_data)

        today = datetime.datetime.today()
        url = reverse('betik_app_staff:passive-staff-log-paginate')
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
        self.assertEqual(response.status_code, 200, response.data)

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
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])
