import datetime
from copy import copy

from betik_app_util.paginations import StandardPagination
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.filters import OrderingFilter
from rest_framework import generics, status
from rest_framework.response import Response

from betik_app_staff.enums import LeaveTypeEnum
from betik_app_staff.filters import StaffLeaveFilter
from betik_app_staff.leave_calculator import get_annual_leave_right_of_leave
from betik_app_staff.models import StaffLeaveModel, StaffModel, AnnualLeaveRuleModel
from betik_app_staff.serializers.annual_leave_rule import AnnualLeaveRuleSerializer
from betik_app_staff.serializers.staff_leave import StaffLeaveSerializer, StaffAnnualLeaveReportSerializer


class StaffLeaveCreateView(generics.CreateAPIView):
    """
        create a leave for staff

        create a leave for staff
    """
    queryset = StaffLeaveModel.objects.all()
    serializer_class = StaffLeaveSerializer


class StaffLeaveUpdateView(generics.UpdateAPIView):
    """
        update a leave for staff

        update a leave for staff
    """
    queryset = StaffLeaveModel.objects.all()
    serializer_class = StaffLeaveSerializer


class StaffLeaveDeleteView(generics.DestroyAPIView):
    """
        delete a staff leave

        delete a staff leave
    """
    queryset = StaffLeaveModel.objects.all()

    @transaction.atomic
    def perform_destroy(self, instance):
        # şu an aktif olan kayıt silinemez
        if instance.active:
            msg = _('active record can not be deleted')
            raise ValidationError({'detail': [msg]})

        # geçmiş kayıtlar silinemez
        if instance.expired:
            msg = _('outdated record can not be deleted')
            raise ValidationError({'detail': [msg]})

        super().perform_destroy(instance)


class StaffLeavePaginateView(generics.ListAPIView):
    """
        paginate staff leaves

        paginate staff leaves
    """

    queryset = StaffLeaveModel.objects.all()
    serializer_class = StaffLeaveSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = StaffLeaveFilter
    ordering_fields = ['start_dt', 'finish_dt', 'staff__person__identity', 'staff__person__name',
                       'staff__person__last_name', 'staff__registration_number']
    ordering = ['-start_dt', 'staff__person__name', 'staff__person__last_name']

    def get_queryset(self):
        qs = super().get_queryset().select_related('staff', 'staff__person')

        start_dt_gte = self.kwargs.get('start_dt_gte')
        start_dt_lte = self.kwargs.get('start_dt_lte')
        qs = qs.filter(start_dt__gte=start_dt_gte, start_dt__lte=start_dt_lte)

        return qs


class AnnualLeaveReportStaffListView(generics.RetrieveAPIView):

    @swagger_auto_schema(responses={200: StaffAnnualLeaveReportSerializer})
    def get(self, request, *args, **kwargs):
        today = datetime.datetime.today().date()
        staff_id = self.kwargs['staff_id']
        inst_staff = StaffModel.objects.get(id=staff_id)
        start_date = inst_staff.start_date

        ret_val = {
            'leaves': [],
            'total_unused_day': 0
        }

        list_leave = []
        current_date = copy(start_date)
        year_of_staff = 0
        while current_date <= today:
            leave = {
                'start_date': current_date,
                'finish_date': current_date + relativedelta(years=1),
                'day': 0,
                'used_day': 0,
                'unused_day': 0,
                'error': None,
                'working_year': year_of_staff,
                'total_unused_day': 0,
                'annual_leave_rule': None
            }

            try:
                # current_date tarihinde yıllık izin hakını getir
                leave['day'] = get_annual_leave_right_of_leave(current_date, inst_staff)

                # bu sene kullandığı toplam yıllık izin
                sum_val = StaffLeaveModel.objects.filter(
                    leave_type__code=LeaveTypeEnum.ANNUAL_LEAVE,
                    staff=inst_staff,
                    start_dt__date__gte=current_date,
                    start_dt__date__lt=current_date + relativedelta(years=1)).aggregate(
                    used_day=Sum('duration'))
                used_day = sum_val.get('used_day', 0) if sum_val else 0
                leave['used_day'] = used_day if used_day else 0

                t = leave['day'] - leave['used_day']

                # sadece bu seneki kullanılmayan izinler
                leave['unused_day'] = t
                try:
                    rule = AnnualLeaveRuleModel.objects.get_rule_on_date(start_date, inst_staff.staff_type)
                    leave['annual_leave_rule'] = AnnualLeaveRuleSerializer(rule).data
                    # geçmişteki izinler bir sonraki seneye aktarılıyor mu?
                    if rule.forward_next_year:
                        if not rule.forward_year:
                            # geçmişteki kullanılmayan tüm izinler bir sonraki seneye aktarılıyor.
                            for item in list_leave:
                                t += item['unused_day']
                        else:
                            # son [rule.forward_year] sene, kullanılmayan izinler bir sonraki seneye aktarılıyor.

                            # geriye dönük [rule.forward_year] yıllık, kullanılmayan izinler toplanıyor
                            starting_working_year = len(list_leave) - rule.forward_year
                            if starting_working_year >= 0:
                                for i in range(starting_working_year, len(list_leave)):
                                    t += list_leave[i]['unused_day']

                except AnnualLeaveRuleModel.DoesNotExist:
                    pass

                leave['total_unused_day'] = t

            except Exception as e:
                leave['error'] = str(e)

            list_leave.append(leave)

            # 1 yıl sonraya git
            current_date += relativedelta(years=1)
            year_of_staff += 1

        if len(list_leave) > 1:
            last_leave = list_leave[len(list_leave) - 1]
            ret_val = {
                'leaves': list_leave,
                'total_unused_day': last_leave['total_unused_day']
            }

        return Response(ret_val, status=status.HTTP_200_OK, content_type='application/json')
