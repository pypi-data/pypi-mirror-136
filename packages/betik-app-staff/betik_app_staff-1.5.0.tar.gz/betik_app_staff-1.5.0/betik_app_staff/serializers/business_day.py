import datetime

from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, DateField, StringField, BoolField, DateTimeField
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from betik_app_staff.models import StaffTypeModel, BusinessDayModel, IndividualShiftModel, ShiftRuleModel, StaffModel
from betik_app_staff.serializers.staff import StaffTypeSerializer
from betik_app_staff.validators import StaffBusinessDaysConflictValidator


class TimeRangeField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if not data:
            return

        if not isinstance(data, dict):
            msg = _('Incorrect type. Expected a dict, but got %s')
            raise ValidationError(msg % type(data).__name__)

        if 'start_time' not in data:
            msg = _('required')
            raise ValidationError({'start_time': [msg]})

        if 'work_hour' not in data:
            msg = _('required')
            raise ValidationError({'work_hour': [msg]})

        start_time = data.get('start_time', None)
        if not start_time:
            msg = _('required')
            raise ValidationError({'start_time': [msg]})

        work_hour = data.get('work_hour', None)
        if work_hour is None:
            msg = _('required')
            raise ValidationError({'work_hour': [msg]})

        try:
            work_hour = int(work_hour)
        except Exception:
            msg = _('must be a number')
            raise ValidationError({'work_hour': [msg]})

        if work_hour <= 0:
            msg = _('bigger than zero')
            raise ValidationError({'work_hour': [msg]})

        if work_hour > 24:
            msg = _('less than 25')
            raise ValidationError({'work_hour': [msg]})

        try:
            datetime.datetime.strptime(start_time, '%H:%M')
        except Exception as e:
            msg = _('Incorrect time format. Expected `%H:%M`')
            raise ValidationError({'start_time': [msg]})

        return data


class BusinessDaySerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    name = serializers.CharField(max_length=200, required=True)
    staff_type_id = serializers.PrimaryKeyRelatedField(source='staff_type', queryset=StaffTypeModel.objects.all(),
                                                       write_only=True)
    staff_type = StaffTypeSerializer(read_only=True)
    monday = TimeRangeField(required=False, allow_null=True)
    tuesday = TimeRangeField(required=False, allow_null=True)
    wednesday = TimeRangeField(required=False, allow_null=True)
    thursday = TimeRangeField(required=False, allow_null=True)
    friday = TimeRangeField(required=False, allow_null=True)
    saturday = TimeRangeField(required=False, allow_null=True)
    sunday = TimeRangeField(required=False, allow_null=True)

    monday_str = serializers.SerializerMethodField(source='monday')
    tuesday_str = serializers.SerializerMethodField(source='tuesday')
    wednesday_str = serializers.SerializerMethodField(source='wednesday')
    thursday_str = serializers.SerializerMethodField(source='thursday')
    friday_str = serializers.SerializerMethodField(source='friday')
    saturday_str = serializers.SerializerMethodField(source='saturday')
    sunday_str = serializers.SerializerMethodField(source='sunday')

    def get_monday_str(self, value):
        if value.monday:
            return f"{value.monday['start_time']}, {value.monday['work_hour']} hours"
        return ""

    def get_tuesday_str(self, value):
        if value.tuesday:
            return f"{value.tuesday['start_time']}, {value.monday['work_hour']} hours"
        return ""

    def get_wednesday_str(self, value):
        if value.wednesday:
            return f"{value.wednesday['start_time']}, {value.monday['work_hour']} hours"
        return ""

    def get_thursday_str(self, value):
        if value.thursday:
            return f"{value.thursday['start_time']}, {value.monday['work_hour']} hours"
        return ""

    def get_friday_str(self, value):
        if value.friday:
            return f"{value.friday['start_time']}, {value.monday['work_hour']} hours"
        return ""

    def get_saturday_str(self, value):
        if value.saturday:
            return f"{value.saturday['start_time']}, {value.monday['work_hour']} hours"
        return ""

    def get_sunday_str(self, value):
        if value.sunday:
            return f"{value.sunday['start_time']}, {value.monday['work_hour']} hours"
        return ""

    class Meta:
        model = BusinessDayModel
        fields = [
            'id', 'name', 'start_date', 'finish_date', 'staff_type_id', 'staff_type', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday', 'monday_str', 'tuesday_str', 'wednesday_str',
            'thursday_str', 'friday_str', 'saturday_str', 'sunday_str', 'active', 'created_dt', 'created_user',
            'updated_dt', 'updated_user'
        ]

        read_only_fields = [
            'id', 'active', 'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', 'ID'),
                StringField('name', _('Name')),
                DateField('start_date', _('Start Date')),
                DateField('finish_date', _('Finish Date')),
                StringField('monday_str', _('Monday')),
                StringField('tuesday_str', _('Tuesday')),
                StringField('wednesday_str', _('Wednesday')),
                StringField('thursday_str', _('Thursday')),
                StringField('friday_str', _('Friday')),
                StringField('saturday_str', _('Saturday')),
                StringField('sunday_str', _('Sunday')),
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
        monday = attrs.get('monday', self.instance.monday if self.instance else None)
        tuesday = attrs.get('tuesday', self.instance.tuesday if self.instance else None)
        wednesday = attrs.get('wednesday', self.instance.wednesday if self.instance else None)
        thursday = attrs.get('thursday', self.instance.thursday if self.instance else None)
        friday = attrs.get('friday', self.instance.friday if self.instance else None)
        saturday = attrs.get('saturday', self.instance.saturday if self.instance else None)
        sunday = attrs.get('sunday', self.instance.sunday if self.instance else None)
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
            if finish_date != self.instance.finish_date and finish_date <= today:
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

        if not (monday or tuesday or wednesday or thursday or friday or saturday or sunday):
            msg = _('required a day at least')
            raise serializers.ValidationError(msg)

        # başlama tarihi, diğer tarihlerle çakışmasın(d1 <= dd1 < d2)
        qs1 = BusinessDayModel.objects.filter(staff_type=staff_type, start_date__lte=start_date,
                                              finish_date__gt=start_date)

        # başlama tarihi, diğer tarihlerle çakışmasın(d1 <= dd1 < ve sonrası)
        qs2 = BusinessDayModel.objects.filter(staff_type=staff_type, start_date__lte=start_date,
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
            qs1 = BusinessDayModel.objects.filter(staff_type=staff_type, start_date__lt=finish_date,
                                                  finish_date__gte=finish_date)
            # bitiş tarihi, diğer tarihlerle çakışmasın(d1 < dd2 <= ve sonrası)
            qs2 = BusinessDayModel.objects.filter(staff_type=staff_type, start_date__lt=finish_date,
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
            qs1 = BusinessDayModel.objects.filter(staff_type=staff_type, start_date__gte=start_date,
                                                  finish_date__lte=finish_date)

            # başlama ve bitiş tarihi başka bir kaydı kapsamasın(dd1 <= d1 < ve sonrası <= dd2)
            qs2 = BusinessDayModel.objects.filter(staff_type=staff_type, start_date__gte=start_date,
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
            qs = BusinessDayModel.objects.filter(staff_type=staff_type, start_date__gte=start_date)

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

        # birbiri ardına gelen mesai saatleini kontrol et.
        # n. çıkış saati, (n+1). giriş saatiyle çakışmasın
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day_index1 in range(0, 6):
            business_day_n = attrs.get(days[day_index1])
            if business_day_n:
                dt = datetime.datetime.strptime(business_day_n['start_time'], '%H:%M')
                day_diff = dt.weekday() - day_index1
                n_start_time = dt - datetime.timedelta(days=day_diff)
                n_start_time = n_start_time.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)
                n_finish_time = n_start_time + datetime.timedelta(hours=business_day_n['work_hour'])
            else:
                continue

            for day_index2 in range(day_index1 + 1, 7):
                day_n1_key = days[day_index2]
                business_day_n1 = attrs.get(day_n1_key)
                if business_day_n1:
                    dt = datetime.datetime.strptime(business_day_n1['start_time'], '%H:%M')
                    day_diff = dt.weekday() - day_index2
                    n1_start_time = dt - datetime.timedelta(days=day_diff)
                    n1_start_time = n1_start_time.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)
                    if n_finish_time > n1_start_time:
                        msg = _('bigger than or equal %(time)s') % {'time': n_finish_time.strftime("%H:%M")}
                        raise ValidationError({day_n1_key: {'start_time': [msg]}})
                    break

        # son günün çıkış saati ile, döngü başındaki ilk günün başlama saati çakışmasın
        last_day = None
        first_day = None
        for day_index in range(0, 7):
            if first_day is None and attrs.get(days[day_index]):
                first_day = attrs.get(days[day_index])
                first_day['day_index'] = day_index

            if attrs.get(days[day_index]):
                last_day = attrs.get(days[day_index])
                last_day['day_index'] = day_index

        if first_day and last_day and first_day['day_index'] != last_day['day_index']:
            dt = datetime.datetime.strptime(first_day['start_time'], '%H:%M')
            day_diff = dt.weekday() - first_day['day_index']
            start_time_of_first_day = dt - datetime.timedelta(days=day_diff)
            start_time_of_first_day = start_time_of_first_day.replace(hour=dt.hour, minute=dt.minute, second=0,
                                                                      microsecond=0)
            dt = datetime.datetime.strptime(last_day['start_time'], '%H:%M')
            day_diff = dt.weekday() - last_day['day_index']
            start_time_of_last_day = dt - datetime.timedelta(days=day_diff)
            start_time_of_last_day = start_time_of_last_day.replace(hour=dt.hour, minute=dt.minute, second=0,
                                                                    microsecond=0)
            finish_time_of_last_day = start_time_of_last_day + datetime.timedelta(hours=last_day['work_hour'])

            is_ring = finish_time_of_last_day.day >= 8

            if is_ring:
                while finish_time_of_last_day.day >= 8:
                    finish_time_of_last_day -= datetime.timedelta(weeks=1)

                if finish_time_of_last_day > start_time_of_first_day:
                    msg = _('bigger than or equal %(time)s') % {
                        'time': finish_time_of_last_day.strftime("%H:%M")}
                    day = days[first_day['day_index']]
                    raise ValidationError({day: {'start_time': [msg]}})
            else:
                if finish_time_of_last_day < start_time_of_first_day:
                    msg = _('bigger than or equal %(time)s') % {
                        'time': finish_time_of_last_day.strftime("%H:%M")}
                    day = days[first_day['day_index']]
                    raise ValidationError({day: {'start_time': [msg]}})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(validated_data)

        # kaydettikden sonra mesai saati çakışmalarını kontrol et
        # kaydın başlangıç ve bitiş tarihi arasındaki çakışmalara bak
        # çıkış tarihi None ise sistemdeki en büyük tarihi al
        # en büyük tarih şu şekilde seçilir
        # kişisel vardiya, vardiya kuralı ve genel iş kurallarından en büyük tarih bulunur
        start_date = instance.start_date
        finish_date = instance.finish_date
        if finish_date is None:
            max_date1 = IndividualShiftModel.objects.get_max_date_in_all_records()
            max_date2 = BusinessDayModel.objects.get_max_date_in_all_records()
            max_date3 = ShiftRuleModel.objects.get_max_date_in_all_records()

            dates = [
                max_date1,
                max_date2,
                max_date3
            ]
            dates = sorted(dates, key=lambda x: datetime.datetime.min.date() if x is None else x)
            try:
                finish_date = dates[-1:][0]
            except:
                finish_date = None

        if finish_date:
            staffs = StaffModel.objects.filter(staff_type=instance.staff_type)
            validator = StaffBusinessDaysConflictValidator(start_date, finish_date, staffs)
            validator.validate(raise_exception=True)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        today = datetime.datetime.today().date()

        before_start_date = instance.start_date
        before_finish_date = instance.finish_date
        before_staff_type = instance.staff_type

        instance = super().update(instance, validated_data)

        after_start_date = instance.start_date
        after_finish_date = instance.finish_date
        after_staff_type = instance.staff_type

        is_changed_date = (
                before_start_date != after_start_date or before_finish_date != after_finish_date or before_staff_type != after_staff_type)

        # kaydettikden sonra mesai saati çakışmalarını kontrol et
        # kaydın başlangıç ve bitiş tarihi arasındaki çakışmalara bak
        # çıkış tarihi None ise sistemdeki en büyük tarihi al
        # en büyük tarih şu şekilde seçilir
        # kişisel vardiya, vardiya kuralı ve genel iş kurallarından en büyük tarih bulunur
        if is_changed_date:
            start_date = min(before_start_date, after_start_date)

            if before_finish_date is not None and after_finish_date is not None:
                finish_date = max(before_finish_date, after_finish_date)
            else:
                max_date1 = IndividualShiftModel.objects.get_max_date_in_all_records()
                max_date2 = BusinessDayModel.objects.get_max_date_in_all_records()
                max_date3 = ShiftRuleModel.objects.get_max_date_in_all_records()

                dates = [
                    max_date1,
                    max_date2,
                    max_date3,
                    before_finish_date,
                    after_finish_date
                ]
                dates = sorted(dates, key=lambda x: datetime.datetime.min.date() if x is None else x)
                try:
                    finish_date = dates[-1:][0]
                except:
                    finish_date = None

            if finish_date:
                if isinstance(finish_date, datetime.datetime):
                    finish_date = finish_date.date()

                if today < finish_date:
                    # başlama tarihi seçerken şuna dikkat edilmeli
                    # kuralın başlama tarihi geçmiş olabilir, bu sebeple çakışmaları
                    # geçmiş tarihde değil, yarından itibaren kontrol etmek gerekir
                    tomorrow = today + datetime.timedelta(days=1)
                    start_date = max(start_date, tomorrow)

                    staffs = StaffModel.objects.filter(staff_type__in=[after_staff_type, before_staff_type])
                    validator = StaffBusinessDaysConflictValidator(start_date, finish_date, staffs)
                    validator.validate(raise_exception=True)

        return instance
