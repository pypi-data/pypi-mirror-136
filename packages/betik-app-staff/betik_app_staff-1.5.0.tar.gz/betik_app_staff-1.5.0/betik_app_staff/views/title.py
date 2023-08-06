from betik_app_util.paginations import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics

from betik_app_staff.filters import TitleFilter
from betik_app_staff.models import TitleModel
from betik_app_staff.serializers.staff import TitleSerializer
from betik_app_staff.serializers_merge import TitleMergeSerializer


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


class TitleMergeView(generics.UpdateAPIView):
    """
        merge a title

        merge a title
    """
    queryset = TitleModel.objects.all()
    serializer_class = TitleMergeSerializer
