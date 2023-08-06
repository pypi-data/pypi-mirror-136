import datetime
import os
from io import StringIO

from betik_app_document.models import DocumentTypeModel
from django.core import management
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from betik_app_staff.enums import StaffStatusEnum
from betik_app_staff.models import StaffModel, PassiveReasonModel, PassiveStaffLogModel, DismissReasonModel, \
    DismissStaffLogModel
from betik_app_staff.serializers.staff import StaffSerializer
from betik_app_staff.serializers.staff_dismiss import StaffSetDismissSerializer
from betik_app_staff.serializers.staff_passive import StaffSetPassiveSerializer
from betik_app_staff.tests.base import TestBase


class TestStaff(TestBase):
    def test_paginate(self):
        self._create_staff()
        self._create_staff()

        staff_qs = StaffModel.objects.all().order_by('-registration_number')
        staff_list = StaffSerializer(instance=staff_qs, many=True).data

        url = reverse('betik_app_staff:staff-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        self.assertListEqual(response.data['results'], staff_list)

    def test_create(self):
        buf = StringIO()
        management.call_command("create_default_document_types", stdout=buf)

        file1 = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        file2 = SimpleUploadedFile("file.pdf", b"file_content", content_type="application/pdf")

        file3 = SimpleUploadedFile("file.txt", b"file_content", content_type="plain/text")
        file4 = SimpleUploadedFile("file.txt", b"file_content", content_type="plain/text")

        now = datetime.datetime.now()
        person_model = self._create_person()
        department_model = self._create_department()
        staff_type_model = self._create_staff_type()
        title_model = self._create_title()
        doc_type = DocumentTypeModel.objects.get(code=DocumentTypeModel.EMPLOYMENT_AGREEMENT)

        post_data = {
            'person_id': person_model.id,
            'registration_number': '1',
            'start_date': now.strftime('%Y-%m-%d'),
            'department_id': department_model.id,
            'staff_type_id': staff_type_model.id,
            'title_id': title_model.id,
            'file_employment_agreement.file': file1,
            'file_statement_of_insured_employment.file': file2,
            'files[0]file': file3,
            'files[0]document_type_id': doc_type.id,
            'files[0]description': 'File description1',
            'files[1]file': file4,
            'files[1]document_type_id': doc_type.id,
            'files[1]description': 'File description2',
        }

        url = reverse('betik_app_staff:staff-create')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201, response.data)

        model = StaffModel.objects.get(id=1)
        request = response.wsgi_request
        serializer_data = StaffSerializer(instance=model, context={'request': request}).data
        self.assertDictEqual(response.data, serializer_data)

        name, extension = os.path.splitext(response.data['file_employment_agreement']['file'])
        self.assertEqual(extension, '.png')
        name, extension = os.path.splitext(response.data['file_statement_of_insured_employment']['file'])
        self.assertEqual(extension, '.pdf')
        name, extension = os.path.splitext(response.data['files'][0]['file'])
        self.assertEqual(extension, '.txt')

    def test_update(self):
        buf = StringIO()
        management.call_command("create_default_document_types", stdout=buf)

        file1 = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        file2 = SimpleUploadedFile("file.pdf", b"file_content", content_type="application/pdf")

        title_model = self._create_title()
        staff_model = self._create_staff()

        patch_data = {
            'title_id': title_model.id,
            'file_employment_agreement.file': file1,
            'file_statement_of_insured_employment.file': file2
        }

        url = reverse('betik_app_staff:staff-update', kwargs={'pk': staff_model.id})
        response = self.client.patch(url, patch_data)
        self.assertEqual(response.status_code, 200, response.data)

        model = StaffModel.objects.get(id=1)

        request = response.wsgi_request
        serializer_data = StaffSerializer(instance=model, context={'request': request}).data
        self.assertDictEqual(response.data, serializer_data)

        name, extension = os.path.splitext(response.data['file_employment_agreement']['file'])
        self.assertEqual(extension, '.png')

        name, extension = os.path.splitext(response.data['file_statement_of_insured_employment']['file'])
        self.assertEqual(extension, '.pdf')

    def test_set_passive(self):
        staff = self._create_staff()
        reason = PassiveReasonModel.objects.create(explain='Reason')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d'),
            'detail': self.faker.text(max_nb_chars=1000)

        }

        url = reverse('betik_app_staff:staff-set-passive')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201, response.data)

        instance = PassiveStaffLogModel.objects.get(id=1)
        serializer_dict = StaffSetPassiveSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

        staff_instance = StaffModel.objects.get(id=1)
        self.assertEqual(StaffStatusEnum.PASSIVE, staff_instance.status)

    def test_set_dismiss(self):
        staff = self._create_staff()
        reason = DismissReasonModel.objects.create(explain='Reason')

        post_data = {
            'staff_id': staff.id,
            'reason_id': reason.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d'),
            'detail': self.faker.text(max_nb_chars=1000)

        }

        url = reverse('betik_app_staff:staff-set-dismiss')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201, response.data)

        instance = DismissStaffLogModel.objects.get(id=1)
        serializer_dict = StaffSetDismissSerializer(instance=instance).data
        self.assertDictEqual(response.data, serializer_dict)

        staff_instance = StaffModel.objects.get(id=1)
        self.assertEqual(StaffStatusEnum.DISMISS, staff_instance.status)
