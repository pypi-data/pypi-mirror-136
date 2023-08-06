from betik_app_util import resolvers
from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, StringField, DateField, MultiLineStringField, DateTimeField
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from betik_app_staff.enums import StaffStatusEnum
from betik_app_staff.models import PassiveReasonModel, StaffModel, PassiveStaffLogModel
from betik_app_staff.serializers.staff import StaffSerializer


class PassiveReasonSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    class Meta:
        model = PassiveReasonModel
        fields = ['id', 'explain', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        read_only_fields = ['id', 'created_dt', 'created_user', 'updated_dt', 'updated_user']

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', _('Passive Reason ID')),
                StringField('explain', _('Passive Reason')),
                DateTimeField('created_dt', _('Created Time')),
                StringField('created_user', _('Created User')),
                DateTimeField('updated_dt', _('Updated Time')),
                StringField('updated_user', _('Updated User'))
            ]


class StaffSetPassiveSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffModel.objects.all(), source='staff', write_only=True)
    staff = StaffSerializer(read_only=True)
    reason_id = serializers.PrimaryKeyRelatedField(queryset=PassiveReasonModel.objects.all(), source='reason',
                                                   write_only=True)
    reason = PassiveReasonSerializer(read_only=True)

    class Meta:
        model = PassiveStaffLogModel
        fields = [
            'id', 'staff_id', 'staff', 'reason_id', 'reason', 'date', 'detail', 'created_dt', 'created_user',
            'updated_dt', 'updated_user'
        ]
        read_only_fields = [
            'id', 'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]

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
        fields = [
            'id', 'staff', 'reason', 'date', 'detail', 'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]
        read_only_fields = [
            'id', 'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]

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
                       DateField('date', _('Passive Date')),
                       MultiLineStringField('detail', _('Detail')),
                       DateTimeField('created_dt', _('Created Time')),
                       StringField('created_user', _('Created User')),
                       DateTimeField('updated_dt', _('Updated Time')),
                       StringField('updated_user', _('Updated User'))
                   ] + staff_fields + reason_fields
