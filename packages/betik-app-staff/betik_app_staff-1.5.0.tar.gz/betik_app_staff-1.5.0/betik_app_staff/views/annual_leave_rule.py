import datetime
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

from betik_app_staff.filters import AnnualLeaveRuleFilter
from betik_app_staff.models import AnnualLeaveRuleModel
from betik_app_staff.serializers.annual_leave_rule import AnnualLeaveRuleSerializer
from betik_app_util.paginations import StandardPagination


class AnnualLeaveRuleCreateView(generics.CreateAPIView):
    """
        create a annual leave rule

        create a annual leave rule
    """
    queryset = AnnualLeaveRuleModel.objects.all()
    serializer_class = AnnualLeaveRuleSerializer


class AnnualLeaveRuleUpdateView(generics.UpdateAPIView):
    """
        update a annual leave rule

        update a annual leave rule
    """
    queryset = AnnualLeaveRuleModel.objects.all()
    serializer_class = AnnualLeaveRuleSerializer


class AnnualLeaveRuleDeleteView(generics.DestroyAPIView):
    """
        delete a annual leave rule

        delete a annual leave rule
    """
    queryset = AnnualLeaveRuleModel.objects.all()

    def perform_destroy(self, instance):
        today = datetime.datetime.today().date()

        # şu an aktif olan kayıt silinemez
        if instance.active:
            msg = _('active record can not be deleted')
            raise ValidationError({'detail': [msg]})

        # geçmiş kayıtlar silinemez
        if instance.finish_date and instance.finish_date <= today:
            msg = _('outdated record can not be deleted')
            raise ValidationError({'detail': [msg]})

        super().perform_destroy(instance)


class AnnualLeaveRulePaginateView(generics.ListAPIView):
    """
        paginate annual leave rules

        paginate annual leave rules
    """
    queryset = AnnualLeaveRuleModel.objects.all()
    serializer_class = AnnualLeaveRuleSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = AnnualLeaveRuleFilter
    ordering_fields = ['start_date', 'staff_type']
    ordering = ['-start_date', 'staff_type']
