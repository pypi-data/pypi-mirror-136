from rest_framework.exceptions import ValidationError


class StaffConflictWorkingTimeError(ValidationError):
    default_code = 'betik_app_staff.staff_conflict_working_time_error'

    def __init__(self, detail=None, item_errors=None):
        super().__init__(detail, self.default_code)
        self.item_errors = item_errors
