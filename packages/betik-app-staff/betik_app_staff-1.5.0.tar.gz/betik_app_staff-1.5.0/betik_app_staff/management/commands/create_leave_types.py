from django.core.management import BaseCommand
from django.utils.translation import gettext as _

from betik_app_staff.enums import LeaveTypeEnum
from betik_app_staff.models import LeaveTypeModel


class Command(BaseCommand):
    help = 'Crate leave types'

    def handle(self, *args, **options):
        self.database = options.get('database')

        self._create_annual_leave_type()

    def _create_annual_leave_type(self):

        model_manager = LeaveTypeModel._default_manager.db_manager(self.database)

        try:
            model_manager.get(code=LeaveTypeEnum.ANNUAL_LEAVE)
        except LeaveTypeModel.DoesNotExist:
            model_manager.create(
                type=_('Annual Leave'),
                code=LeaveTypeEnum.ANNUAL_LEAVE
            )

            print("created annual leave type")
