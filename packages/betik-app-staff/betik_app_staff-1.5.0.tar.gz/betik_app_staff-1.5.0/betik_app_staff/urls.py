from betik_app_acs.enums import UsingModuleEnum
from betik_app_acs.views import DeviceListView, DeviceStatusChangeView, DeviceCreateView, DeviceUpdateView, \
    DeviceEventListByDeviceView, DevicePermissionListByPersonView, PersonDeviceLogPaginateView
from betik_app_util.messages import MESSAGE_URL_MERGE_DETAIL
from betik_app_util.routes import DateTimeConverter, DateConverter
from django.urls import path, register_converter
from django.utils.translation import gettext_lazy as _

from betik_app_staff.views.annual_leave_rule import AnnualLeaveRuleCreateView, AnnualLeaveRuleUpdateView, \
    AnnualLeaveRuleDeleteView, AnnualLeaveRulePaginateView
from betik_app_staff.views.bank_holiday import BankHolidayCreateView, BankHolidayUpdateView, BankHolidayDeleteView, \
    BankHolidayPaginateView
from betik_app_staff.views.business_day import BusinessDayCreateView, BusinessDayUpdateView, BusinessDayDeleteView, \
    BusinessDayPaginateView
from betik_app_staff.views.custom_shift import CustomShiftPaginateView, CustomShiftDeleteView, CustomShiftCreateBulkView
from betik_app_staff.views.department import DepartmentPaginateView, DepartmentCreateView, DepartmentUpdateView, \
    DepartmentDeleteView, DepartmentMergeView
from betik_app_staff.views.enum import ShiftTypeListView
from betik_app_staff.views.holiday import HolidayCreateView, HolidayUpdateView, HolidayDeleteView, HolidayPaginateView
from betik_app_staff.views.leave_type import LeaveTypePaginateView, LeaveTypeCreateView, LeaveTypeUpdateView, \
    LeaveTypeDeleteView
from betik_app_staff.views.shift_rule import ShiftRuleCreateView, ShiftRuleUpdateView, ShiftRuleDeleteView, \
    ShiftRulePaginateView, BulkStaffAssignToShiftRuleView, StaffRemoveFromShiftView
from betik_app_staff.views.staff import StaffPaginateView, StaffEmailSendView, StaffSmsSendView, StaffCreateView, \
    StaffUpdateView, StaffPaginateByShiftRuleView
from betik_app_staff.views.staff_acs_device import DevicePermissionAssignBulkStaffView
from betik_app_staff.views.staff_active import ActiveReasonCreateView, ActiveReasonUpdateView, ActiveReasonDeleteView, \
    ActiveReasonPaginateView, ActiveReasonMergeView, StaffSetActiveView, ActiveStaffLogPaginateView
from betik_app_staff.views.staff_dismiss import DismissReasonCreateView, DismissReasonUpdateView, \
    DismissReasonDeleteView, DismissReasonPaginateView, DismissReasonMergeView, StaffSetDismissView, \
    DismissStaffLogPaginateView
from betik_app_staff.views.staff_leave import StaffLeaveCreateView, StaffLeaveUpdateView, StaffLeaveDeleteView, \
    StaffLeavePaginateView, AnnualLeaveReportStaffListView
from betik_app_staff.views.staff_passive import PassiveReasonCreateView, PassiveReasonUpdateView, \
    PassiveReasonDeleteView, PassiveReasonPaginateView, PassiveReasonMergeView, StaffSetPassiveView, \
    PassiveStaffLogPaginateView
from betik_app_staff.views.staff_statistic import StatisticStaffGenderPaginateView, StatisticStaffBloodPaginateView, \
    StatisticStaffRegisterProvincePaginateView, StatisticStaffEducationPaginateView, \
    StatisticStaffDepartmentPaginateView, StatisticStaffStaffTypePaginateView, StatisticStaffTitlePaginateView
from betik_app_staff.views.staff_type import StaffTypePaginateView, StaffTypeCreateView, StaffTypeUpdateView, \
    StaffTypeDeleteView, StaffTypeMergeView
from betik_app_staff.views.title import TitlePaginateView, TitleCreateView, TitleUpdateView, TitleDeleteView, \
    TitleMergeView
from betik_app_staff.views.working_hour import AbsenteePaginateOnDateView, LatePaginateOnDateView

app_name = 'betik_app_staff'

register_converter(DateTimeConverter, 'datetime')
register_converter(DateConverter, 'date')

urlpatterns = [
    path(
        'department/paginate/',
        DepartmentPaginateView.as_view(),
        name='department-paginate',
        kwargs={
            'name': _('Paginate departments')
        }
    ),

    path(
        'department/create/',
        DepartmentCreateView.as_view(),
        name='department-create',
        kwargs={
            'name': _('Create a department')
        }
    ),

    path(
        'department/update/<int:pk>/',
        DepartmentUpdateView.as_view(),
        name='department-update',
        kwargs={
            'name': _('Update a department')
        }
    ),

    path(
        'department/delete/<int:pk>/',
        DepartmentDeleteView.as_view(),
        name='department-delete',
        kwargs={
            'name': _('Delete a department')
        }
    ),

    path(
        'department/merge/<int:pk>/',
        DepartmentMergeView.as_view(),
        name='department-merge',
        kwargs={
            'name': _('Merge bulk departments'),
            'detail': MESSAGE_URL_MERGE_DETAIL
        }
    ),

    path(
        'title/paginate/',
        TitlePaginateView.as_view(),
        name='title-paginate',
        kwargs={
            'name': _('Paginate titles')
        }
    ),

    path(
        'title/create/',
        TitleCreateView.as_view(),
        name='title-create',
        kwargs={
            'name': _('Create a title')
        }
    ),

    path(
        'title/update/<int:pk>/',
        TitleUpdateView.as_view(),
        name='title-update',
        kwargs={
            'name': _('Update a title')
        }
    ),

    path(
        'title/delete/<int:pk>/',
        TitleDeleteView.as_view(),
        name='title-delete',
        kwargs={
            'name': _('Delete a title')
        }
    ),

    path(
        'title/merge/<int:pk>/',
        TitleMergeView.as_view(),
        name='title-merge',
        kwargs={
            'name': _('Merge bulk titles'),
            'detail': MESSAGE_URL_MERGE_DETAIL
        }
    ),

    path(
        'staff-type/paginate/',
        StaffTypePaginateView.as_view(),
        name='staff-type-paginate',
        kwargs={
            'name': _('Paginate staff types')
        }
    ),

    path(
        'staff-type/create/',
        StaffTypeCreateView.as_view(),
        name='staff-type-create',
        kwargs={
            'name': _('Create a staff type')
        }
    ),

    path(
        'staff-type/update/<int:pk>/',
        StaffTypeUpdateView.as_view(),
        name='staff-type-update',
        kwargs={
            'name': _('Update a staff type')
        }
    ),

    path(
        'staff-type/delete/<int:pk>/',
        StaffTypeDeleteView.as_view(),
        name='staff-type-delete',
        kwargs={
            'name': _('Delete a staff type')
        }
    ),

    path(
        'staff-type/merge/<int:pk>/',
        StaffTypeMergeView.as_view(),
        name='staff-type-merge',
        kwargs={
            'name': _('Merge staff types'),
            'detail': MESSAGE_URL_MERGE_DETAIL
        }
    ),

    path(
        'staff/paginate/',
        StaffPaginateView.as_view(),
        name='staff-paginate',
        kwargs={
            'name': _('Paginate staffs')
        }
    ),

    path(
        'email/send/bulk-staff/',
        StaffEmailSendView.as_view(),
        name='staff-email-send',
        kwargs={
            'name': _('Send bulk emails to staff')
        }
    ),

    path(
        'sms/send/bulk-staff/',
        StaffSmsSendView.as_view(),
        name='staff-sms-send',
        kwargs={
            'name': _('Send bulk sms to staff')
        }
    ),

    path(
        'staff/create/',
        StaffCreateView.as_view(),
        name='staff-create',
        kwargs={
            'name': _('Create a staff')
        }
    ),

    path(
        'staff/update/<int:pk>/',
        StaffUpdateView.as_view(),
        name='staff-update',
        kwargs={
            'name': _('Update a staff')
        }
    ),

    path(
        'passive-reason/create/',
        PassiveReasonCreateView.as_view(),
        name='passive-reason-create',
        kwargs={
            'name': _('Create a passive reason')
        }
    ),

    path(
        'passive-reason/update/<int:pk>/',
        PassiveReasonUpdateView.as_view(),
        name='passive-reason-update',
        kwargs={
            'name': _('Update a passive reason')
        }
    ),

    path(
        'passive-reason/delete/<int:pk>/',
        PassiveReasonDeleteView.as_view(),
        name='passive-reason-delete',
        kwargs={
            'name': _('Delete a passive reason')
        }
    ),

    path(
        'passive-reason/paginate/',
        PassiveReasonPaginateView.as_view(),
        name='passive-reason-paginate',
        kwargs={
            'name': _('Paginate passive reasons')
        }
    ),

    path(
        'passive-reason/merge/<int:pk>/',
        PassiveReasonMergeView.as_view(),
        name='passive-reason-merge',
        kwargs={
            'name': _('Merge passive reasons'),
            'detail': MESSAGE_URL_MERGE_DETAIL
        }
    ),

    path(
        'staff/set/passive/',
        StaffSetPassiveView.as_view(),
        name='staff-set-passive',
        kwargs={
            'name': _('Make a staff passive')
        }
    ),

    path(
        'passive-staff-log/paginate/',
        PassiveStaffLogPaginateView.as_view(),
        name='passive-staff-log-paginate',
        kwargs={
            'name': _('Paginate passive staff logs')
        }
    ),

    path(
        'dismiss-reason/create/',
        DismissReasonCreateView.as_view(),
        name='dismiss-reason-create',
        kwargs={
            'name': _('Create a dismiss reason')
        }
    ),

    path(
        'dismiss-reason/update/<int:pk>/',
        DismissReasonUpdateView.as_view(),
        name='dismiss-reason-update',
        kwargs={
            'name': _('Update a dismiss reason')
        }
    ),

    path(
        'dismiss-reason/delete/<int:pk>/',
        DismissReasonDeleteView.as_view(),
        name='dismiss-reason-delete',
        kwargs={
            'name': _('Delete a dismiss reason')
        }
    ),

    path(
        'dismiss-reason/paginate/',
        DismissReasonPaginateView.as_view(),
        name='dismiss-reason-paginate',
        kwargs={
            'name': _('Paginate dismiss reasons')
        }
    ),

    path(
        'dismiss-reason/merge/<int:pk>/',
        DismissReasonMergeView.as_view(),
        name='dismiss-reason-merge',
        kwargs={
            'name': _('Merge dismiss reasons'),
            'detail': MESSAGE_URL_MERGE_DETAIL
        }
    ),

    path(
        'staff/set/dismiss/',
        StaffSetDismissView.as_view(),
        name='staff-set-dismiss',
        kwargs={
            'name': _('Dismiss a staff')
        }
    ),

    path(
        'dismiss-staff-log/paginate/',
        DismissStaffLogPaginateView.as_view(),
        name='dismiss-staff-log-paginate',
        kwargs={
            'name': _('Paginate dismiss staff logs')
        }
    ),

    path(
        'active-reason/create/',
        ActiveReasonCreateView.as_view(),
        name='active-reason-create',
        kwargs={
            'name': _('Create a active reason')
        }
    ),

    path(
        'active-reason/update/<int:pk>/',
        ActiveReasonUpdateView.as_view(),
        name='active-reason-update',
        kwargs={
            'name': _('Update a active reason')
        }
    ),

    path(
        'active-reason/delete/<int:pk>/',
        ActiveReasonDeleteView.as_view(),
        name='active-reason-delete',
        kwargs={
            'name': _('Delete a active reason')
        }
    ),

    path(
        'active-reason/paginate/',
        ActiveReasonPaginateView.as_view(),
        name='active-reason-paginate',
        kwargs={
            'name': _('Paginate active reasons')
        }
    ),

    path(
        'active-reason/merge/<int:pk>/',
        ActiveReasonMergeView.as_view(),
        name='active-reason-merge',
        kwargs={
            'name': _('Merge active reasons'),
            'detail': MESSAGE_URL_MERGE_DETAIL
        }
    ),

    path(
        'staff/set/active/',
        StaffSetActiveView.as_view(),
        name='staff-set-active',
        kwargs={
            'name': _('Make a staff active')
        }
    ),

    path(
        'active-staff-log/paginate/',
        ActiveStaffLogPaginateView.as_view(),
        name='active-staff-log-paginate',
        kwargs={
            'name': _('Paginate active staff logs')
        }
    ),

    path(
        'bank-holiday/create/',
        BankHolidayCreateView.as_view(),
        name='bank-holiday-create',
        kwargs={
            'name': _('Create a bank holiday')
        }
    ),

    path(
        'bank-holiday/update/<int:pk>/',
        BankHolidayUpdateView.as_view(),
        name='bank-holiday-update',
        kwargs={
            'name': _('Update a bank holiday')
        }
    ),

    path(
        'bank-holiday/delete/<int:pk>/',
        BankHolidayDeleteView.as_view(),
        name='bank-holiday-delete',
        kwargs={
            'name': _('Delete a bank holiday')
        }
    ),

    path(
        'bank-holiday/paginate/',
        BankHolidayPaginateView.as_view(),
        name='bank-holiday-paginate',
        kwargs={
            'name': _('Paginate bank holidays')
        }
    ),

    path(
        'holiday/create/',
        HolidayCreateView.as_view(),
        name='holiday-create',
        kwargs={
            'name': _('Create a holiday')
        }
    ),

    path(
        'holiday/update/<int:pk>/',
        HolidayUpdateView.as_view(),
        name='holiday-update',
        kwargs={
            'name': _('Update a holiday')
        }
    ),

    path(
        'holiday/delete/<int:pk>/',
        HolidayDeleteView.as_view(),
        name='holiday-delete',
        kwargs={
            'name': _('Delete a holiday')
        }
    ),

    path(
        'holiday/paginate/',
        HolidayPaginateView.as_view(),
        name='holiday-paginate',
        kwargs={
            'name': _('Paginate holidays')
        }
    ),

    path(
        'business-day/create/',
        BusinessDayCreateView.as_view(),
        name='business-day-create',
        kwargs={
            'name': _('Create a business day')
        }
    ),

    path(
        'business-day/update/<int:pk>/',
        BusinessDayUpdateView.as_view(),
        name='business-day-update',
        kwargs={
            'name': _('Update a business day')
        }
    ),

    path(
        'business-day/delete/<int:pk>/',
        BusinessDayDeleteView.as_view(),
        name='business-day-delete',
        kwargs={
            'name': _('Delete a business day')
        }
    ),

    path(
        'business-day/paginate/',
        BusinessDayPaginateView.as_view(),
        name='business-day-paginate',
        kwargs={
            'name': _('Paginate business days')
        }
    ),

    path(
        'annual-leave-rule/create/',
        AnnualLeaveRuleCreateView.as_view(),
        name='annual-leave-rule-create',
        kwargs={
            'name': _('Create a annual leave rule')
        }
    ),

    path(
        'annual-leave-rule/update/<int:pk>/',
        AnnualLeaveRuleUpdateView.as_view(),
        name='annual-leave-rule-update',
        kwargs={
            'name': _('Update a annual leave rule')
        }
    ),

    path(
        'annual-leave-rule/delete/<int:pk>/',
        AnnualLeaveRuleDeleteView.as_view(),
        name='annual-leave-rule-delete',
        kwargs={
            'name': _('Delete a annual leave rule')
        }
    ),

    path(
        'annual-leave-rule/paginate/',
        AnnualLeaveRulePaginateView.as_view(),
        name='annual-leave-rule-paginate',
        kwargs={
            'name': _('Paginate annual leave rules')
        }
    ),

    path(
        'leave-type/paginate/',
        LeaveTypePaginateView.as_view(),
        name='leave-type-paginate',
        kwargs={
            'name': _('Paginate leave types')
        }
    ),

    path(
        'leave-type/create/',
        LeaveTypeCreateView.as_view(),
        name='leave-type-create',
        kwargs={
            'name': _('Create a leave type')
        }
    ),

    path(
        'leave-type/update/<int:pk>/',
        LeaveTypeUpdateView.as_view(),
        name='leave-type-update',
        kwargs={
            'name': _('Update a leave type')
        }
    ),

    path(
        'leave-type/delete/<int:pk>/',
        LeaveTypeDeleteView.as_view(),
        name='leave-type-delete',
        kwargs={
            'name': _('Delete a leave type')
        }
    ),

    path(
        'shift-rule/create/',
        ShiftRuleCreateView.as_view(),
        name='shift-rule-create',
        kwargs={
            'name': _('Create a shift rule')
        }
    ),

    path(
        'shift-rule/update/<int:pk>/',
        ShiftRuleUpdateView.as_view(),
        name='shift-rule-update',
        kwargs={
            'name': _('Update a shift rule')
        }
    ),

    path(
        'shift-rule/delete/<int:pk>/',
        ShiftRuleDeleteView.as_view(),
        name='shift-rule-delete',
        kwargs={
            'name': _('Delete a shift rule')
        }
    ),

    path(
        'shift-rule/paginate/',
        ShiftRulePaginateView.as_view(),
        name='shift-rule-paginate',
        kwargs={
            'name': _('Paginate shift rules')
        }
    ),

    path(
        'shift-rule/assign/bulk-staff/',
        BulkStaffAssignToShiftRuleView.as_view(),
        name='shift-rule-assign-bulk-staff',
        kwargs={
            'name': _('Assign shift rule to bulk staff'),
            'detail': _('Assigns bulk staffs to the selected shift')
        }
    ),

    path(
        'shift-rule/remove/staff/<int:staff_id>/<int:shift_rule_id>/',
        StaffRemoveFromShiftView.as_view(),
        name='shift-rule-remove-staff',
        kwargs={
            'name': _('Remove staff from shift rule')
        }
    ),

    path(
        'staff/paginate/shift_rule/<int:shift_rule_id>/shift_no/<int:shift_no>/',
        StaffPaginateByShiftRuleView.as_view(),
        name='staff-paginate-by-shift',
        kwargs={
            'name': _('Paginate staffs who depends on shift rule')
        }
    ),

    path(
        'custom-shift/create/bulk/',
        CustomShiftCreateBulkView.as_view(),
        name='custom-shift-create-bulk',
        kwargs={
            'name': _('Create bulk custom shift')
        }
    ),

    path(
        'custom-shift/delete/<int:pk>/',
        CustomShiftDeleteView.as_view(),
        name='custom-shift-delete',
        kwargs={
            'name': _('Delete a custom shift')
        }
    ),

    path(
        'custom-shift/paginate/<datetime:start_dt_gte>/<datetime:start_dt_lte>/',
        CustomShiftPaginateView.as_view(),
        name='custom-shift-paginate',
        kwargs={
            'name': _('Paginate custom shifts')
        }
    ),

    path(
        'device/list/',
        DeviceListView.as_view(),
        name='device-list',
        kwargs={
            'name': _('List devices(Staff Module)'),
            'module_code': UsingModuleEnum.STAFF
        }
    ),

    path(
        'device/status/change/<int:pk>/',
        DeviceStatusChangeView.as_view(),
        name='device-status-change',
        kwargs={
            'name': _('Change a device status(Staff Module)'),
            'detail': _('The device can be active or passive'),
            'module_code': UsingModuleEnum.STAFF
        }
    ),

    path(
        'device/create/',
        DeviceCreateView.as_view(),
        name='device-create',
        kwargs={
            'name': _('Create a device(Staff Module)'),
            'module_code': UsingModuleEnum.STAFF

        }
    ),

    path(
        'device/update/<int:pk>/',
        DeviceUpdateView.as_view(),
        name='device-update',
        kwargs={
            'name': _('Update a device(Staff Module)'),
            'module_code': UsingModuleEnum.STAFF
        }
    ),

    path(
        'device-event/list/<int:device_id>/',
        DeviceEventListByDeviceView.as_view(),
        name='device-event-list-by-device',
        kwargs={
            'name': _('List device events(Staff Module)'),
            'module_code': UsingModuleEnum.STAFF
        }
    ),

    path(
        'device-permission/list/<int:person_id>/',
        DevicePermissionListByPersonView.as_view(),
        name='device-permission-list-by-person',
        kwargs={
            'name': _('List person\'s device permissions(Staff Module)'),
            'module_code': UsingModuleEnum.STAFF
        }
    ),

    path(
        'device-permission/assign/bulk-staff/',
        DevicePermissionAssignBulkStaffView.as_view(),
        name='device-permission-assign-bulk-staff',
        kwargs={
            'name': _('Assign device permission to bulk staff(Staff Module)'),
            'module_code': UsingModuleEnum.STAFF
        }
    ),

    path(
        'device-log/paginate/<datetime:datetime_gte>/<datetime:datetime_lte>',
        PersonDeviceLogPaginateView.as_view(),
        name='device-log-paginate',
        kwargs={
            'name': _('Paginate person\'s attendance logs(Staff Module)'),
            'module_code': UsingModuleEnum.STAFF
        }
    ),

    path(
        'staff-leave/create',
        StaffLeaveCreateView.as_view(),
        name='staff-leave-create',
        kwargs={
            'name': _('Create a staff leave')
        }
    ),

    path(
        'staff-leave/update/<int:pk>/',
        StaffLeaveUpdateView.as_view(),
        name='staff-leave-update',
        kwargs={
            'name': _('Update a staff leave')
        }
    ),

    path(
        'staff-leave/delete/<int:pk>/',
        StaffLeaveDeleteView.as_view(),
        name='staff-leave-delete',
        kwargs={
            'name': _('Delete a staff leave')
        }
    ),

    path(
        'staff-leave/paginate/<datetime:start_dt_gte>/<datetime:start_dt_lte>/',
        StaffLeavePaginateView.as_view(),
        name='staff-leave-paginate',
        kwargs={
            'name': _('Paginate staff leaves')
        }
    ),

    path(
        'absentee-staff/date/<date:date>/paginate/',
        AbsenteePaginateOnDateView.as_view(),
        name='absentee-staff-paginate-on-date',
        kwargs={
            'name': _('Paginate absentee staff on date')
        }
    ),

    path(
        'late-staff/date/<date:date>/paginate/',
        LatePaginateOnDateView.as_view(),
        name='late-staff-paginate-on-date',
        kwargs={
            'name': _('Paginate late staff on date')
        }
    ),

    path(
        'annual-leave-report/staff/<int:staff_id>/list/',
        AnnualLeaveReportStaffListView.as_view(),
        name='annual-leave-report-staff-list',
        kwargs={
            'name': _('List annual leave report that belongs to staff')
        }
    ),

    path(
        'statistic/staff-gender/paginate/',
        StatisticStaffGenderPaginateView.as_view(),
        name='statistic-staff-gender-paginate',
        kwargs={
            'name': _('Staff-Gender statistic paginate')
        }
    ),

    path(
        'statistic/staff-blood/paginate/',
        StatisticStaffBloodPaginateView.as_view(),
        name='statistic-staff-blood-paginate',
        kwargs={
            'name': _('Staff-Blood statistic paginate')
        }
    ),

    path(
        'statistic/staff-education/paginate/',
        StatisticStaffEducationPaginateView.as_view(),
        name='statistic-staff-education-paginate',
        kwargs={
            'name': _('Staff-Education statistic paginate')
        }
    ),

    path(
        'statistic/staff-register-province/paginate/',
        StatisticStaffRegisterProvincePaginateView.as_view(),
        name='statistic-staff-register-province-paginate',
        kwargs={
            'name': _('Staff-Register Province statistic paginate')
        }
    ),

    path(
        'statistic/staff-department/paginate/',
        StatisticStaffDepartmentPaginateView.as_view(),
        name='statistic-staff-department-paginate',
        kwargs={
            'name': _('Staff-Department statistic paginate')
        }
    ),

    path(
        'statistic/staff-staff-type/paginate/',
        StatisticStaffStaffTypePaginateView.as_view(),
        name='statistic-staff-staff-type-paginate',
        kwargs={
            'name': _('Staff-Staff Type statistic paginate')
        }
    ),

    path(
        'statistic/staff-title/paginate/',
        StatisticStaffTitlePaginateView.as_view(),
        name='statistic-staff-title-paginate',
        kwargs={
            'name': _('Staff-Title statistic paginate')
        }
    ),

    path(
        'shift-type/list/',
        ShiftTypeListView.as_view(),
        name='shift-type-list',
        kwargs={
            'name': _('Shift type list'),
            'is_public': True
        }
    ),
]
