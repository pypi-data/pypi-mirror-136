import datetime

from betik_app_util import resolvers
from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, StringField, DateTimeField, BoolField

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import empty

from betik_app_staff.enums import LeaveTypeEnum, LeaveDurationTypeEnum
from betik_app_staff.leave_calculator import leave_calculate, get_annual_leave_right_of_leave
from betik_app_staff.models import LeaveTypeModel, StaffLeaveModel, StaffModel, AnnualLeaveRuleModel
from betik_app_staff.serializers.annual_leave_rule import AnnualLeaveRuleSerializer
from betik_app_staff.serializers.staff import StaffSerializer


class LeaveTypeSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    class Meta:
        model = LeaveTypeModel
        fields = ['id', 'type', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        read_only_fields = ['id', 'created_dt', 'created_user', 'updated_dt', 'updated_user']

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', _('Leave Type ID')),
                StringField('type', _('Leave Type')),
                DateTimeField('created_dt', _('Created Time')),
                StringField('created_user', _('Created User')),
                DateTimeField('updated_dt', _('Updated Time')),
                StringField('updated_user', _('Updated User'))
            ]


class StaffLeaveSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffModel.objects.all(), write_only=True, source='staff')
    staff = StaffSerializer(read_only=True)
    leave_type_id = serializers.PrimaryKeyRelatedField(queryset=LeaveTypeModel.objects.all(), write_only=True,
                                                       source='leave_type')
    leave_type = LeaveTypeSerializer(read_only=True)
    duration_type_code = serializers.ChoiceField(choices=LeaveDurationTypeEnum.types, write_only=True,
                                                 source='duration_type', required=False, allow_null=True,
                                                 allow_blank=True)
    duration_type = serializers.CharField(read_only=True, source='get_duration_type_display')

    class Meta:
        model = StaffLeaveModel
        fields = [
            'id', 'start_dt', 'finish_dt', 'work_start_dt', 'staff_id', 'staff', 'leave_type_id', 'leave_type',
            'duration', 'duration_type_code', 'duration_type', 'active', 'expired', 'created_dt', 'created_user',
            'updated_dt', 'updated_user'
        ]
        read_only_fields = [
            'finish_dt', 'work_start_dt', 'active', 'expired', 'created_dt', 'created_user', 'updated_dt',
            'updated_user'
        ]

        @staticmethod
        def table_fields():
            fields = [
                IntegerField('id', _('Leave Type ID')),
                DateTimeField('start_dt', _('Leave Type')),
                DateTimeField('finish_dt', _('Leave Type')),
                DateTimeField('work_start_dt', _('Leave Type')),
                IntegerField('duration', _('Leave Type')),
                StringField('duration_type', _('Leave Type')),
                BoolField('active', _('Leave Type')),
                BoolField('expired', _('Leave Type')),
                StringField('leave_type.type', _('Leave Type')),
                DateTimeField('created_dt', _('Created Time')),
                StringField('created_user', _('Created User')),
                DateTimeField('updated_dt', _('Updated Time')),
                StringField('updated_user', _('Updated User'))
            ]
            staff_fields = resolvers.get_table_fields_from_serializer_class(StaffSerializer)
            for k, v in enumerate(staff_fields):
                v.code = 'staff.' + v.code
                if v.code == 'id':
                    v.label = _('Staff ID')
                fields.append(v)

            return fields

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.back_dates = None

    def validate(self, attrs):
        attrs = super().validate(attrs)

        start_dt = attrs.get('start_dt', self.instance.start_dt if self.instance else None)
        leave_type = attrs.get('leave_type', self.instance.leave_type if self.instance else None)
        staff = attrs.get('staff', self.instance.staff if self.instance else None)
        duration_type = attrs.get('duration_type', None)
        duration = attrs.get('duration')
        today = datetime.datetime.today().date()
        now = datetime.datetime.today()

        if not staff.active:
            msg = _('Staff is passive')
            raise serializers.ValidationError({'staff_id': [msg]})

        # saniyeyi sıfır yap
        start_time = datetime.time(hour=start_dt.hour, minute=start_dt.minute, second=0, microsecond=0)
        start_dt = datetime.datetime.combine(start_dt, start_time)

        if leave_type.code == LeaveTypeEnum.ANNUAL_LEAVE:
            if duration_type is not None:
                msg = _('If leave type is annual leave, not required')
                raise serializers.ValidationError({'duration_type_code': [msg]})

            rule = AnnualLeaveRuleModel.objects.get_rule_on_date(start_dt, staff.staff_type)
            if not rule:
                msg = _('Annual leave rule were not determined for the %(staff_type)s on %(date)s') % {
                    'staff_type': staff.staff_type.name,
                    'date': start_dt.strftime('%d %B %Y')
                }
                raise serializers.ValidationError(msg)

            duration_type = rule.duration_type

            try:
                right_of_leave = get_annual_leave_right_of_leave(start_dt, staff)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        else:
            if duration_type is None:
                msg = _('If leave type is not annual leave, required')
                raise serializers.ValidationError({'duration_type_code': [msg]})

        # saat izni ise, start_dt 15'er dakikalık periyotlarda olmalı
        # saat izni değil ise, start_dt saat başı olmalı
        if duration_type == LeaveDurationTypeEnum.HOUR and start_dt.minute % 15 != 0:
            msg = _('It should be in 15-minute periods')
            raise serializers.ValidationError({'start_dt': [msg]})
        elif duration_type != LeaveDurationTypeEnum.HOUR and start_dt.minute != 0:
            msg = _('It should be hourly')
            raise serializers.ValidationError({'start_dt': [msg]})

        if duration_type == LeaveDurationTypeEnum.HOUR:
            # saat izni ise, başlama tarihi şimdiki zamandan sonra olmalı
            # saat izni değilse, başlama tarihi bugünden sonraki bir tarih olmalı
            if not self.instance and start_dt <= now:
                msg = _('Bigger than %(dt)s') % {'dt': now.strftime("%d %B %Y %H:%M")}
                raise serializers.ValidationError({'start_dt': [msg]})
        else:
            if not self.instance and start_dt.date() <= today:
                msg = _('Bigger than today')
                raise serializers.ValidationError({'start_dt': [msg]})

        # başlangıç tarihi değiştirilmek isteniyor
        if duration_type == LeaveDurationTypeEnum.HOUR:
            if self.instance and self.instance.start_dt != start_dt:
                if self.instance.start_dt <= now:
                    msg = _('The start date cannot be changed because the leave has started')
                    raise serializers.ValidationError({'start_dt': [msg]})
                elif start_dt <= now:
                    msg = _('Bigger than %(dt)s') % {'dt': now.strftime("%d %B %Y %H:%M")}
                    raise serializers.ValidationError({'start_dt': [msg]})
        else:
            if self.instance and self.instance.start_dt != start_dt:
                if self.instance.start_dt.date() <= today:
                    msg = _('The start date cannot be changed because the leave has started')
                    raise serializers.ValidationError({'start_dt': [msg]})
                elif start_dt.date() <= today:
                    msg = _('Bigger than today')
                    raise serializers.ValidationError({'start_dt': [msg]})

        try:
            self.back_dates = leave_calculate(staff, start_dt, duration, duration_type)
            finish_dt = self.back_dates['finish_dt']
        except Exception as e:
            raise serializers.ValidationError(str(e))

        if duration_type == LeaveDurationTypeEnum.HOUR:
            # izin tarihi bitişi bugünden sonraki bir tarih olmalı
            # eğer saat izni veriliyorsa, şimdiki zamandan sonra olmalı
            if not self.instance and finish_dt <= now:
                msg = _('Bigger than %(dt)s') % {'dt': now.strftime("%d %B %Y %H:%M")}
                raise serializers.ValidationError({'finish_dt': [msg]})
        else:
            if not self.instance and finish_dt.date() <= today:
                msg = _('Bigger than today')
                raise serializers.ValidationError({'finish_dt': [msg]})

        # bitiş tarihi değiştirilmek isteniyor
        if duration_type == LeaveDurationTypeEnum.HOUR:
            if self.instance and self.instance.finish_dt != finish_dt:
                if self.instance.finish_dt <= now:
                    msg = _('The finish date cannot be changed because the leave has finished')
                    raise serializers.ValidationError({'finish_dt': [msg]})
                elif finish_dt <= now:
                    msg = _('Bigger than %(dt)s') % {'dt': now.strftime("%d %B %Y %H:%M")}
                    raise serializers.ValidationError({'finish_dt': [msg]})
        else:
            if self.instance and self.instance.finish_dt != finish_dt:
                if self.instance.finish_dt.date() <= today:
                    msg = _('The finish date cannot be changed because the leave has finished')
                    raise serializers.ValidationError({'finish_dt': [msg]})
                elif finish_dt.date() <= today:
                    msg = _('Bigger than today')
                    raise serializers.ValidationError({'finish_dt': [msg]})

        # diğer izinlerle çakışma var mı?
        qs = StaffLeaveModel.objects.filter_staff_leave_on_date_range(start_dt, finish_dt, staff)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            inst_conflicting = qs[:1].get()
            msg = _('There is conflict with another leave date(%(leave_type)s %(date1)s - %(date2)s)') % {
                'leave_type': inst_conflicting.leave_type.type,
                'date1': inst_conflicting.start_dt.strftime('%d %B %Y %H:%M'),
                'date2': inst_conflicting.finish_dt.strftime('%d %B %Y %H:%M')
            }
            raise serializers.ValidationError(msg)

        return attrs

    def create(self, validated_data):
        finish_date = self.back_dates['finish_dt']
        work_start_dt = self.back_dates['work_start_dt']

        validated_data['finish_dt'] = finish_date
        validated_data['work_start_dt'] = work_start_dt
        return super().create(validated_data)

    def update(self, instance, validated_data):
        finish_date = self.back_dates['finish_dt']
        work_start_dt = self.back_dates['work_start_dt']

        validated_data['finish_dt'] = finish_date
        validated_data['work_start_dt'] = work_start_dt

        return super().update(instance, validated_data)


class StaffAnnualLeaveItemSerializer(serializers.Serializer):
    start_date = serializers.DateField(read_only=True, help_text=_(
        'the start date of each working year, based on the employment date of the staff'))
    finish_date = serializers.DateField(read_only=True,
                                        help_text=_('1 year after the starting date of the period of the staff'))
    day = serializers.IntegerField(read_only=True, help_text=_('vested annual leave entitlement at period'))
    used_day = serializers.IntegerField(read_only=True, help_text=_('annual leave used at period'))
    unused_day = serializers.IntegerField(read_only=True, help_text=_('annual leave unused at period'))
    error = serializers.CharField(read_only=True, help_text=_('annual leave unused at period'))
    working_year = serializers.IntegerField(read_only=True, help_text=_('working time of the staff as year'))
    total_unused_day = serializers.IntegerField(read_only=True, help_text=_(
        'total leave entitlement at the end of the period, with any past unused leaves'))
    annual_leave_rule = AnnualLeaveRuleSerializer(read_only=True,
                                                  help_text=_('which annual leave rule is subject to at that period'))


class StaffAnnualLeaveReportSerializer(serializers.Serializer):
    leaves = serializers.ListField(child=StaffAnnualLeaveItemSerializer(), read_only=True)
    total_unused_day = serializers.IntegerField(read_only=True)
