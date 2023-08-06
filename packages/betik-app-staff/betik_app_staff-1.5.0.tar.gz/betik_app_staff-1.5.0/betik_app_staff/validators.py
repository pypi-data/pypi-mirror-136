import datetime

from django.utils.translation import gettext as _

from betik_app_staff.exceptions import StaffConflictWorkingTimeError
from betik_app_staff.models import IndividualShiftModel, ShiftRuleModel, BusinessDayModel
from betik_app_staff.working_day import find_working_hour_in_date


class StaffBusinessDaysConflictValidator:
    """
        personellerin start_date'den başlayıp finish_date tarihine kadarki tüm mesai günleri kontrol edilecek
    """

    def __init__(self, start_date, finish_date, staffs) -> None:
        self.start_date = start_date
        self.finish_date = finish_date
        self.staffs = staffs
        self.errors = []
        self.general_error = None
        super().__init__()

    def validate(self, raise_exception=False) -> bool:
        ret_val = True
        for staff in self.staffs:
            day_index = 0
            while self.start_date + datetime.timedelta(days=day_index) <= self.finish_date:
                this_day = self.start_date + datetime.timedelta(days=day_index)
                yesterday = this_day - datetime.timedelta(days=1)
                tomorrow = this_day + datetime.timedelta(days=1)

                yesterday_working_hours = find_working_hour_in_date(yesterday, staff)
                today_working_hours = find_working_hour_in_date(this_day, staff)
                tomorrow_working_hours = find_working_hour_in_date(tomorrow, staff)

                # bir gün önceki mesai saati ile, bugünün mesaisinin başlama saati çakışıyor mu?
                for yesterday_working_hour in yesterday_working_hours:
                    for today_working_hour in today_working_hours:
                        yesterday_start_dt = yesterday_working_hour.get('start_dt')
                        yesterday_finish_dt = yesterday_working_hour.get('finish_dt')
                        today_start_dt = today_working_hour.get('start_dt')

                        if yesterday_start_dt <= today_start_dt < yesterday_finish_dt:
                            msg = self._make_error_message(yesterday_working_hour, today_working_hour, staff)
                            self.errors.append(msg)

                # bugünün mesaisinin çıkış saati ile bir sonraki günün mesaisi çakışıyormu
                # bugünün mesaisi, bir gün sonraki mesai saatini kapsıyor mu
                for today_working_hour in today_working_hours:
                    for tomorrow_working_hour in tomorrow_working_hours:
                        today_start_dt = today_working_hour.get('start_dt')
                        today_finish_dt = today_working_hour.get('finish_dt')
                        tomorrow_start_dt = tomorrow_working_hour.get('start_dt')
                        tomorrow_finish_dt = tomorrow_working_hour.get('finish_dt')

                        if tomorrow_start_dt < today_finish_dt <= tomorrow_finish_dt:
                            msg = self._make_error_message(today_working_hour, tomorrow_working_hour, staff)
                            self.errors.append(msg)
                        elif today_start_dt <= tomorrow_start_dt and tomorrow_finish_dt <= today_finish_dt:
                            msg = self._make_error_message(today_working_hour, tomorrow_working_hour, staff)
                            self.errors.append(msg)

                # bugünün mesaileri birbiriyle çakışıyor mu?
                for index1, today_working_hour1 in enumerate(today_working_hours):
                    for today_working_hour2 in today_working_hours[index1 + 1:]:
                        today1_start_dt = today_working_hour1.get('start_dt')
                        today1_finish_dt = today_working_hour1.get('finish_dt')
                        today2_start_dt = today_working_hour2.get('start_dt')
                        today2_finish_dt = today_working_hour2.get('finish_dt')

                        if today_working_hour1 != today_working_hour2:
                            if today2_start_dt < today1_start_dt <= today2_finish_dt:
                                msg = self._make_error_message(today_working_hour1, today_working_hour2, staff)
                                self.errors.append(msg)
                            elif today2_start_dt < today1_finish_dt <= today2_finish_dt:
                                msg = self._make_error_message(today_working_hour1, today_working_hour2, staff)
                                self.errors.append(msg)
                            elif today1_start_dt <= today2_start_dt and today2_finish_dt <= today1_finish_dt:
                                msg = self._make_error_message(today_working_hour1, today_working_hour2, staff)
                                self.errors.append(msg)

                day_index += 1

        if len(self.errors) > 0:
            self.general_error = _('Conflicts detected on %(count)d shift times') % {
                'count': len(self.errors)
            }

            if raise_exception:
                self._raise()

            ret_val = False

        return ret_val

    def _make_error_message(self, conflicting_day1, conflicting_day2, staff):
        msg = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': staff.person.name,
            'last_name': staff.person.last_name,
            'identity': staff.person.identity
        }

        conflicting_days = [conflicting_day1, conflicting_day2]
        for index, cd in enumerate(conflicting_days):
            inst_day = cd.get('_instance')

            if isinstance(inst_day, BusinessDayModel):
                msg += " " + _(
                    'working hours depending on the general business rule name %(name)s(%(date1)s - %(date2)s)') % {
                           'name': inst_day.name,
                           'date1': cd.get('start_dt').strftime("%d %B %Y %H:%M"),
                           'date2': cd.get('finish_dt').strftime("%d %B %Y %H:%M")
                       }
            elif isinstance(inst_day, ShiftRuleModel):
                msg += " " + _('working hours depending on the shift rule name %(name)s(%(date1)s - %(date2)s)') % {
                    'name': inst_day.name,
                    'date1': cd.get('start_dt').strftime("%d %B %Y %H:%M"),
                    'date2': cd.get('finish_dt').strftime("%d %B %Y %H:%M")
                }
            elif isinstance(inst_day, IndividualShiftModel):
                msg += " " + _('working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
                    'id': inst_day.id,
                    'date1': cd.get('start_dt').strftime("%d %B %Y %H:%M"),
                    'date2': cd.get('finish_dt').strftime("%d %B %Y %H:%M")
                }

            if index == 0:
                msg += " " + _("with")

        msg += " " + _('overlap')

        return msg

    def _raise(self):
        raise StaffConflictWorkingTimeError({'detail': self.general_error}, item_errors=self.errors)
