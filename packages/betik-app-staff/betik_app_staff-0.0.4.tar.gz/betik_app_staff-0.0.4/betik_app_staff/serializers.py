from betik_app_person.models import NaturalPersonModel
from betik_app_person.serializers import NaturalPersonSerializer
from betik_app_util import resolvers
from betik_app_util.table_fields import IntegerField, StringField, DateField
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

        @staticmethod
        def table_fields():
            person_fields = resolvers.get_table_fields_from_serializer_class(NaturalPersonSerializer)
            for k, v in enumerate(person_fields):
                person_fields[k].code = 'person.' + v.code
                if v.code == 'id':
                    person_fields[k].label = _('Person ID')

            return [
                       IntegerField('id', 'ID'),
                       IntegerField('status_code', _('Status Code')),
                       StringField('status', _('Status')),
                       StringField('department.name', _('Department')),
                       IntegerField('department.id', _('Department ID')),
                       StringField('staff_type.name', _('Staff Type')),
                       IntegerField('staff_type.id', _('Staff Type ID')),
                       StringField('title.name', _('Title')),
                       IntegerField('title.id', _('Title ID')),
                       StringField('registration_number', _('Registration Number')),
                       DateField('start_date', _('Start Date')),
                       DateField('finish_date', _('Finish Date')),

                   ] + person_fields
