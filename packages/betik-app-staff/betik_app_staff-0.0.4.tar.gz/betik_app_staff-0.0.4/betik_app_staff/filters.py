from betik_app_util.filters import BaseIdFilter
from django_filters import rest_framework as filters
from betik_app_person.enums import GenderTypeEnum

from betik_app_staff.enums import StaffStatusEnum
from betik_app_staff.models import StaffModel


class StaffFilter(BaseIdFilter):
    identity = filters.CharFilter(field_name="person__identity", lookup_expr='icontains')
    tax_number = filters.CharFilter(field_name="person__tax_number", lookup_expr='icontains')
    name = filters.CharFilter(field_name='person__name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='person__last_name', lookup_expr='icontains')
    gender = filters.ChoiceFilter(field_name='person__gender', choices=GenderTypeEnum.types)
    registration_number = filters.CharFilter(field_name='registration_number')
    status = filters.ChoiceFilter(field_name='status', choices=StaffStatusEnum.types)

    class Meta:
        model = StaffModel
        fields = ['identity', 'tax_number', 'name', 'last_name', 'gender', 'registration_number', 'status']
