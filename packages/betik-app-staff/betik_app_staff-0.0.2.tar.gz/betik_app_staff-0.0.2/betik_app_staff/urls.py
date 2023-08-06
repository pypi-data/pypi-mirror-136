from django.urls import path
from django.utils.translation import gettext as _

from betik_app_staff.views import DepartmentListView, DepartmentCreateView, DepartmentUpdateView, DepartmentDeleteView, \
    TitleListView, TitleCreateView, TitleUpdateView, TitleDeleteView, StaffTypeListView, StaffTypeCreateView, \
    StaffTypeUpdateView, StaffTypeDeleteView, StaffPaginateView, StaffCreateView, StaffUpdateView

urlpatterns = [
    path(
        'department/list/',
        DepartmentListView.as_view(),
        name='department-list',
        kwargs={
            'name': _('Department List')
        }
    ),

    path(
        'department/create/',
        DepartmentCreateView.as_view(),
        name='department-create',
        kwargs={
            'name': _('Department Create')
        }
    ),

    path(
        'department/update/<int:pk>/',
        DepartmentUpdateView.as_view(),
        name='department-update',
        kwargs={
            'name': _('Department Update')
        }
    ),

    path(
        'department/delete/<int:pk>/',
        DepartmentDeleteView.as_view(),
        name='department-delete',
        kwargs={
            'name': _('Department Delete')
        }
    ),

    path(
        'title/list/',
        TitleListView.as_view(),
        name='title-list',
        kwargs={
            'name': _('Title List')
        }
    ),

    path(
        'title/create/',
        TitleCreateView.as_view(),
        name='title-create',
        kwargs={
            'name': _('Title Create')
        }
    ),

    path(
        'title/update/<int:pk>/',
        TitleUpdateView.as_view(),
        name='title-update',
        kwargs={
            'name': _('Title Update')
        }
    ),

    path(
        'title/delete/<int:pk>/',
        TitleDeleteView.as_view(),
        name='title-delete',
        kwargs={
            'name': _('Title Delete')
        }
    ),

    path(
        'staff-type/list/',
        StaffTypeListView.as_view(),
        name='staff-type-list',
        kwargs={
            'name': _('Staff Type List')
        }
    ),

    path(
        'staff-type/create/',
        StaffTypeCreateView.as_view(),
        name='staff-type-create',
        kwargs={
            'name': _('Staff Type Create')
        }
    ),

    path(
        'staff-type/update/<int:pk>/',
        StaffTypeUpdateView.as_view(),
        name='staff-type-update',
        kwargs={
            'name': _('Staff Type Update')
        }
    ),

    path(
        'staff-type/delete/<int:pk>/',
        StaffTypeDeleteView.as_view(),
        name='staff-type-delete',
        kwargs={
            'name': _('Staff Type Delete')
        }
    ),

    path(
        'staff/paginate/',
        StaffPaginateView.as_view(),
        name='staff-paginate',
        kwargs={
            'name': _('Staff Paginate')
        }
    ),

    path(
        'staff/create/',
        StaffCreateView.as_view(),
        name='staff-create',
        kwargs={
            'name': _('Staff Create')
        }
    ),

    path(
        'staff/update/<int:pk>/',
        StaffUpdateView.as_view(),
        name='staff-update',
        kwargs={
            'name': _('Staff Update')
        }
    ),
]
