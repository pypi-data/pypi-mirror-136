import datetime

from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, StringField, DateField, BoolField, DateTimeField

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from betik_app_staff.enums import AnnualLeaveDurationEnum
from betik_app_staff.models import StaffTypeModel, AnnualLeaveRuleModel
from betik_app_staff.serializers.staff import StaffTypeSerializer


class AnnualLeavePeriodField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if data is None:
            msg = _('required')
            raise ValidationError([msg])

        if not isinstance(data, dict):
            msg = _('Incorrect type. Expected a dict, but got %s')
            raise ValidationError(msg % type(data).__name__)

        if 'start_year' not in data:
            msg = _('required')
            raise ValidationError({'start_year': [msg]})

        if 'duration' not in data:
            msg = _('required')
            raise ValidationError({'duration': [msg]})

        start_year = data.get('start_year', None)
        if start_year is None:
            msg = _('required')
            raise ValidationError({'start_year': [msg]})

        finish_year = data.get('finish_year', None)

        duration = data.get('duration', None)
        if duration is None:
            msg = _('required')
            raise ValidationError({'duration': [msg]})

        try:
            d = int(duration)
        except Exception as e:
            msg = _('must be number')
            raise ValidationError({'duration': [msg]})

        try:
            y1 = int(start_year)
        except Exception as e:
            msg = _('must be number')
            raise ValidationError({'start_year': [msg]})

        if d < 0:
            msg = _('must be bigger than or equal 0')
            raise ValidationError({'duration': [msg]})

        if y1 < 0:
            msg = _('must be bigger than or equal zero')
            raise ValidationError({'start_year': [msg]})

        if finish_year is not None:
            try:
                y2 = int(finish_year)
            except Exception as e:
                msg = _('must be number')
                raise ValidationError({'finish_year': [msg]})

            if y2 <= 0:
                msg = _('must be bigger than 0')
                raise ValidationError({'finish_year': [msg]})

            if y1 >= y2:
                msg = _('must be bigger than start year(%(v)d)') % {'v': y1}
                raise ValidationError({'finish_year': [msg]})

        return data


class AnnualLeaveRuleSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    staff_type_id = serializers.PrimaryKeyRelatedField(source='staff_type', queryset=StaffTypeModel.objects.all(),
                                                       write_only=True)
    staff_type = StaffTypeSerializer(read_only=True)
    periods = serializers.ListField(child=AnnualLeavePeriodField(), min_length=1)
    periods_arr_str = serializers.SerializerMethodField(source='periods')
    duration_type_code = serializers.ChoiceField(source='duration_type', choices=AnnualLeaveDurationEnum.types)
    duration_type = serializers.CharField(source='get_duration_type_display', read_only=True)

    def get_periods_arr_str(self, value):
        ret_val = []
        if value.periods:
            for p in value.periods:
                if p.get('finish_year'):
                    msg = _("%(y1)d - %(y2)d Years; %(duration)d") % {
                        'y1': p['start_year'],
                        'y2': p['finish_year'],
                        'duration': p['duration']
                    }
                else:
                    msg = _("%(y1)d Years and beyond; %(duration)d") % {
                        'y1': p['start_year'],
                        'duration': p['duration']
                    }
                ret_val.append(msg)

        return ret_val

    class Meta:
        model = AnnualLeaveRuleModel
        fields = [
            'id', 'start_date', 'finish_date', 'staff_type_id', 'staff_type', 'periods', 'periods_arr_str', 'active',
            'duration_type_code', 'duration_type', 'forward_next_year', 'forward_year', 'created_dt', 'created_user',
            'updated_dt', 'updated_user'
        ]

        read_only_fields = [
            'id', 'active', 'duration', 'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', 'ID'),
                DateField('start_date', _('Start Date')),
                DateField('finish_date', _('Finish Date')),
                StringField('periods_str_arr', _('Periods')),
                IntegerField('duration_type', _('Duration Type')),
                StringField('forward_next_year', _('Forward Next Year')),
                BoolField('forward_year', _('Forward Year')),
                StringField('staff_type.name', _('Staff Type')),
                BoolField('active', _('Active')),
                DateTimeField('created_dt', _('Created Time')),
                StringField('created_user', _('Created User')),
                DateTimeField('updated_dt', _('Updated Time')),
                StringField('updated_user', _('Updated User'))
            ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        finish_date = attrs.get('finish_date', self.instance.finish_date if self.instance else None)
        start_date = attrs.get('start_date', self.instance.start_date if self.instance else None)
        periods = attrs.get('periods', self.instance.periods if self.instance else None)
        staff_type = attrs.get('staff_type', self.instance.staff_type if self.instance else None)

        today = datetime.datetime.today().date()

        if self.instance:

            # kayıt akitfse, bitiş tarihi dışında hiçbir şey değiştirilemez
            if self.instance.active:
                exclude_fields = ['finish_date']
                fields = self.instance._meta.get_fields()
                for field in fields:
                    try:
                        value = getattr(self.instance, field.name)
                    except:
                        value = None
                    if field.name not in exclude_fields:
                        if value != attrs.get(field.name, getattr(self.instance, field.name)):
                            msg = _('Anything other than the finish date of active registrations cannot be changed')
                            raise serializers.ValidationError(msg)

            # geçerliliğini yitirmiş kayıtlar hiçbir şekilde değiştirilemez
            if self.instance.finish_date and self.instance.finish_date <= today:
                msg = _('expired records cannot be changed in any way')
                raise serializers.ValidationError(msg)

            # başlama tarihi değiştirilmek isteniyorsa, bugünden sonraki bir tarih olmalı
            if start_date != self.instance.start_date and start_date <= today:
                msg = _('bigger than today')
                raise serializers.ValidationError({'start_date': [msg]})

            # bitiş tarihi değiştirilmek isteniyorsa, bugünden sonraki bir tarih olmalı
            if finish_date and finish_date != self.instance.finish_date and finish_date <= today:
                msg = _('bigger than today')
                raise serializers.ValidationError({'finish_date': [msg]})
        else:
            # başlama tarihi, bugünden sonraki bir tarih olmalı
            if start_date <= today:
                msg = _('bigger than today')
                raise serializers.ValidationError({'start_date': [msg]})

            # bitiş tarihi, bugünden sonraki bir tarih olmalı
            if finish_date and finish_date <= today:
                msg = _('bigger than today')
                raise serializers.ValidationError({'finish_date': [msg]})

        if finish_date and finish_date <= start_date:
            msg = _('bigger than start date(%(date)s)') % {'date': start_date.strftime('%d %B %Y')}
            raise serializers.ValidationError({'finish_date': [msg]})

        # dönemleri kontrol et
        if len(periods) > 1:
            # son dönemin, son yılı null olmalı
            for (k, v) in enumerate(periods):
                if k == len(periods) - 1:
                    if v.get('finish_year'):
                        msg = _("must not be set year")
                        raise serializers.ValidationError({'periods': {k: {'finish_year': [msg]}}})
                    else:
                        continue
                # son dönem hariç, diğer tüm dönemlerin son yılı girilmeli
                if not v.get('finish_year'):
                    msg = _("must be set a year")
                    raise serializers.ValidationError({'periods': {k: {'finish_year': [msg]}}})
        else:
            if periods[0].get('finish_year'):
                msg = _("must not be set year")
                raise serializers.ValidationError({'periods': {0: {'finish_year': [msg]}}})

        # n. dönemin son yılı n+1. dönemin ilk yılına eşit olmalı
        for (k, v) in enumerate(periods):
            if k == 0:
                continue

            prev_period = periods[k - 1]
            if v['start_year'] != prev_period['finish_year']:
                msg = _("must be equal to %(p)d. period's finish year(%(year)d)") % {
                    'p': k,
                    'year': prev_period['finish_year']
                }
                raise serializers.ValidationError({'periods': {k: {'start_year': [msg]}}})

        # başlama tarihi, diğer tarihlerle çakışmasın(d1 <= dd1 < d2)
        qs1 = AnnualLeaveRuleModel.objects.filter(staff_type=staff_type, start_date__lte=start_date,
                                                  finish_date__gt=start_date)

        # başlama tarihi, diğer tarihlerle çakışmasın(d1 <= dd1 < ve sonrası)
        qs2 = AnnualLeaveRuleModel.objects.filter(staff_type=staff_type, start_date__lte=start_date,
                                                  finish_date__isnull=True)

        qs = qs1 | qs2
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            inst = qs[:1].get()
            if inst.finish_date:
                msg = _('Conflicts with the dates(%(date1)s - %(date1)s) of record #%(id)s') % {
                    'id': inst.id,
                    'date1': inst.start_date.strftime("%d %B %Y"),
                    'date2': inst.finish_date.strftime("%d %B %Y")
                }
            else:
                msg = _('Conflicts with the dates(%(date1)s and later) of record #%(id)s') % {
                    'id': inst.id,
                    'date1': inst.start_date.strftime("%d %B %Y")
                }
            raise serializers.ValidationError({'start_date': [msg]})

        if finish_date:
            # bitiş tarihi, diğer tarihlerle çakışmasın(d1 < dd2 <= d2)
            qs1 = AnnualLeaveRuleModel.objects.filter(staff_type=staff_type, start_date__lt=finish_date,
                                                      finish_date__gte=finish_date)
            # bitiş tarihi, diğer tarihlerle çakışmasın(d1 < dd2 <= ve sonrası)
            qs2 = AnnualLeaveRuleModel.objects.filter(staff_type=staff_type, start_date__lt=finish_date,
                                                      finish_date__isnull=True)
            qs = qs1 | qs2
            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            if qs.exists():
                inst = qs[:1].get()
                if inst.finish_date:
                    msg = _('Conflicts with the dates(%(date1)s - %(date1)s) of record #%(id)s') % {
                        'id': inst.id,
                        'date1': inst.start_date.strftime("%d %B %Y"),
                        'date2': inst.finish_date.strftime("%d %B %Y")
                    }
                else:
                    msg = _('Conflicts with the dates(%(date1)s and later) of record #%(id)s') % {
                        'id': inst.id,
                        'date1': inst.start_date.strftime("%d %B %Y")
                    }
                raise serializers.ValidationError({'finish_date': [msg]})

            # başlama ve bitiş tarihi başka bir kaydı kapsamasın(dd1 <= d1 < d2 <= dd2)
            qs1 = AnnualLeaveRuleModel.objects.filter(staff_type=staff_type, start_date__gte=start_date,
                                                      finish_date__lte=finish_date)

            # başlama ve bitiş tarihi başka bir kaydı kapsamasın(dd1 <= d1 < ve sonrası <= dd2)
            qs2 = AnnualLeaveRuleModel.objects.filter(staff_type=staff_type, start_date__gte=start_date,
                                                      start_date__lt=finish_date,
                                                      finish_date__isnull=True)
            qs = qs1 | qs2
            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            if qs.exists():
                inst = qs[:1].get()
                if inst.finish_date:
                    msg = _('Contains with the dates(%(date1)s - %(date2)s) of record #%(id)s') % {
                        'id': inst.id,
                        'date1': inst.start_date.strftime("%d %B %Y"),
                        'date2': inst.finish_date.strftime("%d %B %Y")
                    }
                else:
                    msg = _('The start date(%(date1)s) of record #%(id)did, conflicts with the entered dates') % {
                        'id': inst.id,
                        'date1': inst.start_date.strftime("%d %B %Y")
                    }
                raise serializers.ValidationError([msg])

        else:
            # bitiş tarihi girilmemiş

            # başlama tarihi başka bir kaydı kapsamasın(dd1 <= d1 < d2 <= ve sonrası)
            qs = AnnualLeaveRuleModel.objects.filter(staff_type=staff_type, start_date__gte=start_date)

            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            if qs.exists():
                inst = qs[:1].get()
                if inst.finish_date:
                    msg = _('Contains with the dates(%(date1)s - %(date2)s) of record #%(id)s') % {
                        'id': inst.id,
                        'date1': inst.start_date.strftime("%d %B %Y"),
                        'date2': inst.finish_date.strftime("%d %B %Y")
                    }
                else:
                    msg = _('Contains with the dates(%(date1)s and later) of record #%(id)s') % {
                        'id': inst.id,
                        'date1': inst.start_date.strftime("%d %B %Y")
                    }

                raise serializers.ValidationError({'detail': [msg]})

        return attrs
