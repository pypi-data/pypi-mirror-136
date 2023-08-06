from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from betik_app_util.table_fields import IntegerField, StringField, DateField, DateTimeField

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from betik_app_staff.models import HolidayModel


class HolidaySerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    class Meta:
        model = HolidayModel
        fields = ['id', 'start_date', 'finish_date', 'name', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        read_only_fields = ['id', 'created_dt', 'created_user', 'updated_dt', 'updated_user']

        @staticmethod
        def table_fields():
            return [
                IntegerField('id', 'ID'),
                DateField('start_date', _('Start Date')),
                DateField('finish_date', _('Finish Date')),
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

        if finish_date and finish_date <= start_date:
            raise serializers.ValidationError({'finish_date': [
                _('must be greater than start date(%(date)s)') % {'date': start_date.strftime('%d %B %Y')}
            ]})

        return attrs
