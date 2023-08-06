from betik_app_person.models import NaturalPersonModel
from betik_app_person.serializers import NaturalPersonSerializer
from betik_app_util import resolvers
from betik_app_util.table_fields import IntegerField, StringField, DateField
from django.db import transaction
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from betik_app_staff.enums import StaffStatusEnum
from betik_app_staff.models import DepartmentModel, TitleModel, StaffTypeModel, StaffModel, PassiveReasonModel, \
    PassiveStaffLogModel, DismissReasonModel, DismissStaffLogModel


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentModel
        fields = ['id', 'name']
        table_fields = [
            IntegerField('id', _('Department ID')),
            StringField('name', _('Department'))
        ]


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleModel
        fields = ['id', 'name']
        table_fields = [
            IntegerField('id', _('Title ID')),
            StringField('name', _('Title'))
        ]


class StaffTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffTypeModel
        fields = ['id', 'name']
        table_fields = [
            IntegerField('id', _('Staff Type ID')),
            StringField('name', _('Staff Type'))
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
            fields = [
                IntegerField('id', 'ID'),
                IntegerField('status_code', _('Status Code')),
                StringField('status', _('Status')),
                StringField('registration_number', _('Registration Number')),
                DateField('start_date', _('Start Date')),
                DateField('finish_date', _('Finish Date')),

            ]

            person_fields = resolvers.get_table_fields_from_serializer_class(NaturalPersonSerializer)
            for k, v in enumerate(person_fields):
                v.code = 'person.' + v.code
                if v.code == 'id':
                    v.label = _('Person ID')
                fields.append(v)

            department_fields = resolvers.get_table_fields_from_serializer_class(DepartmentSerializer)
            for k, v in enumerate(department_fields):
                department_fields[k].code = 'department.' + v.code

            staff_type_fields = resolvers.get_table_fields_from_serializer_class(StaffTypeSerializer)
            for k, v in enumerate(staff_type_fields):
                staff_type_fields[k].code = 'staff_type.' + v.code

            title_fields = resolvers.get_table_fields_from_serializer_class(TitleSerializer)
            for k, v in enumerate(title_fields):
                title_fields[k].code = 'title.' + v.code

            return fields


class PassiveReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassiveReasonModel
        fields = ['id', 'explain']

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', _('Passive Reason ID')),
                StringField('explain', _('Passive Reason'))
            ]


class StaffSetPassiveSerializer(serializers.ModelSerializer):
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffModel.objects.all(), source='staff', write_only=True)
    staff = StaffSerializer(read_only=True)
    reason_id = serializers.PrimaryKeyRelatedField(queryset=PassiveReasonModel.objects.all(), source='reason',
                                                   write_only=True)
    reason = PassiveReasonSerializer(read_only=True)

    class Meta:
        model = PassiveStaffLogModel
        fields = ['id', 'staff_id', 'staff', 'reason_id', 'reason', 'date']

    def validate(self, attrs):
        attrs = super().validate(attrs)

        staff = attrs.get('staff')
        if staff.status != StaffStatusEnum.ACTIVE:
            error = _('Staff is not active')
            raise serializers.ValidationError(error)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(validated_data)

        staff = validated_data.get('staff')
        date = validated_data.get('date')

        staff.finish_date = date
        staff.status = StaffStatusEnum.PASSIVE
        staff.save()

        return instance


class PassiveStaffLogSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    reason = PassiveReasonSerializer(read_only=True)

    class Meta:
        model = PassiveStaffLogModel
        fields = ['id', 'staff', 'reason', 'date']

        @staticmethod
        def table_fields():
            staff_fields = resolvers.get_table_fields_from_serializer_class(StaffSerializer)
            for k, v in enumerate(staff_fields):
                staff_fields[k].code = 'staff.' + v.code
                if v.code == 'id':
                    staff_fields[k].label = _('Staff ID')

            reason_fields = resolvers.get_table_fields_from_serializer_class(PassiveReasonSerializer)
            for k, v in enumerate(reason_fields):
                reason_fields[k].code = 'reason.' + v.code

            return [
                       IntegerField('id', _('Passive Log ID')),
                       DateField('date', _('Passive Date'))
                   ] + staff_fields + reason_fields


class DismissReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DismissReasonModel
        fields = ['id', 'explain']

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', _('Dismiss Reason ID')),
                StringField('explain', _('Dismiss Reason'))
            ]


class StaffSetDismissSerializer(serializers.ModelSerializer):
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffModel.objects.all(), source='staff', write_only=True)
    staff = StaffSerializer(read_only=True)
    reason_id = serializers.PrimaryKeyRelatedField(queryset=DismissReasonModel.objects.all(), source='reason',
                                                   write_only=True)
    reason = PassiveReasonSerializer(read_only=True)

    class Meta:
        model = DismissStaffLogModel
        fields = ['id', 'staff_id', 'staff', 'reason_id', 'reason', 'date']

    def validate(self, attrs):
        attrs = super().validate(attrs)

        staff = attrs.get('staff')
        if staff.status == StaffStatusEnum.DISMISS:
            error = _('Staff is dismiss')
            raise serializers.ValidationError(error)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(validated_data)

        staff = validated_data.get('staff')
        date = validated_data.get('date')

        staff.finish_date = date
        staff.status = StaffStatusEnum.DISMISS
        staff.save()

        return instance


class DismissStaffLogSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    reason = DismissReasonSerializer(read_only=True)

    class Meta:
        model = DismissStaffLogModel
        fields = ['id', 'staff', 'reason', 'date']

        @staticmethod
        def table_fields():
            staff_fields = resolvers.get_table_fields_from_serializer_class(StaffSerializer)
            for k, v in enumerate(staff_fields):
                staff_fields[k].code = 'staff.' + v.code
                if v.code == 'id':
                    staff_fields[k].label = _('Staff ID')

            reason_fields = resolvers.get_table_fields_from_serializer_class(PassiveReasonSerializer)
            for k, v in enumerate(reason_fields):
                reason_fields[k].code = 'reason.' + v.code

            return [
                       IntegerField('id', _('Dismiss ID')),
                       DateField('date', _('Dismiss Date'))
                   ] + staff_fields + reason_fields
