from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import StaffFilter
from betik_app_staff.models import StaffModel
from betik_app_staff.serializers.staff import StaffSerializer
from betik_app_email.serializers import EmailLogCreateFromQuerySerializer
from betik_app_sms.serializers import SmsLogCreateFromQuerySerializer
from betik_app_util.paginations import StandardPagination


class StaffPaginateView(generics.ListAPIView):
    """
        paginate staffs

        paginate staffs
    """
    queryset = StaffModel.objects.all()
    serializer_class = StaffSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = StaffFilter
    ordering_fields = ['person__identity', 'person__name', 'person__last_name', 'registration_number', 'start_date',
                       'status']
    ordering = ['-registration_number']

    def get_queryset(self):
        return super().get_queryset().select_related('person')


class StaffPaginateByShiftRuleView(generics.ListAPIView):
    """
        paginate staffs that depends on shift rule

        paginate staffs that depends on shift rule
    """
    queryset = StaffModel.objects.all()
    serializer_class = StaffSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = StaffFilter
    ordering_fields = ['person__identity', 'person__name', 'person__last_name', 'registration_number', 'start_date',
                       'status']
    ordering = ['-registration_number']

    def get_queryset(self):
        shift_rule_id = self.kwargs['shift_rule_id']
        shift_no = self.kwargs['shift_no']

        qs = super().get_queryset().select_related('person')
        qs = qs.filter(shift_staffs__shift_rule=shift_rule_id, shift_staffs=shift_no)

        return qs


class StaffEmailSendView(generics.CreateAPIView):
    """
        send email to staffs

        send email to staffs
    """
    queryset = StaffModel.objects.all()
    serializer_class = EmailLogCreateFromQuerySerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = StaffFilter
    ordering_fields = ['person__identity', 'person__name', 'person__last_name', 'registration_number', 'start_date',
                       'status']
    ordering = ['-registration_number']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['target_query'] = self.filter_queryset(self.get_queryset())
        context['target_serializer'] = StaffSerializer
        return context

    def get_queryset(self):
        return super().get_queryset().select_related('person')


class StaffSmsSendView(generics.CreateAPIView):
    """
        send sms to staffs

        send sms to staffs
    """
    queryset = StaffModel.objects.all()
    serializer_class = SmsLogCreateFromQuerySerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = StaffFilter
    ordering_fields = ['person__identity', 'person__name', 'person__last_name', 'registration_number', 'start_date',
                       'status']
    ordering = ['-registration_number']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['target_query'] = self.filter_queryset(self.get_queryset())
        context['target_serializer'] = StaffSerializer
        return context

    def get_queryset(self):
        return super().get_queryset().select_related('person')


class StaffCreateView(generics.CreateAPIView):
    """
        create a staff

        create a staff
    """
    queryset = StaffModel.objects.all()
    serializer_class = StaffSerializer


class StaffUpdateView(generics.UpdateAPIView):
    """
        update a staff

        update a staff
    """
    queryset = StaffModel.objects.all()
    serializer_class = StaffSerializer
