from django.conf.urls import url

from betik_app_staff.views import DepartmentListView, DepartmentCreateView, DepartmentUpdateView, DepartmentDeleteView, \
    TitleListView, TitleCreateView, TitleUpdateView, TitleDeleteView, StaffTypeListView, StaffTypeCreateView, \
    StaffTypeUpdateView, StaffTypeDeleteView, StaffPaginateView, StaffCreateView, StaffUpdateView

urlpatterns = [
    url(r'^department/list/?$', DepartmentListView.as_view(), name='department-list'),
    url(r'^department/create/?$', DepartmentCreateView.as_view(), name='department-create'),
    url(r'^department/update/(?P<pk>[0-9]+)/?$', DepartmentUpdateView.as_view(), name='department-update'),
    url(r'^department/delete/(?P<pk>[0-9]+)/?$', DepartmentDeleteView.as_view(), name='department-delete'),

    url(r'^title/list/?$', TitleListView.as_view(), name='title-list'),
    url(r'^title/create/?$', TitleCreateView.as_view(), name='title-create'),
    url(r'^title/update/(?P<pk>[0-9]+)/?$', TitleUpdateView.as_view(), name='title-update'),
    url(r'^title/delete/(?P<pk>[0-9]+)/?$', TitleDeleteView.as_view(), name='title-delete'),

    url(r'^staff-type/list/?$', StaffTypeListView.as_view(), name='staff-type-list'),
    url(r'^staff-type/create/?$', StaffTypeCreateView.as_view(), name='staff-type-create'),
    url(r'^staff-type/update/(?P<pk>[0-9]+)/?$', StaffTypeUpdateView.as_view(), name='staff-type-update'),
    url(r'^staff-type/delete/(?P<pk>[0-9]+)/?$', StaffTypeDeleteView.as_view(), name='staff-type-delete'),

    url(r'^staff/paginate/?$', StaffPaginateView.as_view(), name='staff-paginate'),
    url(r'^staff/create/?$', StaffCreateView.as_view(), name='staff-create'),
    url(r'^staff/update/(?P<pk>[0-9]+)/?$', StaffUpdateView.as_view(), name='staff-update'),
]
