from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import StaffTypeFilter
from betik_app_staff.models import StaffTypeModel
from betik_app_staff.serializers.staff import StaffTypeSerializer
from betik_app_staff.serializers_merge import StaffTypeMergeSerializer


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


class StaffTypeMergeView(generics.UpdateAPIView):
    """
        merge a staff type

        merge a staff type
    """
    queryset = StaffTypeModel.objects.all()
    serializer_class = StaffTypeMergeSerializer
