from django.db.models import Case, CharField, Value, When, F, Count
from django.utils.encoding import force_str
from betik_app_staff.models import StaffModel

from betik_app_staff.serializers_statistic import StaffGenderStatisticSerializer, StaffBloodStatisticSerializer, \
    StaffRegisterProvinceStatisticSerializer, StaffEducationStatisticSerializer, StaffDepartmentStatisticSerializer, \
    StaffStaffTypeStatisticSerializer, StaffTitleStatisticSerializer
from betik_app_staff.views.staff import StaffPaginateView


class WithChoices(Case):
    def __init__(self, model, field, condition=None, then=None, **lookups):
        fields = field.split('__')
        for f in fields:
            model = model._meta.get_field(f)

            if model.related_model:
                model = model.related_model

        # choices = dict(model._meta.get_field(field).flatchoices)
        choices = dict(model.flatchoices)
        whens = [When(**{field: k, 'then': Value(force_str(v))}) for k, v in choices.items()]
        super().__init__(*whens, output_field=CharField())


class StatisticStaffGenderPaginateView(StaffPaginateView):
    """
        paginate staff-gender statistic

        paginate staff-gender statistic
    """
    serializer_class = StaffGenderStatisticSerializer
    ordering_fields = ['gender_exp', 'count']
    ordering = ['-count']

    def get_queryset(self):
        qs = super().get_queryset().select_related('person')
        qs = qs.values('person__gender')
        qs = qs.annotate(
            count=Count("person__gender"),
            gender_exp=WithChoices(StaffModel, 'person__gender'),
            gender_code=F('person__gender')
        )
        return qs


class StatisticStaffBloodPaginateView(StaffPaginateView):
    """
        paginate staff-blood statistic

        paginate staff-blood statistic
    """
    serializer_class = StaffBloodStatisticSerializer
    ordering_fields = ['blood_exp', 'count']
    ordering = ['-count']

    def get_queryset(self):
        qs = super().get_queryset().select_related('person')
        qs = qs.values('person__blood')
        qs = qs.annotate(
            count=Count("person__blood"),
            blood_exp=WithChoices(StaffModel, 'person__blood'),
            blood_code=F('person__blood')
        )
        return qs


class StatisticStaffEducationPaginateView(StaffPaginateView):
    """
        paginate staff-education statistic

        paginate staff-education statistic
    """
    serializer_class = StaffEducationStatisticSerializer
    ordering_fields = ['education_exp', 'count']
    ordering = ['-count']

    def get_queryset(self):
        qs = super().get_queryset().select_related('person')
        qs = qs.values('person__education_status')
        qs = qs.annotate(
            count=Count("person__education_status"),
            education_exp=WithChoices(StaffModel, 'person__education_status'),
            education_code=F('person__education_status')
        )
        return qs


class StatisticStaffRegisterProvincePaginateView(StaffPaginateView):
    """
        paginate staff-register province statistic

        paginate staff-register province statistic
    """
    serializer_class = StaffRegisterProvinceStatisticSerializer
    ordering_fields = ['province_name', 'count']
    ordering = ['-count']

    def get_queryset(self):
        qs = super().get_queryset().select_related('person')
        qs = qs.values('person__register_district__province')
        qs = qs.annotate(
            count=Count("person__register_district__province"),
            province_name=F('person__register_district__province__name'),
            province_id=F('person__register_district__province__id')
        )
        return qs


class StatisticStaffDepartmentPaginateView(StaffPaginateView):
    """
        paginate staff-department statistic

        paginate staff-department statistic
    """
    serializer_class = StaffDepartmentStatisticSerializer
    ordering_fields = ['department_name', 'count']
    ordering = ['-count']

    def get_queryset(self):
        qs = super().get_queryset().select_related('person')
        qs = qs.values('department')
        qs = qs.annotate(
            count=Count("department"),
            department_name=F('department__name'),
            department_id=F('department__id')
        )
        return qs


class StatisticStaffStaffTypePaginateView(StaffPaginateView):
    """
        paginate staff-staff type statistic

        paginate staff-staff type statistic
    """
    serializer_class = StaffStaffTypeStatisticSerializer
    ordering_fields = ['staff_type_name', 'count']
    ordering = ['-count']

    def get_queryset(self):
        qs = super().get_queryset().select_related('person')
        qs = qs.values('department')
        qs = qs.annotate(
            count=Count("staff_type"),
            staff_type_name=F('staff_type__name'),
            staff_type_id=F('staff_type__id')
        )
        return qs


class StatisticStaffTitlePaginateView(StaffPaginateView):
    """
        paginate staff-title statistic

        paginate staff-title statistic
    """
    serializer_class = StaffTitleStatisticSerializer
    ordering_fields = ['title_name', 'count']
    ordering = ['-count']

    def get_queryset(self):
        qs = super().get_queryset().select_related('person')
        qs = qs.values('title')
        qs = qs.annotate(
            count=Count("title"),
            title_name=F('title__name'),
            title_id=F('title__id')
        )
        return qs
