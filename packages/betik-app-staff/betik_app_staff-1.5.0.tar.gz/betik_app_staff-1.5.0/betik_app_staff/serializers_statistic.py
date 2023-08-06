from django.utils.translation import gettext as _
from betik_app_util.table_fields import IntegerField, StringField
from rest_framework import serializers


class StaffGenderStatisticSerializer(serializers.Serializer):
    gender_code = serializers.IntegerField(read_only=True)
    gender_exp = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        @staticmethod
        def table_fields():
            return [
                IntegerField('count', _('Count')),
                StringField('gender_exp', _('Gender'))
            ]


class StaffBloodStatisticSerializer(serializers.Serializer):
    blood_code = serializers.IntegerField(read_only=True)
    blood_exp = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        @staticmethod
        def table_fields():
            return [
                IntegerField('count', _('Count')),
                StringField('blood_exp', _('Blood Group'))
            ]


class StaffEducationStatisticSerializer(serializers.Serializer):
    education_code = serializers.IntegerField(read_only=True)
    education_exp = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        @staticmethod
        def table_fields():
            return [
                IntegerField('count', _('Count')),
                StringField('education_exp', _('Education Status'))
            ]


class StaffRegisterProvinceStatisticSerializer(serializers.Serializer):
    province_id = serializers.IntegerField(read_only=True)
    province_name = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        @staticmethod
        def table_fields():
            return [
                IntegerField('count', _('Count')),
                StringField('province_name', _('Province Name'))
            ]


class StaffDepartmentStatisticSerializer(serializers.Serializer):
    department_id = serializers.IntegerField(read_only=True)
    department_name = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        @staticmethod
        def table_fields():
            return [
                IntegerField('count', _('Count')),
                StringField('department_name', _('Department'))
            ]


class StaffStaffTypeStatisticSerializer(serializers.Serializer):
    staff_type_id = serializers.IntegerField(read_only=True)
    staff_type_name = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        @staticmethod
        def table_fields():
            return [
                IntegerField('count', _('Count')),
                StringField('staff_type_name', _('Staff Type'))
            ]


class StaffTitleStatisticSerializer(serializers.Serializer):
    title_id = serializers.IntegerField(read_only=True)
    title_name = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        @staticmethod
        def table_fields():
            return [
                IntegerField('count', _('Count')),
                StringField('title_name', _('Title'))
            ]
