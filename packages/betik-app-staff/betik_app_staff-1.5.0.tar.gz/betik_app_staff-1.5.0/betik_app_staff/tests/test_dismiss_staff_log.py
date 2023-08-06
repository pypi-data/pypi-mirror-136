import datetime

from django.urls import reverse

from betik_app_staff.models import DismissReasonModel, DismissStaffLogModel
from betik_app_staff.serializers.staff_dismiss import DismissStaffLogSerializer
from betik_app_staff.tests.base import TestBase


class TestDismissStaffLog(TestBase):
    def test_paginate(self):
        staff = self._create_staff()
        reason = DismissReasonModel.objects.create(explain='Explain')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d'),
            'detail': self.faker.text(max_nb_chars=1000)

        }
        self.client.post(reverse('betik_app_staff:staff-set-dismiss'), post_data)

        url = reverse('betik_app_staff:dismiss-staff-log-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = DismissStaffLogModel.objects.all()
        serializer_dict = DismissStaffLogSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])
