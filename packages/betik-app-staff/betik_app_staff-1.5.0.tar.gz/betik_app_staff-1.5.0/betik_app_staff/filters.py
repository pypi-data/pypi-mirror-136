from betik_app_person.models import NaturalPersonModel
from betik_app_util.filters import BaseIdFilter
from django.db.models import Value, Q
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from betik_app_person.enums import GenderTypeEnum

from betik_app_staff.enums import StaffStatusEnum, ShiftTypeEnum
from betik_app_staff.models import StaffModel, PassiveReasonModel, DepartmentModel, TitleModel, StaffTypeModel, \
    PassiveStaffLogModel, DismissReasonModel, DismissStaffLogModel, ActiveReasonModel, ActiveStaffLogModel, \
    BankHolidayModel, HolidayModel, BusinessDayModel, AnnualLeaveRuleModel, LeaveTypeModel, ShiftRuleModel, \
    ShiftRuleStaffModel, IndividualShiftModel, StaffLeaveModel, WorkingHourModel


class StaffFilter(BaseIdFilter):
    identity = filters.CharFilter(field_name="person__identity", lookup_expr='icontains')
    tax_number = filters.CharFilter(field_name="person__tax_number", lookup_expr='icontains')
    name = filters.CharFilter(field_name='person__name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='person__last_name', lookup_expr='icontains')
    gender = filters.ChoiceFilter(field_name='person__gender', choices=GenderTypeEnum.types)
    registration_number = filters.CharFilter(field_name='registration_number')
    status = filters.ChoiceFilter(field_name='status', choices=StaffStatusEnum.types)
    quick_search = filters.CharFilter(method='quick_search', label=_('identity, tax number, name, last name'))

    class Meta:
        model = StaffModel
        fields = ['identity', 'tax_number', 'name', 'last_name', 'gender', 'registration_number', 'status']

    def quick_search(self, queryset, name, value):
        qs = NaturalPersonModel.objects. \
            annotate(full_name=Concat('name', Value(' '), 'last_name')). \
            filter(full_name__icontains=value)

        return queryset.filter(
            Q(person__name__icontains=value) |
            Q(person__last_name__icontains=value) |
            Q(person__identity__icontains=value) |
            Q(person__tax_number__icontains=value) |
            Q(person__id__in=qs)
        )


class PassiveReasonFilter(BaseIdFilter):
    explain = filters.CharFilter(field_name="explain", lookup_expr='icontains')

    class Meta:
        model = PassiveReasonModel
        fields = ['explain']


class DepartmentFilter(BaseIdFilter):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = DepartmentModel
        fields = ['name']


class TitleFilter(BaseIdFilter):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = TitleModel
        fields = ['name']


class StaffTypeFilter(BaseIdFilter):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = StaffTypeModel
        fields = ['name']


class PassiveStaffLogFilter(BaseIdFilter):
    identity = filters.CharFilter(field_name="staff__person__identity", lookup_expr='icontains')
    tax_number = filters.CharFilter(field_name="staff__person__tax_number", lookup_expr='icontains')
    name = filters.CharFilter(field_name='staff__person__name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='staff__person__last_name', lookup_expr='icontains')
    gender = filters.ChoiceFilter(field_name='staff__person__gender', choices=GenderTypeEnum.types)
    registration_number = filters.CharFilter(field_name='staff__registration_number')
    reason_id = filters.ModelChoiceFilter(field_name='reason', queryset=PassiveReasonModel.objects.all())
    date_gte = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_lte = filters.DateFilter(field_name='date', lookup_expr='lte')
    quick_search = filters.CharFilter(method='quick_search', label=_('identity, tax number, name, last name'))

    class Meta:
        model = PassiveStaffLogModel
        fields = [
            'identity', 'tax_number', 'name', 'last_name', 'gender', 'registration_number', 'reason_id', 'date_gte',
            'date_lte'
        ]

    def quick_search(self, queryset, name, value):
        qs = NaturalPersonModel.objects. \
            annotate(full_name=Concat('name', Value(' '), 'last_name')). \
            filter(full_name__icontains=value)

        return queryset.filter(
            Q(staff__person__name__icontains=value) |
            Q(staff__person__last_name__icontains=value) |
            Q(staff__person__identity__icontains=value) |
            Q(staff__person__tax_number__icontains=value) |
            Q(staff__person__id__in=qs)
        )


class DismissReasonFilter(BaseIdFilter):
    explain = filters.CharFilter(field_name="explain", lookup_expr='icontains')

    class Meta:
        model = DismissReasonModel
        fields = ['explain']


class DismissStaffLogFilter(BaseIdFilter):
    identity = filters.CharFilter(field_name="staff__person__identity", lookup_expr='icontains')
    tax_number = filters.CharFilter(field_name="staff__person__tax_number", lookup_expr='icontains')
    name = filters.CharFilter(field_name='staff__person__name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='staff__person__last_name', lookup_expr='icontains')
    gender = filters.ChoiceFilter(field_name='staff__person__gender', choices=GenderTypeEnum.types)
    registration_number = filters.CharFilter(field_name='staff__registration_number')
    reason_id = filters.ModelChoiceFilter(field_name='reason', queryset=DismissReasonModel.objects.all())
    date_gte = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_lte = filters.DateFilter(field_name='date', lookup_expr='lte')
    quick_search = filters.CharFilter(method='quick_search', label=_('identity, tax number, name, last name'))

    class Meta:
        model = DismissStaffLogModel
        fields = [
            'identity', 'tax_number', 'name', 'last_name', 'gender', 'registration_number', 'reason_id', 'date_gte',
            'date_lte'
        ]

    def quick_search(self, queryset, name, value):
        qs = NaturalPersonModel.objects. \
            annotate(full_name=Concat('name', Value(' '), 'last_name')). \
            filter(full_name__icontains=value)

        return queryset.filter(
            Q(staff__person__name__icontains=value) |
            Q(staff__person__last_name__icontains=value) |
            Q(staff__person__identity__icontains=value) |
            Q(staff__person__tax_number__icontains=value) |
            Q(staff__person__id__in=qs)
        )


class ActiveReasonFilter(BaseIdFilter):
    explain = filters.CharFilter(field_name="explain", lookup_expr='icontains')

    class Meta:
        model = ActiveReasonModel
        fields = ['explain']


class ActiveStaffLogFilter(BaseIdFilter):
    identity = filters.CharFilter(field_name="staff__person__identity", lookup_expr='icontains')
    tax_number = filters.CharFilter(field_name="staff__person__tax_number", lookup_expr='icontains')
    name = filters.CharFilter(field_name='staff__person__name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='staff__person__last_name', lookup_expr='icontains')
    gender = filters.ChoiceFilter(field_name='staff__person__gender', choices=GenderTypeEnum.types)
    registration_number = filters.CharFilter(field_name='staff__registration_number')
    reason_id = filters.ModelChoiceFilter(field_name='reason', queryset=ActiveReasonModel.objects.all())
    date_gte = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_lte = filters.DateFilter(field_name='date', lookup_expr='lte')
    quick_search = filters.CharFilter(method='quick_search', label=_('identity, tax number, name, last name'))

    class Meta:
        model = ActiveStaffLogModel
        fields = [
            'identity', 'tax_number', 'name', 'last_name', 'gender', 'registration_number', 'reason_id', 'date_gte',
            'date_lte'
        ]

    def quick_search(self, queryset, name, value):
        qs = NaturalPersonModel.objects. \
            annotate(full_name=Concat('name', Value(' '), 'last_name')). \
            filter(full_name__icontains=value)

        return queryset.filter(
            Q(staff__person__name__icontains=value) |
            Q(staff__person__last_name__icontains=value) |
            Q(staff__person__identity__icontains=value) |
            Q(staff__person__tax_number__icontains=value) |
            Q(staff__person__id__in=qs)
        )


class BankHolidayFilter(BaseIdFilter):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = BankHolidayModel
        fields = ['name']


class HolidayFilter(BaseIdFilter):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    year = filters.NumberFilter(field_name="start_date__year")

    class Meta:
        model = HolidayModel
        fields = ['name', 'year']


class BusinessDayFilter(BaseIdFilter):
    staff_type_id = filters.ModelChoiceFilter(field_name="staff_type", queryset=StaffTypeModel.objects.all())

    class Meta:
        model = BusinessDayModel
        fields = ['staff_type_id']


class AnnualLeaveRuleFilter(BaseIdFilter):
    staff_type_id = filters.ModelChoiceFilter(field_name="staff_type", queryset=StaffTypeModel.objects.all())

    class Meta:
        model = AnnualLeaveRuleModel
        fields = ['staff_type_id']


class LeaveTypeFilter(BaseIdFilter):
    type = filters.CharFilter(field_name="type", lookup_expr='icontains')

    class Meta:
        model = LeaveTypeModel
        fields = ['type']


class ShiftRuleFilter(BaseIdFilter):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ShiftRuleModel
        fields = ['name']


class ShiftRuleStaffFilter(BaseIdFilter):
    shift_rule_id = filters.ModelChoiceFilter(field_name="shift_rule", queryset=ShiftRuleModel.objects.all())
    staff_id = filters.ModelChoiceFilter(field_name="staff", queryset=StaffModel.objects.all())

    class Meta:
        model = ShiftRuleStaffModel
        fields = ['shift_rule_id', 'staff_id']


class IndividualShiftStaffFilter(BaseIdFilter):
    staff_id = filters.ModelChoiceFilter(field_name="staff", queryset=StaffModel.objects.all())
    shift_type = filters.ChoiceFilter(field_name='type', choices=ShiftTypeEnum.types)
    finish_dt_gte = filters.DateTimeFilter(field_name='finish_dt', lookup_expr='gte')
    finish_dt_lte = filters.DateTimeFilter(field_name='finish_dt', lookup_expr='lte')

    class Meta:
        model = IndividualShiftModel
        fields = ['staff_id', 'shift_type', 'finish_dt_gte', 'finish_dt_lte']


class StaffLeaveFilter(BaseIdFilter):
    identity = filters.CharFilter(field_name="staff__person__identity", lookup_expr='icontains')
    tax_number = filters.CharFilter(field_name="staff__person__tax_number", lookup_expr='icontains')
    name = filters.CharFilter(field_name='staff__person__name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='staff__person__last_name', lookup_expr='icontains')
    gender = filters.ChoiceFilter(field_name='staff__person__gender', choices=GenderTypeEnum.types)
    registration_number = filters.CharFilter(field_name='staff__registration_number')
    quick_search = filters.CharFilter(method='staff_quick_search', label=_('identity, tax number, name, last name'))
    leave_type_id = filters.ModelChoiceFilter(field_name='leave_type', queryset=LeaveTypeModel.objects.all())
    staff_id = filters.ModelChoiceFilter(field_name='staff', queryset=StaffModel.objects.all())

    class Meta:
        model = StaffLeaveModel
        fields = [
            'identity', 'tax_number', 'name', 'last_name', 'gender', 'registration_number', 'staff_id', 'leave_type_id'
        ]

    def staff_quick_search(self, queryset, name, value):
        qs = NaturalPersonModel.objects. \
            annotate(full_name=Concat('name', Value(' '), 'last_name')). \
            filter(full_name__icontains=value)

        return queryset.filter(
            Q(staff__person__name__icontains=value) |
            Q(staff__person__last_name__icontains=value) |
            Q(staff__person__identity__icontains=value) |
            Q(staff__person__tax_number__icontains=value) |
            Q(staff__person__id__in=qs)
        )


class WorkingHourFilter(BaseIdFilter):
    identity = filters.CharFilter(field_name="staff__person__identity", lookup_expr='icontains')
    tax_number = filters.CharFilter(field_name="staff__person__tax_number", lookup_expr='icontains')
    name = filters.CharFilter(field_name='staff__person__name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='staff__person__last_name', lookup_expr='icontains')
    gender = filters.ChoiceFilter(field_name='staff__person__gender', choices=GenderTypeEnum.types)
    registration_number = filters.CharFilter(field_name='staff__registration_number')
    status = filters.ChoiceFilter(field_name='staff__status', choices=StaffStatusEnum.types)
    quick_search = filters.CharFilter(method='quick_search', label=_('identity, tax number, name, last name'))

    class Meta:
        model = WorkingHourModel
        fields = ['identity', 'tax_number', 'name', 'last_name', 'gender', 'registration_number', 'status']

    def quick_search(self, queryset, name, value):
        qs = NaturalPersonModel.objects. \
            annotate(full_name=Concat('name', Value(' '), 'last_name')). \
            filter(full_name__icontains=value)

        return queryset.filter(
            Q(staff__person__name__icontains=value) |
            Q(staff__person__last_name__icontains=value) |
            Q(staff__person__identity__icontains=value) |
            Q(staff__person__tax_number__icontains=value) |
            Q(staff__person__id__in=qs)
        )