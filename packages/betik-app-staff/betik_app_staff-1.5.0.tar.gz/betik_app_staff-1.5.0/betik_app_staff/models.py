import datetime

import architect
from betik_app_acs.mixins import UsableAttendanceDeviceMixIn
from betik_app_email.models import GetEmailAddressMixIn
from betik_app_person.models import NaturalPersonModel
from betik_app_sms.models import GetMobilePhoneMixIn
from betik_app_util.models import TimestampAbstractModel
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext as _

from betik_app_staff.enums import StaffStatusEnum, AnnualLeaveDurationEnum, LeaveDurationTypeEnum, ShiftTypeEnum
from betik_app_staff.managers import BankHolidayManager, HolidayManager, ShiftRuleManager, BusinessDayManager, \
    IndividualShiftManager, AnnualLeaveRuleManager, StaffLeaveManager


class DepartmentModel(TimestampAbstractModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Department'))

    class Meta:
        app_label = 'betik_app_staff'
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')

    def __str__(self):
        return self.name


class TitleModel(TimestampAbstractModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))

    class Meta:
        app_label = 'betik_app_staff'
        verbose_name = _('Title')
        verbose_name_plural = _('Titles')

    def __str__(self):
        return self.name


class StaffTypeModel(TimestampAbstractModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))

    class Meta:
        app_label = 'betik_app_staff'
        verbose_name = _('Staff Type')
        verbose_name_plural = _('Staff Types')

    def __str__(self):
        return self.name


class StaffModel(TimestampAbstractModel, GetEmailAddressMixIn, GetMobilePhoneMixIn, UsableAttendanceDeviceMixIn):
    person = models.ForeignKey('betik_app_person.NaturalPersonModel', on_delete=models.CASCADE, related_name='staffs',
                               verbose_name=_('Person'))
    registration_number = models.CharField(max_length=50, unique=True, verbose_name=_('Registration Number'))
    department = models.ForeignKey(DepartmentModel, on_delete=models.DO_NOTHING, related_name='staffs',
                                   verbose_name=_('Department'))
    staff_type = models.ForeignKey(StaffTypeModel, on_delete=models.DO_NOTHING, related_name='staffs',
                                   verbose_name=_('Staff Type'))
    title = models.ForeignKey(TitleModel, on_delete=models.DO_NOTHING, related_name='staffs', null=True, blank=True,
                              verbose_name=_('Title'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    finish_date = models.DateField(null=True, blank=True, verbose_name=_('Finish Date'))
    status = models.IntegerField(choices=StaffStatusEnum.types, default=StaffStatusEnum.ACTIVE,
                                 verbose_name=_('Status'))

    file_employment_agreement = models.OneToOneField('betik_app_document.DocumentModel', on_delete=models.CASCADE,
                                                     null=True,
                                                     blank=True, verbose_name=_('Employment Agreement'),
                                                     related_name='staff_employment_agreement')
    file_statement_of_insured_employment = models.OneToOneField('betik_app_document.DocumentModel',
                                                                on_delete=models.CASCADE,
                                                                null=True, blank=True,
                                                                verbose_name=_('Statement of Insured Employment'),
                                                                related_name='staff_statement_of_insured_employment')

    files = models.ManyToManyField('betik_app_document.DocumentModel', related_name='staff_files')

    @property
    def active(self):
        return self.finish_date is None

    class Meta:
        app_label = 'betik_app_staff'
        indexes = [
            models.Index(fields=['person', 'registration_number', 'start_date']),
            models.Index(fields=['registration_number', 'start_date']),
            models.Index(fields=['start_date'])
        ]
        verbose_name = _('Staff')
        verbose_name_plural = _('Staffs')

    def get_email_addresses(self):
        return self.person.get_email_addresses()

    def get_mobile_phones(self):
        return self.person.get_mobile_phones()

    def get_person(self) -> NaturalPersonModel:
        return self.person


class PassiveReasonModel(TimestampAbstractModel):
    explain = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = 'betik_app_staff'
        verbose_name = _('Passive Reason')
        verbose_name_plural = _('Passive Reasons')


class PassiveStaffLogModel(TimestampAbstractModel):
    staff = models.ForeignKey('betik_app_staff.StaffModel', on_delete=models.CASCADE, related_name='passive_events')
    reason = models.ForeignKey('betik_app_staff.PassiveReasonModel', on_delete=models.PROTECT,
                               related_name='passive_events')
    date = models.DateField()
    detail = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'betik_app_staff'
        verbose_name = _('Passive Staff Event')
        verbose_name_plural = _('Passive Staff Events')


class DismissReasonModel(TimestampAbstractModel):
    explain = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = 'betik_app_staff'
        verbose_name = _('Dismiss Reason')
        verbose_name_plural = _('Dismiss Reasons')


class DismissStaffLogModel(TimestampAbstractModel):
    staff = models.ForeignKey('betik_app_staff.StaffModel', on_delete=models.CASCADE, related_name='dismiss_logs')
    reason = models.ForeignKey('betik_app_staff.DismissReasonModel', on_delete=models.PROTECT,
                               related_name='dismiss_logs')
    date = models.DateField()
    detail = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'betik_app_staff'
        verbose_name = _('Dismiss Staff Log')
        verbose_name_plural = _('Dismiss Staff Logs')


class ActiveReasonModel(TimestampAbstractModel):
    explain = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = 'betik_app_staff'
        verbose_name = _('Active Reason')
        verbose_name_plural = _('Active Reasons')


class ActiveStaffLogModel(TimestampAbstractModel):
    staff = models.ForeignKey('betik_app_staff.StaffModel', on_delete=models.CASCADE, related_name='active_logs')
    reason = models.ForeignKey('betik_app_staff.ActiveReasonModel', on_delete=models.PROTECT,
                               related_name='dismiss_logs')
    date = models.DateField()
    detail = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'betik_app_staff'
        verbose_name = _('Active Staff Log')
        verbose_name_plural = _('Active Staff Logs')


class BankHolidayModel(TimestampAbstractModel):
    start_date = models.DateField(help_text=_('the start date the bank holiday becomes official'))
    finish_date = models.DateField(null=True, blank=True, help_text=_('the date of the abolition of the bank holiday'))
    day = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    name = models.CharField(max_length=200)

    objects = BankHolidayManager()

    class Meta:
        app_label = 'betik_app_staff'


class HolidayModel(TimestampAbstractModel):
    start_date = models.DateField(help_text=_('the first day of holiday'))
    finish_date = models.DateField(help_text=_('one day after the last day of holiday'))
    name = models.CharField(max_length=200)

    objects = HolidayManager()

    class Meta:
        app_label = 'betik_app_staff'
        indexes = [
            models.Index(fields=['start_date', 'finish_date'])
        ]


class BusinessDayModel(TimestampAbstractModel):
    name = models.CharField(max_length=200, unique=True, null=True, blank=True)
    start_date = models.DateField()
    finish_date = models.DateField(null=True, blank=True)
    staff_type = models.ForeignKey('betik_app_staff.StaffTypeModel', on_delete=models.PROTECT,
                                   related_name='business_days')
    monday = models.JSONField(null=True, blank=True)
    tuesday = models.JSONField(null=True, blank=True)
    wednesday = models.JSONField(null=True, blank=True)
    thursday = models.JSONField(null=True, blank=True)
    friday = models.JSONField(null=True, blank=True)
    saturday = models.JSONField(null=True, blank=True)
    sunday = models.JSONField(null=True, blank=True)

    objects = BusinessDayManager()

    class Meta:
        app_label = 'betik_app_staff'
        indexes = [
            models.Index(fields=['start_date', 'finish_date', 'staff_type'])
        ]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.name:
            self.name = None

        return super().save(force_insert, force_update, using, update_fields)

    @property
    def active(self):
        today = datetime.datetime.today().date()
        return today >= self.start_date and (not self.finish_date or today < self.finish_date)

    def get_formatted_date_range(self) -> str:
        if self.finish_date:
            date_range = self.start_date.strftime("%d %B %Y")
            date_range += " - "
            date_range += self.finish_date.strftime("%d %B %Y")
        else:
            date_range = self.start_date.strftime("%d %B %Y")
            date_range += " "
            date_range += _('And Later')

        return date_range

    def get_business_day_on_date(self, date):
        """
            o tarihdeki güne denk gelen çalışma saatleri bulur
        """

        day_index = date.weekday()
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_name = day_names[day_index]
        business_day = getattr(self, day_name)

        if business_day:
            start_time = business_day.get('start_time')
            work_hour = business_day.get('work_hour')

            start_dt = datetime.datetime.combine(date, datetime.time.fromisoformat(start_time))
            finish_dt = start_dt + datetime.timedelta(hours=work_hour)

            return {
                'start_dt': start_dt,
                'finish_dt': finish_dt,
                'work_hour': work_hour,
                '_instance': self
            }
        return None

    def is_working_time(self, date_time):
        """
            verilen tarih ve saatte mesai var mı?
        """
        working_day = self.get_business_day_on_date(date_time)
        if working_day:
            if working_day['start_dt'] <= date_time < working_day['finish_dt']:
                return True

        return False

    def is_conflict(self, business_day) -> bool:
        if self.id == business_day.id:
            return False

        if self.finish_date:
            if business_day.finish_date:
                if self.start_date <= business_day.start_date < self.finish_date:
                    return True
                elif self.start_date < business_day.finish_date <= self.finish_date:
                    return True
                elif business_day.start_date <= self.start_date and self.finish_date <= business_day.finish_date:
                    return True
            else:
                if business_day.start_date < self.finish_date:
                    return True
        else:
            if business_day.finish_date:
                if self.start_date < business_day.finish_date:
                    return True
            else:
                return True
        return False


class AnnualLeaveRuleModel(TimestampAbstractModel):
    start_date = models.DateField()
    finish_date = models.DateField(null=True, blank=True)
    staff_type = models.ForeignKey('betik_app_staff.StaffTypeModel', on_delete=models.PROTECT,
                                   related_name='annual_leave_rules')
    periods = models.JSONField()
    duration_type = models.PositiveIntegerField(choices=AnnualLeaveDurationEnum.types)
    forward_next_year = models.BooleanField()
    forward_year = models.PositiveIntegerField(null=True, blank=True)

    objects = AnnualLeaveRuleManager()

    class Meta:
        app_label = 'betik_app_staff'
        indexes = [
            models.Index(fields=['start_date', 'finish_date', 'staff_type'])
        ]

    @property
    def active(self):
        today = datetime.datetime.today().date()
        return today >= self.start_date and (not self.finish_date or today < self.finish_date)

    def get_formatted_date_range(self) -> str:
        if self.finish_date:
            date_range = self.start_date.strftime("%d %B %Y")
            date_range += " - "
            date_range += self.finish_date.strftime("%d %B %Y")
        else:
            date_range = self.start_date.strftime("%d %B %Y")
            date_range += " "
            date_range += _('And Later')

        return date_range

    def get_duration_for_working_year(self, working_year):
        for period in self.periods:
            year1 = period['start_year']
            year2 = period.get('finish_year')

            if year2 is None:
                if year1 <= working_year:
                    return period['duration']
            elif year1 <= working_year < year2:
                return period['duration']

        return 0

    def is_conflict(self, annual_leave) -> bool:
        if self.id == annual_leave.id:
            return False

        if self.finish_date:
            if annual_leave.finish_date:
                if self.start_date <= annual_leave.start_date < self.finish_date:
                    return True
                elif self.start_date < annual_leave.finish_date <= self.finish_date:
                    return True
                elif annual_leave.start_date <= self.start_date and self.finish_date <= annual_leave.finish_date:
                    return True
            else:
                if annual_leave.start_date < self.finish_date:
                    return True
        else:
            if annual_leave.finish_date:
                if self.start_date < annual_leave.finish_date:
                    return True
            else:
                return True
        return False


class LeaveTypeModel(TimestampAbstractModel):
    type = models.CharField(max_length=100, unique=True)
    code = models.PositiveIntegerField(unique=True, null=True, blank=True)

    class Meta:
        app_label = 'betik_app_staff'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.code:
            self.code = None

        return super().save(force_insert, force_update, using, update_fields)


@architect.install('partition', type='range', subtype='date', constraint='month', column='start_dt')
class StaffLeaveModel(TimestampAbstractModel):
    start_dt = models.DateTimeField()
    finish_dt = models.DateTimeField()
    work_start_dt = models.DateTimeField()
    staff = models.ForeignKey('betik_app_staff.StaffModel', on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.ForeignKey('betik_app_staff.LeaveTypeModel', on_delete=models.PROTECT)
    duration = models.PositiveIntegerField()
    duration_type = models.PositiveIntegerField(choices=LeaveDurationTypeEnum.types)

    objects = StaffLeaveManager()

    @property
    def active(self):
        now = datetime.datetime.now()
        return self.start_dt <= now < self.finish_dt

    @property
    def expired(self):
        now = datetime.datetime.now()
        return self.finish_dt < now

    class Meta:
        app_label = 'betik_app_staff'
        indexes = [
            models.Index(fields=['start_dt', 'staff', 'leave_type']),
            models.Index(fields=['start_dt', 'finish_dt', 'staff', 'leave_type'])
        ]


class ShiftRuleModel(TimestampAbstractModel):
    name = models.CharField(max_length=200, unique=True)
    start_date = models.DateField()
    finish_date = models.DateField(null=True, blank=True)
    business_days = models.JSONField()
    period_start_date = models.DateField()
    period_end_date = models.DateField()
    period_duration = models.PositiveIntegerField()

    objects = ShiftRuleManager()

    class Meta:
        app_label = 'betik_app_staff'
        indexes = [
            models.Index(fields=['start_date', 'finish_date'])
        ]

    @property
    def active(self):
        today = datetime.datetime.today().date()
        return today >= self.start_date and (not self.finish_date or today < self.finish_date)

    @property
    def expiry(self):
        today = datetime.datetime.today().date()
        return self.finish_date and self.finish_date <= today

    def is_conflict(self, shift_rule):
        if self.finish_date:
            if shift_rule.finish_date:
                if self.start_date <= shift_rule.start_date < self.finish_date:
                    return True
                elif self.start_date < shift_rule.finish_date <= self.finish_date:
                    return True
                elif shift_rule.start_date <= self.start_date and self.finish_date <= shift_rule.finish_date:
                    return True
            else:
                if shift_rule.start_date < self.finish_date:
                    return True
        else:
            if shift_rule.finish_date:
                if self.start_date < shift_rule.finish_date:
                    return True
            else:
                return True
        return False

    def get_business_day_on_date(self, date, staff):
        """
            personelin, o tarihdeki güne denk gelen çalışma saatlerini bulur
        """
        if isinstance(date, datetime.datetime):
            date = date.date()

        # vardiya kuralında toplam kaç vardiya numarası var
        total_period_count = len(self.business_days)

        # vardiya kuralının başlangıç tarihinden itibaren, verilen tarihe kadar kaç gün var
        diff_days = (date - self.period_start_date).days

        # verilen tarihde hangi vardiya numarasında oluncal

        # kaç kere değişim yapılacağını bul
        exchange_period_count = int(diff_days / (self.period_duration * 7))

        # personel ilk hangi vardiya numarasında
        inst_shift_rule_staff = self.shift_staffs.filter(staff=staff).get()
        shift_no = inst_shift_rule_staff.shift_no

        shift_no += exchange_period_count % total_period_count
        if shift_no > total_period_count:
            shift_no -= total_period_count

        period = self.business_days[shift_no - 1]
        day_index = date.weekday()
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_name = day_names[day_index]
        business_day = period.get(day_name, None)

        if business_day:
            start_time = business_day.get('start_time')
            work_hour = business_day.get('work_hour')

            start_dt = datetime.datetime.combine(date, datetime.time.fromisoformat(start_time))
            finish_dt = start_dt + datetime.timedelta(hours=work_hour)

            return {
                'start_dt': start_dt,
                'finish_dt': finish_dt,
                'work_hour': work_hour,
                '_instance': self
            }

        return None

    def is_working_time(self, date_time, staff):
        """
            verilen tarih ve saatte mesai var mı?
        """
        working_day = self.get_business_day_on_date(date_time, staff)
        if working_day:
            if working_day['start_dt'] <= date_time < working_day['finish_dt']:
                return True

        return False


class ShiftRuleStaffModel(TimestampAbstractModel):
    shift_rule = models.ForeignKey('betik_app_staff.ShiftRuleModel', on_delete=models.CASCADE,
                                   related_name='shift_staffs')
    staff = models.ForeignKey('betik_app_staff.StaffModel', on_delete=models.CASCADE, related_name='shift_staffs')
    shift_no = models.PositiveIntegerField()

    class Meta:
        app_label = 'betik_app_staff'
        constraints = [
            models.UniqueConstraint(fields=['shift_rule', 'staff'], name='staff_in_shift_rule')
        ]
        indexes = [
            models.Index(fields=['shift_rule', 'staff', 'shift_no'])
        ]


@architect.install('partition', type='range', subtype='date', constraint='month', column='start_dt')
class IndividualShiftModel(TimestampAbstractModel):
    start_dt = models.DateTimeField()
    finish_dt = models.DateTimeField()
    work_hour = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=1)])
    type = models.PositiveIntegerField(choices=ShiftTypeEnum.types)
    staff = models.ForeignKey('betik_app_staff.StaffModel', on_delete=models.CASCADE, related_name='individual_shifts')

    objects = IndividualShiftManager()

    class Meta:
        app_label = 'betik_app_staff'
        indexes = [
            models.Index(fields=['start_dt', 'finish_dt', 'staff']),
            models.Index(fields=['start_dt', 'staff'])
        ]


@architect.install('partition', type='range', subtype='date', constraint='month', column='start_dt')
class WorkingHourModel(TimestampAbstractModel):
    start_dt = models.DateTimeField()
    finish_dt = models.DateTimeField()
    work_hour = models.PositiveIntegerField()
    type = models.PositiveIntegerField(choices=ShiftTypeEnum.types)
    staff = models.ForeignKey('betik_app_staff.StaffModel', on_delete=models.CASCADE, related_name='working_hours')
    in_dt = models.DateTimeField(null=True, blank=True)
    out_dt = models.DateTimeField(null=True, blank=True)
    late_minute = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        app_label = 'betik_app_staff'
        indexes = [
            models.Index(fields=['start_dt', 'finish_dt', 'staff']),
            models.Index(fields=['start_dt', 'staff']),
            models.Index(fields=['start_dt', 'late_minute'])
        ]
