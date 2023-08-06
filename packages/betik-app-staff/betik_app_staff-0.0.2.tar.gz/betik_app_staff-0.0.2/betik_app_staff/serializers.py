from betik_app_person.models import NaturalPersonModel
from betik_app_person.serializers import NaturalPersonSerializer
from betik_app_util.table_fields import IntegerField, StringField, ImageField, ArrayField
from rest_framework import serializers
from django.utils.translation import gettext as _

from betik_app_staff.enums import StaffStatusEnum
from betik_app_staff.models import DepartmentModel, TitleModel, StaffTypeModel, StaffModel


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentModel
        fields = ['id', 'name']
        table_fields = [
            IntegerField('id', 'ID'),
            StringField('name', _('Name'))
        ]


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleModel
        fields = ['id', 'name']
        table_fields = [
            IntegerField('id', 'ID'),
            StringField('name', _('Name'))
        ]


class StaffTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffTypeModel
        fields = ['id', 'name']
        table_fields = [
            IntegerField('id', 'ID'),
            StringField('name', _('Name'))
        ]


class StaffSerializer(serializers.ModelSerializer):
    status_code = serializers.ChoiceField(choices=StaffStatusEnum.types, source='status', read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    person_id = serializers.PrimaryKeyRelatedField(queryset=NaturalPersonModel.objects.all(), source='person',
                                                   write_only=True)
    person = NaturalPersonSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=DepartmentModel.objects.all(), source='department',
                                                       write_only=True)
    department = DepartmentSerializer(read_only=True)
    staff_type_id = serializers.PrimaryKeyRelatedField(queryset=StaffTypeModel.objects.all(), source='staff_type',
                                                       write_only=True)
    staff_type = StaffTypeSerializer(read_only=True)
    title_id = serializers.PrimaryKeyRelatedField(queryset=TitleModel.objects.all(), source='title',
                                                  write_only=True)
    title = TitleSerializer(read_only=True)

    class Meta:
        model = StaffModel
        fields = [
            'id', 'person_id', 'person', 'registration_number', 'department_id', 'department', 'staff_type_id',
            'staff_type', 'title_id', 'title', 'start_date', 'finish_date', 'status_code', 'status'
        ]
        read_only_fields = [
            'id', 'finish_date', 'status_code', 'status', 'person', 'department', 'staff_type', 'title'
        ]
        table_fields = [
            IntegerField('status_code', _('Status Code')),
            StringField('status', _('Status')),
            StringField('department.name', _('Department')),
            StringField('staff_type.name', _('Staff Type')),
            StringField('title.name', _('Title')),
            StringField('registration_number', _('Registration Number')),
            StringField('start_date', _('Start Date')),
            StringField('finish_date', _('Finish Date')),
            StringField('person.id', _('Person ID')),
            ImageField('person.image', _('Image')),
            StringField('person.identity', _('Identity')),
            StringField('person.tax_number', _('Tax Number')),
            StringField('person.name', _('Name')),
            StringField('person.last_name', _('Last Name')),
            StringField('person.gender', _('Gender')),
            StringField('person.birth_date', _('Birth Date')),
            StringField('person.birth_place', _('Birth Place')),
            StringField('person.father_name', _('Father Name')),
            StringField('person.mother_name', _('Mother Name')),
            StringField('person.register_district.name', _('Register District')),
            StringField('person.register_district.province.name', _('Register Province Name')),
            StringField('person.volume_code', _('Volume Code')),
            StringField('person.volume_name', _('Volume Name')),
            StringField('person.family_no', _('Family No')),
            StringField('person.person_no', _('Person No')),
            StringField('person.education_status', _('Education Status')),
            StringField('person.blood', _('Blood')),
            ArrayField('person.email_addresses', _('Email Address')),
            ArrayField('person.phones', _('Phone')),
            ArrayField('person.faxes', _('Fax')),
            ArrayField('person.addresses', _('Address'))
        ]
