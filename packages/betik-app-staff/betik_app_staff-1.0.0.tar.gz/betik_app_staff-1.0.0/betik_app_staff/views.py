from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from betik_app_staff.filters import StaffFilter, PassiveReasonFilter, DepartmentFilter, TitleFilter, StaffTypeFilter, \
    PassiveStaffLogFilter, DismissReasonFilter, DismissStaffLogFilter
from betik_app_staff.models import DepartmentModel, TitleModel, StaffTypeModel, StaffModel, PassiveReasonModel, \
    PassiveStaffLogModel, DismissReasonModel, DismissStaffLogModel
from betik_app_staff.serializers import DepartmentSerializer, TitleSerializer, StaffTypeSerializer, StaffSerializer, \
    PassiveReasonSerializer, StaffSetPassiveSerializer, PassiveStaffLogSerializer, DismissReasonSerializer, \
    StaffSetDismissSerializer, DismissStaffLogSerializer


class DepartmentPaginateView(generics.ListAPIView):
    """
        paginate departments

        paginate departments
    """
    queryset = DepartmentModel.objects.all()
    serializer_class = DepartmentSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = DepartmentFilter
    ordering_fields = ['name']
    ordering = ['name']


class DepartmentCreateView(generics.CreateAPIView):
    """
        create a department

        create a department
    """
    queryset = DepartmentModel.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentUpdateView(generics.UpdateAPIView):
    """
        update a department

        update a department
    """
    queryset = DepartmentModel.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentDeleteView(generics.DestroyAPIView):
    """
        delete a department

        delete a department
    """
    queryset = DepartmentModel.objects.all()


class TitlePaginateView(generics.ListAPIView):
    """
        paginate titles

        paginate titles
    """
    queryset = TitleModel.objects.all()
    serializer_class = TitleSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = TitleFilter
    ordering_fields = ['name']
    ordering = ['name']


class TitleCreateView(generics.CreateAPIView):
    """
        create a title

        create a title
    """
    queryset = TitleModel.objects.all()
    serializer_class = TitleSerializer


class TitleUpdateView(generics.UpdateAPIView):
    """
        update a title

        update a title
    """
    queryset = TitleModel.objects.all()
    serializer_class = TitleSerializer


class TitleDeleteView(generics.DestroyAPIView):
    """
        delete a title

        delete a title
    """
    queryset = TitleModel.objects.all()


class StaffTypePaginateView(generics.ListAPIView):
    """
        paginate staff types

        paginate staff types
    """
    queryset = StaffTypeModel.objects.all()
    serializer_class = StaffTypeSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = StaffTypeFilter
    ordering_fields = ['name']
    ordering = ['name']


class StaffTypeCreateView(generics.CreateAPIView):
    """
        create a staff type

        create a staff type
    """
    queryset = StaffTypeModel.objects.all()
    serializer_class = StaffTypeSerializer


class StaffTypeUpdateView(generics.UpdateAPIView):
    """
        update a staff type

        update a staff type
    """
    queryset = StaffTypeModel.objects.all()
    serializer_class = StaffTypeSerializer


class StaffTypeDeleteView(generics.DestroyAPIView):
    """
        delete a staff type

        delete a staff type
    """
    queryset = StaffTypeModel.objects.all()


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
        return super().get_queryset().prefetch_related('person')


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


class PassiveReasonCreateView(generics.CreateAPIView):
    """
        create a passive reason

        create a passive reason
    """
    queryset = PassiveReasonModel.objects.all()
    serializer_class = PassiveReasonSerializer


class PassiveReasonUpdateView(generics.UpdateAPIView):
    """
        update a passive reason

        update a passive reason
    """
    queryset = PassiveReasonModel.objects.all()
    serializer_class = PassiveReasonSerializer


class PassiveReasonDeleteView(generics.DestroyAPIView):
    """
        delete a passive reason

        delete a passive reason
    """
    queryset = PassiveReasonModel.objects.all()


class PassiveReasonPaginateView(generics.ListAPIView):
    """
        paginate passive reasons

        paginate passive reasons
    """
    queryset = PassiveReasonModel.objects.all()
    serializer_class = PassiveReasonSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = PassiveReasonFilter
    ordering_fields = ['explain']
    ordering = ['explain']


class StaffSetPassiveView(generics.CreateAPIView):
    """
        set passive a staff

        set passive a staff
    """
    queryset = PassiveStaffLogModel.objects.all()
    serializer_class = StaffSetPassiveSerializer


class PassiveStaffLogPaginateView(generics.ListAPIView):
    """
        paginate passive staff logs

        paginate passive staff logs
    """
    queryset = PassiveStaffLogModel.objects.all()
    serializer_class = PassiveStaffLogSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = PassiveStaffLogFilter
    ordering_fields = [
        'staff__person__identity', 'staff__person__name', 'staff__person__last_name', 'staff__registration_number',
        'date', 'reason__explain'
    ]
    ordering = ['-date']


class DismissReasonCreateView(generics.CreateAPIView):
    """
        create a dismiss reason

        create a dismiss reason
    """
    queryset = DismissReasonModel.objects.all()
    serializer_class = DismissReasonSerializer


class DismissReasonUpdateView(generics.UpdateAPIView):
    """
        update a dismiss reason

        update a dismiss reason
    """
    queryset = DismissReasonModel.objects.all()
    serializer_class = DismissReasonSerializer


class DismissReasonDeleteView(generics.DestroyAPIView):
    """
        delete a dismiss reason

        delete a dismiss reason
    """
    queryset = DismissReasonModel.objects.all()


class DismissReasonPaginateView(generics.ListAPIView):
    """
        paginate dismiss reasons

        paginate dismiss reasons
    """
    queryset = DismissReasonModel.objects.all()
    serializer_class = DismissReasonSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = DismissReasonFilter
    ordering_fields = ['explain']
    ordering = ['explain']


class StaffSetDismissView(generics.CreateAPIView):
    """
        set dismiss a staff

        set dismiss a staff
    """
    queryset = DismissStaffLogModel.objects.all()
    serializer_class = StaffSetDismissSerializer


class DismissStaffLogPaginateView(generics.ListAPIView):
    """
        paginate dismiss staff logs

        paginate dismiss staff logs
    """
    queryset = DismissStaffLogModel.objects.all()
    serializer_class = DismissStaffLogSerializer
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = DismissStaffLogFilter
    ordering_fields = [
        'staff__person__identity', 'staff__person__name', 'staff__person__last_name', 'staff__registration_number',
        'date', 'reason__explain'
    ]
    ordering = ['-date']
