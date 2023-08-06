import datetime

from betik_app_util import resolvers
from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, DateTimeField, StringField
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from betik_app_staff.enums import ShiftTypeEnum
from betik_app_staff.models import IndividualShiftModel, BankHolidayModel, HolidayModel
from betik_app_staff.serializers.staff import StaffSerializer
from betik_app_staff.validators import StaffBusinessDaysConflictValidator


class CustomShiftCreateBulkSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.Serializer):
    result = serializers.BooleanField(read_only=True)
    start_dt = serializers.DateTimeField(write_only=True)
    work_hour = serializers.IntegerField(write_only=True)
    shift_type = serializers.ChoiceField(choices=ShiftTypeEnum.types, write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        start_dt = attrs.get('start_dt')
        work_hour = attrs.get('work_hour')
        shift_type = attrs.get('shift_type')
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)
        staffs = self.context.get('target_query')

        today = datetime.datetime.today().date()
        if start_dt.date() <= today:
            msg = _('bigger than today')
            raise serializers.ValidationError({'start_dt': [msg]})

        if shift_type == ShiftTypeEnum.WEEKEND:
            # bu vardiya tipi sadece pazar günü için kullanılabilir
            if start_dt.weekday() != 6:
                msg = _('for this shift type, only sunday shift can be entered')
                raise serializers.ValidationError({'shift_type': [msg]})
        elif shift_type == ShiftTypeEnum.HOLIDAY:
            # bu vardiya tipi sadece tatil günlerinde kullanılabilir
            is_bank_holiday = BankHolidayModel.objects.is_holiday(start_dt)
            is_holiday = HolidayModel.objects.is_holiday(start_dt)
            if not is_holiday and not is_bank_holiday:
                msg = _('for this shift type, only holiday days can be entered')
                raise serializers.ValidationError({'shift_type': [msg]})
        elif shift_type == ShiftTypeEnum.OVERTIME:
            is_bank_holiday = BankHolidayModel.objects.is_holiday(start_dt)
            is_holiday = HolidayModel.objects.is_holiday(start_dt)
            if is_holiday or is_bank_holiday:
                msg = _('this shift type cannot be used on holidays')
                raise serializers.ValidationError({'shift_type': [msg]})

            if start_dt.weekday() == 6:
                msg = _('this shift type cannot be used on sunday')
                raise serializers.ValidationError({'shift_type': [msg]})

        for staff in staffs:
            # başlama tarihi, aynı tarihlerde başka kişisel vardiya ile çakışmasın
            qs = IndividualShiftModel.objects.filter(start_dt__lte=start_dt, finish_dt__gt=start_dt, staff=staff)
            if qs.exists():
                inst_conflict = qs[:1].get()
                msg = _(
                    'staff who has %(identity)s identity, %(name)s %(last_name)s names, conflict with individual shift which has #%(id)d no. Conflicting shift\'s dates are %(date1)s - %(date2)s') % {
                          'identity': staff.person.identity,
                          'name': staff.person.name,
                          'last_name': staff.person.last_name,
                          'id': inst_conflict.id,
                          'date1': inst_conflict.start_dt.strftime("%d %B %Y %H:%M"),
                          'date2': inst_conflict.finish_dt.strftime("%d %B %Y %H:%M")
                      }
                raise serializers.ValidationError({'start_dt': [msg]})

            # bitiş tarihi, aynı tarihlerde başka kişisel vardiya ile çakışmasın
            qs = IndividualShiftModel.objects.filter(start_dt__lt=finish_dt, finish_dt__gte=finish_dt, staff=staff)
            if qs.exists():
                inst_conflict = qs[:1].get()
                msg = _(
                    'staff who has %(identity)s identity, %(name)s %(last_name)s names, conflict with individual shift which has #%(id)d no. Conflicting shift\'s dates are %(date1)s - %(date2)s') % {
                          'identity': staff.person.identity,
                          'name': staff.person.name,
                          'last_name': staff.person.last_name,
                          'id': inst_conflict.id,
                          'date1': inst_conflict.start_dt.strftime("%d %B %Y %H:%M"),
                          'date2': inst_conflict.finish_dt.strftime("%d %B %Y %H:%M")
                      }
                raise serializers.ValidationError({'work_hour': [msg]})

            # başlama - bitiş tarihi, başka kişisel vardiyanın tarihlerini kapsamasın
            qs = IndividualShiftModel.objects.filter(start_dt__gte=start_dt, finish_dt__lte=finish_dt, staff=staff)
            if qs.exists():
                inst_conflict = qs[:1].get()
                msg = _(
                    'staff who has with %(identity)s identity, %(name)s %(last_name)s named, individual shift which has #%(id)d ID, is covered. Shift\'s covered dates: %(date1)s to %(date2)s') % {
                          'identity': staff.person.identity,
                          'name': staff.person.name,
                          'last_name': staff.person.last_name,
                          'id': inst_conflict.id,
                          'date1': inst_conflict.start_dt.strftime("%d %B %Y %H:%M"),
                          'date2': inst_conflict.finish_dt.strftime("%d %B %Y %H:%M")
                      }
                raise serializers.ValidationError(msg)

        return attrs

    def update(self, instance, validated_data):
        pass

    @transaction.atomic
    def create(self, validated_data):
        validated_data = self.get_validated_data_to_create(validated_data)
        start_dt = validated_data.get('start_dt')
        work_hour = validated_data.get('work_hour')
        shift_type = validated_data.get('shift_type')
        created_user = validated_data.get('created_user')
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)
        staffs = self.context.get('target_query')

        for staff in staffs:
            IndividualShiftModel.objects.create(
                staff=staff,
                start_dt=start_dt,
                finish_dt=finish_dt,
                work_hour=work_hour,
                type=shift_type,
                created_user=created_user
            )

        validator = StaffBusinessDaysConflictValidator(start_dt, finish_dt, staffs)
        validator.validate(raise_exception=True)

        return {'result': True}


class CustomShiftSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    type_exp = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = IndividualShiftModel
        fields = [
            'id', 'staff', 'start_dt', 'finish_dt', 'work_hour', 'type', 'type_exp', 'created_dt', 'created_user',
            'updated_dt', 'updated_user'
        ]
        read_only_fields = [
            'id', 'staff', 'start_dt', 'finish_dt', 'work_hour', 'type', 'type_exp', 'created_dt', 'created_user',
            'updated_dt', 'updated_user'
        ]

        @staticmethod
        def table_fields():
            fields = [
                IntegerField('id', 'ID'),
                DateTimeField('start_dt', _('Start Date')),
                DateTimeField('finish_dt', _('Finish Date')),
                IntegerField('work_hour', _('Work Hour')),
                StringField('type_exp', _('Shift Type')),
                DateTimeField('created_dt', _('Created Time')),
                StringField('created_user', _('Created User')),
                DateTimeField('updated_dt', _('Updated Time')),
                StringField('updated_user', _('Updated User'))
            ]

            staff_fields = resolvers.get_table_fields_from_serializer_class(StaffSerializer)
            for k, v in enumerate(staff_fields):
                v.code = 'staff.' + v.code
                v.label = _('Staff') + " " + v.label
                fields.append(v)

            return fields
