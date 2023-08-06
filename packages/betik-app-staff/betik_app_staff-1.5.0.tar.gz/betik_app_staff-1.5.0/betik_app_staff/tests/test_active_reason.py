from django.urls import reverse

from betik_app_staff.models import ActiveReasonModel
from betik_app_staff.serializers.staff_active import ActiveReasonSerializer
from betik_app_staff.tests.base import TestBase


class TestActiveReason(TestBase):
    def test_create(self):
        post_data = {
            'explain': 'Reason'
        }

        url = reverse('betik_app_staff:active-reason-create')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201, response.data)

        instance = ActiveReasonModel.objects.get(id=1)
        serializer_dict = ActiveReasonSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_update(self):
        instance = ActiveReasonModel.objects.create(explain='Reason')

        put_data = {
            'explain': 'New Reason'
        }

        url = reverse('betik_app_staff:active-reason-update', kwargs={'pk': instance.id})
        response = self.client.put(url, put_data)
        self.assertEqual(response.status_code, 200, response.data)

        model = ActiveReasonModel.objects.get(id=1)
        serializer_dict = ActiveReasonSerializer(instance=model).data
        self.assertDictEqual(response.data, serializer_dict)

    def test_delete(self):
        instance = ActiveReasonModel.objects.create(explain='Reason')

        url = reverse('betik_app_staff:active-reason-delete', kwargs={'pk': instance.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

        count = ActiveReasonModel.objects.count()
        self.assertEqual(0, count)

    def test_paginate(self):
        ActiveReasonModel.objects.create(explain='Explain')
        ActiveReasonModel.objects.create(explain='Explain1')

        url = reverse('betik_app_staff:active-reason-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = ActiveReasonModel.objects.all()
        serializer_dict = ActiveReasonSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])

    def test_filter_paginate(self):
        ActiveReasonModel.objects.create(explain='Explain')
        ActiveReasonModel.objects.create(explain='Explain1')

        url = reverse('betik_app_staff:active-reason-paginate') + '?explain=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = ActiveReasonModel.objects.filter(explain__icontains='1').order_by('explain')
        serializer_dict = ActiveReasonSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = instances.count()
        self.assertEqual(count, response.data['count'])
