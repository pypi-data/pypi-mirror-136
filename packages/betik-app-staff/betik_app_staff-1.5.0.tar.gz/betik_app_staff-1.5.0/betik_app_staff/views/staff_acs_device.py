from betik_app_acs.serializers import PersonDevicePermissionsSetFromQuerySerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

from rest_framework.filters import OrderingFilter
from rest_framework import generics, status

from betik_app_staff.filters import StaffFilter
from betik_app_staff.models import StaffModel


class DevicePermissionAssignBulkStaffView(generics.CreateAPIView):
    """
        bulk staff send to device permission

        bulki staff send to device permission
    """
    queryset = StaffModel.objects.all()
    serializer_class = PersonDevicePermissionsSetFromQuerySerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = StaffFilter
    ordering_fields = ['person__identity', 'person__name', 'person__last_name', 'registration_number', 'start_date',
                       'status']
    ordering = ['-registration_number']

    def get_queryset(self):
        return super().get_queryset().select_related('person')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['target_query'] = self.filter_queryset(self.get_queryset())
        return context

    @swagger_auto_schema(request_body=PersonDevicePermissionsSetFromQuerySerializer,
                         responses={202: PersonDevicePermissionsSetFromQuerySerializer})
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response
