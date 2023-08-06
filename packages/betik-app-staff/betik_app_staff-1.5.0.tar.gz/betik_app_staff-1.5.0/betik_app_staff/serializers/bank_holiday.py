import datetime

from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, DateField, StringField, DateTimeField
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from betik_app_staff.models import BankHolidayModel


class BankHolidaySerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    class Meta:
        model = BankHolidayModel
        fields = [
            'id', 'start_date', 'finish_date', 'day', 'month', 'name', 'created_dt', 'created_user', 'updated_dt',
            'updated_user'
        ]
        read_only_fields = ['id', 'created_dt', 'created_user', 'updated_dt', 'updated_user']

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', 'ID'),
                DateField('start_date', _('Start Date')),
                DateField('finish_date', _('Finish Date')),
                IntegerField('day', _('Day')),
                IntegerField('month', _('Month')),
                StringField('name', _('Name')),
                DateTimeField('created_dt', _('Created Time')),
                StringField('created_user', _('Created User')),
                DateTimeField('updated_dt', _('Updated Time')),
                StringField('updated_user', _('Updated User'))
            ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        start_date = attrs.get('start_date', self.instance.start_date if self.instance else None)
        finish_date = attrs.get('finish_date', self.instance.finish_date if self.instance else None)
        day = attrs.get('day', self.instance.day if self.instance else None)
        month = attrs.get('month', self.instance.month if self.instance else None)

        if finish_date and finish_date <= start_date:
            raise serializers.ValidationError({'finish_date': [
                _('must be greater than start date(%(date)s)') % {'date': start_date.strftime('%d %B %Y')}
            ]})

        if month == 2 and day > 28:
            raise serializers.ValidationError({'day': [
                _('must be less than or equal %(day)d') % {'day': 28}
            ]})

        if month in [1, 3, 5, 7, 8, 10, 12] and day > 31:
            raise serializers.ValidationError({'day': [
                _('must be less than or equal %(day)d') % {'day': 31}
            ]})

        if month in [4, 6, 9, 11] and day > 30:
            raise serializers.ValidationError({'day': [
                _('must be less than or equal %(day)d') % {'day': 30}
            ]})

        query = BankHolidayModel.objects.filter(day=day, month=month)
        if self.instance:
            query = query.exclude(id=self.instance.id)
        if query.exists():
            this_year = datetime.datetime.today().year
            conflict_day_month = datetime.datetime(month=month, day=day, year=this_year).strftime("%d %B")
            message = _('%(day_month)s is already a bank holiday') % {'day_month': conflict_day_month}
            raise serializers.ValidationError(message)

        return attrs