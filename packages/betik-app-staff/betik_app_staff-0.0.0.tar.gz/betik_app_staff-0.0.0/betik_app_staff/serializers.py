from betik_app_person.models import NaturalPersonModel
from betik_app_person.serializers import NaturalPersonSerializer
from rest_framework import serializers

from betik_app_staff.models import DepartmentModel, TitleModel, StaffTypeModel, StaffModel


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentModel
        fields = ['id', 'name']


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleModel
        fields = ['id', 'name']


class StaffTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffTypeModel
        fields = ['id', 'name']


class StaffSerializer(serializers.ModelSerializer):
    status_code = serializers.IntegerField(source='status', read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    person_id = serializers.PrimaryKeyRelatedField(queryset=NaturalPersonModel.objects.all(), source='person',
                                                   write_only=True)
    person = NaturalPersonSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=DepartmentModel.objects.all(), source='department',
                                                       write_only=True)
    department = DepartmentSerializer(read_only=True)
    staff_type_id = serializers.PrimaryKeyRelatedField(queryset=StaffTypeModel.objects.all(), source='staff_type',
                                                       write_only=True)
    staff_type = StaffTypeSerializer(read_only=True)
    title_id = serializers.PrimaryKeyRelatedField(queryset=TitleModel.objects.all(), source='title',
                                                  write_only=True)
    title = TitleSerializer(read_only=True)

    class Meta:
        model = StaffModel
        fields = ['id', 'person_id', 'person', 'registration_number', 'department_id', 'department', 'staff_type_id',
                  'staff_type', 'title_id', 'title', 'start_date', 'finish_date', 'status_code', 'status']
        read_only_fields = ['id', 'finish_date', 'status_code', 'status', 'person', 'department', 'staff_type', 'title']
