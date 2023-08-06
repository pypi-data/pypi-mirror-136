import datetime

from django.urls import reverse

from betik_app_staff.enums import StaffStatusEnum
from betik_app_staff.models import ActiveReasonModel, ActiveStaffLogModel
from betik_app_staff.serializers.staff_active import ActiveStaffLogSerializer
from betik_app_staff.tests.base import TestBase


class TestActiveStaffLog(TestBase):
    def test_paginate(self):
        today = datetime.datetime.today()

        staff = self._create_staff()
        staff.status = StaffStatusEnum.PASSIVE
        staff.finish_date = today
        staff.save()

        reason = ActiveReasonModel.objects.create(explain='Explain')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d'),
            'detail': self.faker.text(max_nb_chars=1000)

        }

        url = reverse('betik_app_staff:staff-set-active')
        self.client.post(url, post_data)

        url = reverse('betik_app_staff:active-staff-log-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = ActiveStaffLogModel.objects.all()
        serializer_dict = ActiveStaffLogSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])
