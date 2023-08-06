from betik_app_email.models import GetEmailAddressMixIn
from betik_app_sms.models import GetMobilePhoneMixIn
from django.db import models
from django.utils.translation import gettext_lazy as _

from betik_app_staff.enums import StaffStatusEnum


class DepartmentModel(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Department'))

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')

    def __str__(self):
        return self.name


class TitleModel(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Title')
        verbose_name_plural = _('Titles')

    def __str__(self):
        return self.name


class StaffTypeModel(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Staff Type')
        verbose_name_plural = _('Staff Types')

    def __str__(self):
        return self.name


class StaffModel(models.Model, GetEmailAddressMixIn, GetMobilePhoneMixIn):
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

    class Meta:
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


class PassiveReasonModel(models.Model):
    explain = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = _('Passive Reason')
        verbose_name_plural = _('Passive Reasons')


class PassiveStaffLogModel(models.Model):
    staff = models.ForeignKey('betik_app_staff.StaffModel', on_delete=models.CASCADE, related_name='passive_events')
    reason = models.ForeignKey('betik_app_staff.PassiveReasonModel', on_delete=models.PROTECT,
                               related_name='passive_events')
    date = models.DateField()
    detail = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Passive Staff Event')
        verbose_name_plural = _('Passive Staff Events')


class DismissReasonModel(models.Model):
    explain = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = _('Dismiss Reason')
        verbose_name_plural = _('Dismiss Reasons')


class DismissStaffLogModel(models.Model):
    staff = models.ForeignKey('betik_app_staff.StaffModel', on_delete=models.CASCADE, related_name='dismiss_logs')
    reason = models.ForeignKey('betik_app_staff.DismissReasonModel', on_delete=models.PROTECT,
                               related_name='dismiss_logs')
    date = models.DateField()
    detail = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Dismiss Staff Log')
        verbose_name_plural = _('Dismiss Staff Logs')
