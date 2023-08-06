from django.utils.translation import gettext_lazy as _


class StaffStatusEnum:
    ACTIVE = 1
    PASSIVE = 2
    DISMISS = 3

    types = (
        (ACTIVE, _("Active")),
        (PASSIVE, _("Passive")),
        (DISMISS, _("Dismiss")),
    )


class AnnualLeaveDurationEnum:
    DAY = 1
    BUSINESS_DAY = 2

    types = (
        (DAY, _("Day")),
        (BUSINESS_DAY, _("Business Day")),
    )


class LeaveDurationTypeEnum(AnnualLeaveDurationEnum):
    HOUR = 3
    WEEK = 4
    MONTH = 5
    YEAR = 6

    types = (
                (HOUR, _("Hour")),
                (WEEK, _("Week")),
            ) + AnnualLeaveDurationEnum.types + (
                (MONTH, _("Month")),
                (YEAR, _("Year")),
            )


class ShiftTypeEnum:
    OVERTIME = 1
    WEEKEND = 2
    HOLIDAY = 3
    NORMAL = 4

    types = (
        (OVERTIME, _("Overtime Shift")),
        (WEEKEND, _("Weekend Shift")),
        (HOLIDAY, _("Holiday Shift")),
        (NORMAL, _("Normal Shift")),
    )


class LeaveTypeEnum:
    ANNUAL_LEAVE = 1

    types = (
        (ANNUAL_LEAVE, _("Annual Leave"))
    )
