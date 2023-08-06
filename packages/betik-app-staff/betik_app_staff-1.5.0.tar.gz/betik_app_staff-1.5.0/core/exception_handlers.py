from betik_app_staff.exceptions import StaffConflictWorkingTimeError
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, StaffConflictWorkingTimeError):
        response.data['staff_errors'] = exc.item_errors

    return response
