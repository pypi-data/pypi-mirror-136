from django.urls import reverse

from betik_app_staff.enums import ShiftTypeEnum
from betik_app_staff.tests.base import TestBase


class TestEnumView(TestBase):
    def test_shift_type_list(self):
        url = reverse('betik_app_staff:shift-type-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        shift_types = ShiftTypeEnum.types
        result = []
        for item in shift_types:
            result.append({'code': item[0], 'exp': item[1]})

        self.assertListEqual(response.data, result)
