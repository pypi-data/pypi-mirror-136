import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import gettext as _

from betik_app_staff.models import BankHolidayModel


class Command(BaseCommand):
    help = 'Crate bank holidays'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

        self.database = None
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.country_code = getattr(settings, 'COUNTRY_CODE', None)
        if self.country_code:
            self.country_code = self.country_code.lower()

    def handle(self, *args, **options):
        self.database = options.get('database')

        self._create_bank_holidays()

    def _create_bank_holidays(self):

        bh_manager = BankHolidayModel._default_manager.db_manager(self.database)

        if self.country_code:
            json_file = str(self.base_dir) + "/resource/" + self.country_code + "/bank_holiday.json"

            if os.path.exists(json_file):
                json_data = open(json_file, encoding='utf8')
                json_content = json.load(json_data)

                for bh in json_content:
                    name = bh["name"]
                    start_date = bh["start_date"]
                    day = bh["day"]
                    month = bh["month"]

                    defaults = {
                        'name': name,
                        'start_date': start_date
                    }

                    bh_manager.update_or_create(defaults=defaults, day=day, month=month)

                print("updated bank holidays")

            else:
                raise FileNotFoundError(_('%s file not found') % json_file)
