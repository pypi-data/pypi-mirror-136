from betik_app_util import resolvers
from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, StringField, DateTimeField, DurationMinuteField

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from betik_app_staff.models import WorkingHourModel
from betik_app_staff.serializers.staff import StaffSerializer


class WorkingHourSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    type_exp = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = WorkingHourModel
        fields = [
            'id', 'start_dt', 'finish_dt', 'work_hour', 'type_exp', 'staff', 'in_dt', 'out_dt', 'late_minute',
            'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]
        read_only_fields = [
            'id', 'start_dt', 'finish_dt', 'work_hour', 'type_exp', 'staff', 'in_dt', 'out_dt', 'late_minute',
            'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]

        @staticmethod
        def table_fields():
            staff_fields = resolvers.get_table_fields_from_serializer_class(StaffSerializer)
            for k, v in enumerate(staff_fields):
                staff_fields[k].code = 'staff.' + v.code
                if v.code == 'id':
                    staff_fields[k].label = _('Staff ID')

            return [
                       IntegerField('id', _('Passive Log ID')),
                       DateTimeField('start_dt', _('Start Working Time')),
                       DateTimeField('finish_dt', _('Finish Working Time')),
                       IntegerField('work_hour', _('Work Hour')),
                       StringField('type_exp', _('Working Type')),
                       DateTimeField('in_dt', _('Staff Start Working Time')),
                       DateTimeField('out_dt', _('Staff Finish Working Time')),
                       DurationMinuteField('late_minute', _('Late Duration')),
                       DateTimeField('created_dt', _('Created Time')),
                       StringField('created_user', _('Created User')),
                       DateTimeField('updated_dt', _('Updated Time')),
                       StringField('updated_user', _('Updated User'))
                   ] + staff_fields
