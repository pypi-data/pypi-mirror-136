import datetime

from betik_app_util import resolvers
from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, DateField, StringField, BoolField, ArrayField, DateTimeField
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from betik_app_staff.models import ShiftRuleModel, ShiftRuleStaffModel, IndividualShiftModel, BusinessDayModel
from betik_app_staff.serializers.staff import StaffSerializer
from betik_app_staff.validators import StaffBusinessDaysConflictValidator


class ShiftRuleBusinessDayField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):

        if not isinstance(data, dict):
            msg = _('Incorrect type. Expected a dict, but got %s')
            raise ValidationError(msg % type(data).__name__)

        if 'work_in_official_days' not in data:
            data['work_in_official_days'] = False
        else:
            if not isinstance(data['work_in_official_days'], bool):
                data['work_in_official_days'] = bool(data['work_in_official_days'])

        if 'shift_no' not in data or data['shift_no'] is None:
            msg = _('required')
            raise ValidationError({'shift_no': [msg]})

        try:
            d = int(data['shift_no'])
        except Exception as e:
            msg = _('must be a number')
            raise ValidationError({'shift_no': [msg]})

        if d <= 0:
            msg = _('must be bigger than 0')
            raise ValidationError({'shift_no': [msg]})

        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day in days:
            if day not in data:
                msg = _('not found')
                raise ValidationError({day: [msg]})

            if not isinstance(data[day], dict):
                data[day] = None
                continue

            if 'start_time' not in data[day] or not data[day]['start_time']:
                msg = _('required')
                raise ValidationError({day: {'start_time': [msg]}})

            if 'work_hour' not in data[day] or data[day]['work_hour'] is None:
                msg = _('required')
                raise ValidationError({day: {'work_hour': [msg]}})

            try:
                datetime.datetime.strptime(data[day]['start_time'], '%H:%M')
            except Exception as e:
                msg = _('Incorrect time format. Expected `%H:%M`')
                raise ValidationError({day: {'start_time': [msg]}})

            try:
                d = int(data[day]['work_hour'])
            except Exception as e:
                msg = _('must be a number')
                raise ValidationError({day: {'work_hour': [msg]}})

            if d <= 0:
                msg = _('must be bigger than 0')
                raise ValidationError({day: {'work_hour': [msg]}})

            if d > 24:
                msg = _('must be less than %(hour)d') % {'hour': 24}
                raise ValidationError({day: {'work_hour': [msg]}})

        # birbiri ardına gelen vardiya saatleini kontrol et.
        # n. çıkış saati, (n+1). giriş saatiyle çakışmasın
        for day_index1 in range(0, 6):
            business_day_n = data[days[day_index1]]
            if business_day_n:
                dt = datetime.datetime.strptime(business_day_n['start_time'], '%H:%M')
                day_diff = dt.weekday() - day_index1
                n_start_time = (dt - datetime.timedelta(days=day_diff)).replace(hour=dt.hour, minute=dt.minute,
                                                                                second=0, microsecond=0)

                n_finish_time = n_start_time + datetime.timedelta(hours=business_day_n['work_hour'])
            else:
                continue

            for day_index2 in range(day_index1 + 1, 7):
                day_n1_key = days[day_index2]
                business_day_n1 = data[day_n1_key]
                if business_day_n1:
                    dt = datetime.datetime.strptime(business_day_n1['start_time'], '%H:%M')
                    day_diff = dt.weekday() - day_index2
                    n1_start_time = (dt - datetime.timedelta(days=day_diff)).replace(hour=dt.hour, minute=dt.minute,
                                                                                     second=0, microsecond=0)

                    if n_finish_time > n1_start_time:
                        msg = _('bigger than or equal %(time)s') % {'time': n_finish_time.strftime("%H:%M")}
                        raise ValidationError({day_n1_key: {'start_time': [msg]}})

                    break

        # vardiyadaki döngüde, son günün çıkış saati ile, döngü başındaki ilk günün başlama saati çakışmasın
        last_day = None
        first_day = None
        for day_index in range(0, 7):
            if first_day is None and data[days[day_index]]:
                first_day = data[days[day_index]]
                first_day['day_index'] = day_index
                data['first_weekday_key'] = days[day_index]
                data['first_weekday_index'] = day_index

            if data[days[day_index]]:
                last_day = data[days[day_index]]
                last_day['day_index'] = day_index
                data['last_weekday_key'] = days[day_index]
                data['last_weekday_index'] = day_index

        if first_day and last_day and first_day['day_index'] != last_day['day_index']:
            dt = datetime.datetime.strptime(first_day['start_time'], '%H:%M')
            day_diff = dt.weekday() - first_day['day_index']
            start_time_of_first_day = (dt - datetime.timedelta(days=day_diff)).replace(hour=dt.hour, minute=dt.minute,
                                                                                       second=0,
                                                                                       microsecond=0)

            dt = datetime.datetime.strptime(last_day['start_time'], '%H:%M')
            day_diff = dt.weekday() - last_day['day_index']
            start_time_of_last_day = (dt - datetime.timedelta(days=day_diff)).replace(hour=dt.hour, minute=dt.minute,
                                                                                      second=0,
                                                                                      microsecond=0)

            finish_time_of_last_day = start_time_of_last_day + datetime.timedelta(hours=last_day['work_hour'])

            is_ring = finish_time_of_last_day.day >= 8

            if is_ring:
                while finish_time_of_last_day.day >= 8:
                    finish_time_of_last_day -= datetime.timedelta(weeks=1)

                if finish_time_of_last_day > start_time_of_first_day:
                    msg = _('bigger than or equal %(time)s') % {'time': finish_time_of_last_day.strftime("%H:%M")}
                    day = days[first_day['day_index']]
                    raise ValidationError({day: {'start_time': [msg]}})
            else:
                if finish_time_of_last_day < start_time_of_first_day:
                    msg = _('bigger than or equal %(time)s') % {'time': finish_time_of_last_day.strftime("%H:%M")}
                    day = days[first_day['day_index']]
                    raise ValidationError({day: {'start_time': [msg]}})

        return data


class ShiftRuleSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    business_days = serializers.ListField(child=ShiftRuleBusinessDayField(), min_length=2)
    business_days_str = serializers.SerializerMethodField(source='get_business_days_str')

    class Meta:
        model = ShiftRuleModel

        fields = [
            'id', 'start_date', 'finish_date', 'business_days', 'period_start_date', 'period_end_date',
            'period_duration', 'active', 'name', 'business_days_str', 'created_dt', 'created_user',
            'updated_dt', 'updated_user'
        ]
        read_only_fields = [
            'id', 'period_start_date', 'period_end_date', 'active', 'business_days_str', 'created_dt', 'created_user',
            'updated_dt', 'updated_user'
        ]

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', 'ID'),
                StringField('name', 'Name'),
                DateField('start_date', _('Start Date')),
                DateField('finish_date', _('Finish Date')),
                DateField('period_start_date', _('Period Start Date')),
                DateField('period_end_date', _('Period Finish Date')),
                IntegerField('period_duration', _('Period Duration')),
                BoolField('active', _('Active')),
                ArrayField('business_days_str', _('Business Days')),
                DateTimeField('created_dt', _('Created Time')),
                StringField('created_user', _('Created User')),
                DateTimeField('updated_dt', _('Updated Time')),
                StringField('updated_user', _('Updated User'))
            ]

    def get_business_days_str(self, value):
        ret_val = []
        for bw in value.business_days:
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            day_names = [
                _('Monday'),
                _('Tuesday'),
                _('Wednesday'),
                _('Thursday'),
                _('Friday'),
                _('Saturday'),
                _('Sunday')
            ]

            shift_no = bw.get('shift_no')
            row_str = _("Shift No") + ":" + str(shift_no) + " "
            for k, d in enumerate(days):
                bd = bw.get(d)

                if bd:
                    start_time = bw.get(d).get('start_time')
                    work_hour = bw.get(d).get('work_hour')
                    if start_time:
                        row_str += day_names[k] + ":" + start_time + " (" + str(work_hour) + ")"
                    else:
                        row_str += day_names[k] + ":-"
                else:
                    row_str += day_names[k] + ":-"

                if k != len(days) - 1:
                    row_str += ' | '
            ret_val.append(row_str)

        return ret_val

    def validate(self, attrs):
        attrs = super().validate(attrs)

        finish_date = attrs.get('finish_date', self.instance.finish_date if self.instance else None)
        start_date = attrs.get('start_date', self.instance.start_date if self.instance else None)
        business_days = attrs.get('business_days', self.instance.business_days if self.instance else None)
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

        if finish_date and start_date >= finish_date:
            msg = _('bigger than start date(%(date)s)') % {'date': start_date.strftime('%d %B %Y')}
            raise serializers.ValidationError({'finish_date': [msg]})

        # başlama tarihi pazartesi gününe denk gelmeli
        if start_date.weekday() != 0:
            msg = _('must fall on monday')
            raise serializers.ValidationError({'start_date': [msg]})

        # bitiş tarihi varsa, pazartesi gününe denk gelmeli
        if finish_date and finish_date.weekday() != 0:
            msg = _('must fall on monday')
            raise serializers.ValidationError({'finish_date': [msg]})

        # vardiya numaralarını kontrol et
        # 1'den başlayıp ardışık olarak gitmesi gerekir
        sorted_business_days = sorted(business_days, key=lambda kv: kv['shift_no'])
        for k, v in enumerate(sorted_business_days):
            if k + 1 != v['shift_no']:
                msg = _('must be %(no)d') % {'no': k + 1}
                raise serializers.ValidationError({'business_days': {k: {'shift_no': [msg]}}})

        # n. vardiyanın son gününün bitiş saati, (n+1). vardiyanın ilk gününün başlama saati ile çakışmamalı
        for k1, v1 in enumerate(sorted_business_days):
            last_day_n = v1[v1['last_weekday_key']]
            last_day_n_weekday_index = v1['last_weekday_index']

            for k2 in range(k1 + 1, len(sorted_business_days)):
                v2 = sorted_business_days[k2]
                first_day_n1 = v2[v2['first_weekday_key']]
                first_day_n1_weekday_index = v2['first_weekday_index']

                if last_day_n and first_day_n1:
                    dt = datetime.datetime.strptime(last_day_n['start_time'], '%H:%M')
                    day_diff = dt.weekday() - last_day_n_weekday_index
                    start_time_n = (dt - datetime.timedelta(days=day_diff)).replace(hour=dt.hour, minute=dt.minute,
                                                                                    second=0, microsecond=0)
                    finish_time_n = start_time_n + datetime.timedelta(hours=last_day_n['work_hour'])

                    dt = datetime.datetime.strptime(first_day_n1['start_time'], '%H:%M')
                    day_diff = dt.weekday() - first_day_n1_weekday_index
                    start_time_n1 = (dt - datetime.timedelta(days=day_diff)).replace(hour=dt.hour, minute=dt.minute,
                                                                                     second=0, microsecond=0)

                    is_ring = finish_time_n.day >= 8
                    if is_ring:
                        while finish_time_n.day >= 8:
                            finish_time_n -= datetime.timedelta(weeks=1)

                        if start_time_n1 < finish_time_n:
                            msg = _('bigger than or equal %(time)s') % {'time': finish_time_n.strftime('%H:%M')}
                            raise serializers.ValidationError(
                                {'business_days': {k2: {v2['first_weekday_key']: {'start_time': [msg]}}}})
                    else:
                        if start_time_n <= start_time_n1 < finish_time_n:
                            msg = _('bigger than or equal %(time)s') % {'time': finish_time_n.strftime('%H:%M')}
                            raise serializers.ValidationError(
                                {'business_days': {k2: {v2['first_weekday_key']: {'start_time': [msg]}}}})

                    break

        # sonuncu vardiyanın son gününün bitiş saati, ilk vardiyanın ilk gününün başlama saati ile çakışmamalı
        shift_first = sorted_business_days[0]
        shift_last = sorted_business_days[len(sorted_business_days) - 1]

        first_day_key_in_first_shift = shift_first['first_weekday_key']
        first_day_in_first_shift = shift_first[first_day_key_in_first_shift]
        first_day_weekday_in_first_shift = shift_first['first_weekday_index']

        last_day_key_in_last_shift = shift_last['last_weekday_key']
        last_day_in_last_shift = shift_last[last_day_key_in_last_shift]
        last_day_weekday_in_last_shift = shift_last['last_weekday_index']

        if first_day_in_first_shift and last_day_in_last_shift:

            dt = datetime.datetime.strptime(first_day_in_first_shift['start_time'], '%H:%M')
            day_diff = dt.weekday() - first_day_weekday_in_first_shift
            start_time_of_first_day_in_first_shift = (dt - datetime.timedelta(days=day_diff)).replace(hour=dt.hour,
                                                                                                      minute=dt.minute,
                                                                                                      second=0,
                                                                                                      microsecond=0)

            dt = datetime.datetime.strptime(last_day_in_last_shift['start_time'], '%H:%M')
            day_diff = dt.weekday() - last_day_weekday_in_last_shift
            start_time_of_last_day_in_last_shift = (dt - datetime.timedelta(days=day_diff)).replace(hour=dt.hour,
                                                                                                    minute=dt.minute,
                                                                                                    second=0,
                                                                                                    microsecond=0)
            finish_time_of_last_day_in_last_shift = start_time_of_last_day_in_last_shift + datetime.timedelta(
                hours=last_day_in_last_shift['work_hour'])

            is_ring = finish_time_of_last_day_in_last_shift.day >= 8

            if is_ring:
                while finish_time_of_last_day_in_last_shift.day >= 8:
                    finish_time_of_last_day_in_last_shift -= datetime.timedelta(weeks=1)

                if finish_time_of_last_day_in_last_shift > start_time_of_first_day_in_first_shift:
                    msg = _('bigger than %(time)s') % {
                        'time': finish_time_of_last_day_in_last_shift.strftime('%H:%M')
                    }
                    raise serializers.ValidationError(
                        {'business_days': {0: {first_day_key_in_first_shift: {'start_time': [msg]}}}})
            else:
                if finish_time_of_last_day_in_last_shift < start_time_of_first_day_in_first_shift:
                    msg = _('bigger than %(time)s') % {
                        'time': finish_time_of_last_day_in_last_shift.strftime('%H:%M')
                    }
                    raise serializers.ValidationError(
                        {'business_days': {0: {first_day_key_in_first_shift: {'start_time': [msg]}}}})

        # vardiya kuralına bağlı personellerin, atandığı diğer vardiya kurallarıyla, bu vardiya kuralının tarihleri çakışmamalı
        # yani personel, belli bir tarihde aktif olan vardiya kurallarından aynı anda, en fazla bir tanesine kayıtlı olabilir
        if self.instance:
            # bu tarihlerle çakışan kayıtları bul
            qs1 = ShiftRuleModel.objects.filter(start_date__lte=start_date, finish_date__isnull=True)
            qs2 = ShiftRuleModel.objects.filter(start_date__lte=start_date, finish_date__gt=start_date)
            qs = qs1 | qs2
            if finish_date:
                qs3 = ShiftRuleModel.objects.filter(start_date__lt=finish_date, finish_date__isnull=True)
                qs4 = ShiftRuleModel.objects.filter(start_date__lt=finish_date, finish_date__gte=finish_date)
                qs5 = ShiftRuleModel.objects.filter(start_date__gte=start_date, finish_date__lte=finish_date)
                qs = qs | qs3 | qs4 | qs5
            else:
                qs6 = ShiftRuleModel.objects.filter(start_date__gte=start_date)
                qs = qs | qs6

            qs = qs.exclude(id=self.instance.id)

            # çakışmalar var
            if qs.exists():
                # bu vardiya kuralına bağlı personelleri al
                staff_ids = ShiftRuleStaffModel.objects.values('staff__id').filter(shift_rule=self.instance)
                if staff_ids:
                    # çakışan vardiya kurallarından herhangi birinde, bu personellerden en az bir tanesi varsa hata ver
                    for shift_rule in qs:
                        qs_ = ShiftRuleStaffModel.objects.filter(shift_rule=shift_rule, staff__in=staff_ids)
                        if qs_.exists():
                            msg = _(
                                'There are %(count)d joint staff both in this shift and in the shift named %(shift_name)s. Unable to edit because the dates of these two shifts overlap') % {
                                      'count': qs_.count(),
                                      'shift_name': shift_rule.name
                                  }
                            raise serializers.ValidationError(msg)

        return attrs

    def create(self, validated_data):
        start_date = validated_data.get('start_date')
        duration = validated_data.get('period_duration')

        validated_data['period_start_date'] = start_date
        validated_data['period_end_date'] = validated_data['period_start_date'] + datetime.timedelta(weeks=duration)

        instance = super().create(validated_data)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        start_date = validated_data.get('start_date', self.instance.start_date if self.instance else None)
        duration = validated_data.get('period_duration', self.instance.period_duration if self.instance else None)

        validated_data['period_start_date'] = start_date
        validated_data['period_end_date'] = validated_data['period_start_date'] + datetime.timedelta(weeks=duration)

        before_start_date = instance.start_date
        before_finish_date = instance.finish_date

        instance = super().update(instance, validated_data)

        after_start_date = instance.start_date
        after_finish_date = instance.finish_date

        # burada belli bir zaman aralığındaki mesai saatlerinin çakışma kontrolü yapılması gerekiyor
        # mümkün olan zaman aralığını bulmak için, güncellemeden önce ve sonra ki tarihleri alıp kıyas yapılmalı
        # başlangıç tarihi için en küçük değer seçilmei
        # bitiş tarihi, önceden veya sonra null olabilir ki buda sonsuza kadar devam etsin demek
        # burada bitiş tarihini hesaplamak için;
        # 1- eğer önce ve sonra null değilse en büyük olan alınmalı
        # 2- herhangibiri null ise, kişisel vardiyada, genel iş kuralı veya vardiya kuralı arasından en büyük
        #    tarihe sahip kaydın tarihi alınır

        is_changed_date = (before_start_date != after_start_date or before_finish_date != after_finish_date)
        staff_count = instance.shift_staffs.all().count()

        # çakışma kontrolü için, tarihlerin değişmiş olması ve vardiyada personel kayıtlı olması gerekir
        if is_changed_date and staff_count > 0:
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
                # bu vardiya kuralına bağlı personelleri al
                staffs = [item.staff for item in instance.shift_staffs.all()]
                validator = StaffBusinessDaysConflictValidator(start_date, finish_date, staffs)
                validator.validate(raise_exception=True)

        return instance


class StaffAssignToShiftRuleFromQuerySerializer(SetCreatedUpdatedUserFromSerializerContextMixin,
                                                serializers.Serializer):
    shift_rule_id = serializers.PrimaryKeyRelatedField(queryset=ShiftRuleModel.objects.all(), write_only=True)
    shift_no = serializers.IntegerField(write_only=True)
    result = serializers.BooleanField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        shift_rule = attrs.get('shift_rule_id', self.instance.shift_rule if self.instance else None)
        shift_no = attrs.get('shift_no', self.instance.shift_no if self.instance else None)
        staffs = self.context.get('target_query')

        # tarihi geçmiş vardiya kuralı için işlem yapılmaz
        if shift_rule.expiry:
            msg = _('No action can be taken for an out-of-date shift rule')
            raise serializers.ValidationError({'shift_rule_id': [msg]})

        # period numarası, vardiya kuralında var mı?
        shift_nos = []
        for bd in shift_rule.business_days:
            shift_nos.append(bd.get('shift_no'))

        if shift_no not in shift_nos:
            msg = _('The shift number should have the these values; %(values)s') % {
                'values': ", ".join(str(shift_nos))
            }
            raise serializers.ValidationError({'shift_no': [msg]})

        for staff in staffs:
            # personel aynı vardiyada, başka bir dönemde ise, eğer vardiya kuralı aktif ise değişime izin verme
            try:
                inst = ShiftRuleStaffModel.objects.get(staff=staff, shift_rule=shift_rule)
                if inst.shift_no != shift_no and inst.shift_rule.active:
                    msg = _(
                        'Staff who %(identity)s identity, named %(name)s %(last_name)s, are already registered in the %(shift_no)d. shift no of this shift.') % {
                              'shift_no': inst.shift_no,
                              'identity': inst.staff.person.identity,
                              'name': inst.staff.person.name,
                              'last_name': inst.staff.person.last_name
                          }
                    raise serializers.ValidationError(msg)
            except ShiftRuleStaffModel.DoesNotExist:
                pass

            # personel başka bir vardiyada kayıtlıysa, bu vardiya ile, atanmak istenen vardiyanın tarihleri çakışmamalı
            insts = ShiftRuleStaffModel.objects.filter(staff=staff).exclude(shift_rule=shift_rule)
            for inst in insts:
                if shift_rule.is_conflict(inst.shift_rule):
                    msg = _(
                        'Staff who %(identity)s identity, named %(name)s %(last_name)s, is registered to the shift named %(registered_shift_name)s. the dates of this shift conflict with the dates of the shift named %(new_shift_name)s') % {
                              'identity': inst.staff.person.identity,
                              'name': inst.staff.person.name,
                              'last_name': inst.staff.person.last_name,
                              'registered_shift_name': inst.shift_rule.name,
                              'new_shift_name': shift_rule.name
                          }
                    raise serializers.ValidationError(msg)

        return attrs

    def update(self, instance, validated_data):
        pass

    @transaction.atomic
    def create(self, validated_data):
        validated_data = self.get_validated_data_to_create(validated_data)

        today = datetime.datetime.today().date()

        shift_rule = validated_data.get('shift_rule_id')
        shift_no = validated_data.get('shift_no')
        staffs = self.context.get('target_query')

        for staff in staffs:
            defaults = {
                'shift_no': shift_no,
                'created_user': validated_data['created_user']
            }
            ShiftRuleStaffModel.objects.update_or_create(defaults=defaults, staff=staff, shift_rule=shift_rule)

        # burada belli bir zaman aralığındaki mesai saatlerinin çakışma kontrolü yapılması gerekiyor
        # başlangıç tarihi için, mevcut kaydın başlangıç tarihi alınır
        # bitiş tarihi, null olabilir ki buda sonsuza kadar devam etsin demek
        # burada bitiş tarihini hesaplamak için;
        # kişisel vardiyada,  genel iş kuralları yada vardiya kuralları arasında en büyük tarihe sahip kaydın tarihi alınır
        start_date = shift_rule.start_date
        finish_dt = shift_rule.finish_date

        if finish_dt is not None:
            finish_date = finish_dt
        else:
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
            if isinstance(finish_date, datetime.datetime):
                finish_date = finish_date.date()

            if today < finish_date:
                # başlama tarihi seçerken şuna dikkat edilmeli
                # vardiya emrinin başlama tarihi geçmiş olabilir, bu sebeple çakışmaları
                # geçmiş tarihde değil, yarından itibaren kontrol etmek gerekir
                tomorrow = today + datetime.timedelta(days=1)
                start_date = max(start_date, tomorrow)

                validator = StaffBusinessDaysConflictValidator(start_date, finish_date, staffs)
                validator.validate(raise_exception=True)

        return {'result': True}


class ShiftRuleStaffSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    shift_rule = ShiftRuleSerializer(read_only=True)

    class Meta:
        model = ShiftRuleStaffModel
        fields = [
            'id', 'staff', 'shift_rule', 'shift_no', 'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]
        read_only_fields = [
            'id', 'staff', 'shift_rule', 'shift_no', 'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]

        @staticmethod
        def table_fields():
            fields = [
                IntegerField('id', 'ID'),
                IntegerField('shift_no', _('Shift No'))
            ]

            staff_fields = resolvers.get_table_fields_from_serializer_class(ShiftRuleSerializer)
            for k, v in enumerate(staff_fields):
                v.code = 'shift_rule.' + v.code
                v.label = _('Shift Rule') + " " + v.label
                fields.append(v)

            staff_fields = resolvers.get_table_fields_from_serializer_class(StaffSerializer)
            for k, v in enumerate(staff_fields):
                v.code = 'staff.' + v.code
                v.label = _('Staff') + " " + v.label
                fields.append(v)

            return fields
