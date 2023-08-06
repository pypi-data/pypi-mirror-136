from django.urls import reverse

from betik_app_staff.tests.base import TestBase


class TestStatistic(TestBase):
    def test_gender(self):
        for i in range(0, 10):
            self._create_staff()

        url = reverse('betik_app_staff:statistic-staff-gender-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

    def test_blood(self):
        for i in range(0, 10):
            self._create_staff()

        url = reverse('betik_app_staff:statistic-staff-blood-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

    def test_education(self):
        for i in range(0, 10):
            self._create_staff()

        url = reverse('betik_app_staff:statistic-staff-education-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

    def test_register_province(self):
        for i in range(0, 10):
            self._create_staff()

        url = reverse('betik_app_staff:statistic-staff-register-province-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

    def test_department(self):
        for i in range(0, 10):
            self._create_staff()

        url = reverse('betik_app_staff:statistic-staff-department-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

    def test_staff_type(self):
        for i in range(0, 10):
            self._create_staff()

        url = reverse('betik_app_staff:statistic-staff-staff-type-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

    def test_title(self):
        for i in range(0, 10):
            self._create_staff()

        url = reverse('betik_app_staff:statistic-staff-title-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)
