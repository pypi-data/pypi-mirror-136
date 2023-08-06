from betik_app_util import resolvers
from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, StringField, DateField, MultiLineStringField, DateTimeField
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from betik_app_staff.enums import StaffStatusEnum
from betik_app_staff.models import ActiveReasonModel, StaffModel, ActiveStaffLogModel
from betik_app_staff.serializers.staff import StaffSerializer


class ActiveReasonSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    class Meta:
        model = ActiveReasonModel
        fields = ['id', 'explain', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        read_only_fields = ['id', 'created_dt', 'created_user', 'updated_dt', 'updated_user']

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', _('Active Reason ID')),
                StringField('explain', _('Active Reason')),
                DateTimeField('created_dt', _('Created Time')),
                StringField('created_user', _('Created User')),
                DateTimeField('updated_dt', _('Updated Time')),
                StringField('updated_user', _('Updated User'))
            ]


class StaffSetActiveSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffModel.objects.all(), source='staff', write_only=True)
    staff = StaffSerializer(read_only=True)
    reason_id = serializers.PrimaryKeyRelatedField(queryset=ActiveReasonModel.objects.all(), source='reason',
                                                   write_only=True)
    reason = ActiveReasonSerializer(read_only=True)

    class Meta:
        model = ActiveStaffLogModel
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
        if staff.status == StaffStatusEnum.ACTIVE:
            error = _('Staff is active')
            raise serializers.ValidationError(error)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(validated_data)

        staff = validated_data.get('staff')
        date = validated_data.get('date')

        staff.finish_date = None
        staff.start_date = date
        staff.status = StaffStatusEnum.ACTIVE
        staff.save()

        return instance


class ActiveStaffLogSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    reason = ActiveReasonSerializer(read_only=True)

    class Meta:
        model = ActiveStaffLogModel
        fields = ['id', 'staff', 'reason', 'date', 'detail', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        read_only_fields = ['id', 'created_dt', 'created_user', 'updated_dt', 'updated_user']

        @staticmethod
        def table_fields():
            staff_fields = resolvers.get_table_fields_from_serializer_class(StaffSerializer)
            for k, v in enumerate(staff_fields):
                staff_fields[k].code = 'staff.' + v.code
                if v.code == 'id':
                    staff_fields[k].label = _('Staff ID')

            reason_fields = resolvers.get_table_fields_from_serializer_class(ActiveReasonSerializer)
            for k, v in enumerate(reason_fields):
                reason_fields[k].code = 'reason.' + v.code

            return [
                       IntegerField('id', _('Active ID')),
                       DateField('date', _('Active Date')),
                       MultiLineStringField('detail', _('Detail')),
                       DateTimeField('created_dt', _('Created Time')),
                       StringField('created_user', _('Created User')),
                       DateTimeField('updated_dt', _('Updated Time')),
                       StringField('updated_user', _('Updated User'))
                   ] + staff_fields + reason_fields
