from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import DepartmentFilter
from betik_app_staff.models import DepartmentModel
from betik_app_staff.serializers.staff import DepartmentSerializer
from betik_app_staff.serializers_merge import DepartmentMergeSerializer


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


class DepartmentMergeView(generics.UpdateAPIView):
    """
        merge a department

        merge a department
    """
    queryset = DepartmentModel.objects.all()
    serializer_class = DepartmentMergeSerializer
