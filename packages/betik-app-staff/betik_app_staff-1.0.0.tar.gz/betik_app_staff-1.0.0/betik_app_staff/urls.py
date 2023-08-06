from django.urls import path
from django.utils.translation import gettext_lazy as _

from betik_app_staff.views import DepartmentCreateView, DepartmentUpdateView, DepartmentDeleteView, \
    TitleCreateView, TitleUpdateView, TitleDeleteView, StaffTypeCreateView, StaffTypeUpdateView, StaffTypeDeleteView, \
    StaffPaginateView, StaffCreateView, StaffUpdateView, PassiveReasonCreateView, PassiveReasonUpdateView, \
    PassiveReasonDeleteView, PassiveReasonPaginateView, DepartmentPaginateView, TitlePaginateView, \
    StaffTypePaginateView, StaffSetPassiveView, PassiveStaffLogPaginateView, DismissReasonCreateView, \
    DismissReasonUpdateView, DismissReasonDeleteView, DismissReasonPaginateView, StaffSetDismissView, \
    DismissStaffLogPaginateView

urlpatterns = [
    path(
        'department/paginate/',
        DepartmentPaginateView.as_view(),
        name='department-paginate',
        kwargs={
            'name': _('Department Paginate')
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
        'title/paginate/',
        TitlePaginateView.as_view(),
        name='title-paginate',
        kwargs={
            'name': _('Title Paginate')
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
        'staff-type/paginate/',
        StaffTypePaginateView.as_view(),
        name='staff-type-paginate',
        kwargs={
            'name': _('Staff Type Paginate')
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

    path(
        'passive-reason/create/',
        PassiveReasonCreateView.as_view(),
        name='passive-reason-create',
        kwargs={
            'name': _('Passive Reason Create')
        }
    ),

    path(
        'passive-reason/update/<int:pk>/',
        PassiveReasonUpdateView.as_view(),
        name='passive-reason-update',
        kwargs={
            'name': _('Passive Reason Update')
        }
    ),

    path(
        'passive-reason/delete/<int:pk>/',
        PassiveReasonDeleteView.as_view(),
        name='passive-reason-delete',
        kwargs={
            'name': _('Passive Reason Delete')
        }
    ),

    path(
        'passive-reason/paginate/',
        PassiveReasonPaginateView.as_view(),
        name='passive-reason-paginate',
        kwargs={
            'name': _('Passive Reason Paginate')
        }
    ),

    path(
        'staff/set-passive/',
        StaffSetPassiveView.as_view(),
        name='staff-set-passive',
        kwargs={
            'name': _('Staff Set Passive')
        }
    ),

    path(
        'passive-staff-log/paginate/',
        PassiveStaffLogPaginateView.as_view(),
        name='passive-staff-log-paginate',
        kwargs={
            'name': _('Passive Staff Log Paginate')
        }
    ),

    path(
        'dismiss-reason/create/',
        DismissReasonCreateView.as_view(),
        name='dismiss-reason-create',
        kwargs={
            'name': _('Dismiss Reason Create')
        }
    ),

    path(
        'dismiss-reason/update/<int:pk>/',
        DismissReasonUpdateView.as_view(),
        name='dismiss-reason-update',
        kwargs={
            'name': _('Dismiss Reason Update')
        }
    ),

    path(
        'dismiss-reason/delete/<int:pk>/',
        DismissReasonDeleteView.as_view(),
        name='dismiss-reason-delete',
        kwargs={
            'name': _('Dismiss Reason Delete')
        }
    ),

    path(
        'dismiss-reason/paginate/',
        DismissReasonPaginateView.as_view(),
        name='dismiss-reason-paginate',
        kwargs={
            'name': _('Dismiss Reason Paginate')
        }
    ),

    path(
        'staff/set-dismiss/',
        StaffSetDismissView.as_view(),
        name='staff-set-dismiss',
        kwargs={
            'name': _('Staff Set Dismiss')
        }
    ),

    path(
        'dismiss-staff-log/paginate/',
        DismissStaffLogPaginateView.as_view(),
        name='dismiss-staff-log-paginate',
        kwargs={
            'name': _('Dismiss Staff Log Paginate')
        }
    ),
]
