from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from betik_app_staff.filters import StaffFilter
from betik_app_staff.models import DepartmentModel, TitleModel, StaffTypeModel, StaffModel
from betik_app_staff.serializers import DepartmentSerializer, TitleSerializer, StaffTypeSerializer, StaffSerializer


class DepartmentListView(generics.ListAPIView):
    """
        list all departments

        list all departments
    """
    queryset = DepartmentModel.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
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


class TitleListView(generics.ListAPIView):
    """
        list all titles

        list all titles
    """
    queryset = TitleModel.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
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


class StaffTypeListView(generics.ListAPIView):
    """
        list all staff types

        list all staff types
    """
    queryset = StaffTypeModel.objects.all()
    serializer_class = StaffTypeSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
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
