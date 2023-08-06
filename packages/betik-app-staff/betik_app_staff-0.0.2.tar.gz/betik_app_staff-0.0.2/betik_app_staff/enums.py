from django.utils.translation import gettext as _


class StaffStatusEnum:
    ACTIVE = 1
    PASSIVE = 2
    DISMISS = 3

    types = (
        (ACTIVE, _("Active")),
        (PASSIVE, _("Passive")),
        (DISMISS, _("Dismiss")),
    )
