import datetime

from betik_app_location.models import ProvinceModel, DistrictModel
from betik_app_person.enums import GenderTypeEnum, BloodTypeEnum, EducationTypeEnum
from betik_app_person.faker_providers import IdentityProvider
from betik_app_person.models import NaturalPersonModel
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from faker import Faker
from faker.providers import lorem, person, date_time
from rest_framework.test import APIClient

from betik_app_staff.enums import AnnualLeaveDurationEnum, LeaveDurationTypeEnum, ShiftTypeEnum
from betik_app_staff.models import ShiftRuleModel, StaffModel, TitleModel, DepartmentModel, StaffTypeModel, \
    BankHolidayModel, HolidayModel, AnnualLeaveRuleModel, BusinessDayModel, IndividualShiftModel, LeaveTypeModel, \
    StaffLeaveModel


class TestBase(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.faker = Faker()
        self.faker.add_provider(lorem)

        self._login()

    def _login(self):
        user = get_user_model().objects.create(email="test@test.com", is_staff=True)
        user.set_password("123")
        user.save()

        self.client.force_authenticate(user)
        return user

    def _create_person(self):

        register_province = ProvinceModel.objects.create(name=self.faker.bothify(text='Province-????'))
        register_district = DistrictModel.objects.create(name=self.faker.bothify(text='District-????'),
                                                         province=register_province)

        self.faker.add_provider(person)
        self.faker.add_provider(IdentityProvider)
        gender_code = self.faker.random_element(elements=GenderTypeEnum.types)
        blood_code = self.faker.random_element(elements=BloodTypeEnum.types)
        education_status_code = self.faker.random_element(elements=EducationTypeEnum.types)

        return NaturalPersonModel.objects.create(
            identity=self.faker.identity(),
            name=self.faker.first_name(),
            last_name=self.faker.last_name(),
            gender=gender_code[0],
            blood=blood_code[0],
            education_status=education_status_code[0],
            register_district=register_district
        )

    def _create_staff_type(self):
        staff_type = self.faker.bothify(text='Staff-????-###')
        return StaffTypeModel.objects.create(name=staff_type)

    def _create_department(self):
        dep_name = self.faker.bothify(text='Dep-????-###')
        return DepartmentModel.objects.create(name=dep_name)

    def _create_title(self):
        title = self.faker.bothify(text='Title-????-###')
        return TitleModel.objects.create(name=title)

    def _create_staff(self):
        person_model = self._create_person()
        department_model = self._create_department()
        staff_type_model = self._create_staff_type()
        title_model = self._create_title()

        staff_model = StaffModel.objects.create(
            person=person_model,
            registration_number=StaffModel.objects.count() + 1,
            department=department_model,
            staff_type=staff_type_model,
            start_date=datetime.datetime.now(),
            title=title_model
        )

        return staff_model

    def _create_shift_rule(self):
        # start_date pazartesi günü olmalı
        future_date = self.faker.future_date()
        future_date += datetime.timedelta(days=10)
        day_diff = future_date.weekday() - 0

        start_date = future_date - datetime.timedelta(days=day_diff)

        name = self.faker.bothify(text='Shift Rule-????-###')

        return ShiftRuleModel.objects.create(
            name=name,
            start_date=start_date,
            period_duration=2,
            period_start_date=start_date,
            period_end_date=start_date + datetime.timedelta(weeks=2),
            business_days=[
                {
                    'shift_no': 1,
                    'monday': {'start_time': '11:00', 'work_hour': 8},
                    'sunday': {'start_time': '11:00', 'work_hour': 8}
                },
                {
                    'shift_no': 2,
                    'monday': {'start_time': '19:00', 'work_hour': 8},
                    'sunday': {'start_time': '19:00', 'work_hour': 12}
                },
                {
                    'shift_no': 3,
                    'monday': {'start_time': '23:00', 'work_hour': 8},
                    'tuesday': {'start_time': '23:00', 'work_hour': 8},
                    'wednesday': {'start_time': '23:00', 'work_hour': 8},
                    'thursday': {'start_time': '23:00', 'work_hour': 8},
                    'friday': {'start_time': '23:00', 'work_hour': 8},
                    'saturday': {'start_time': '23:00', 'work_hour': 8}
                },
                {
                    'shift_no': 4,
                    'monday': {'start_time': '09:00', 'work_hour': 8},
                    'tuesday': {'start_time': '09:00', 'work_hour': 8},
                    'wednesday': {'start_time': '09:00', 'work_hour': 8},
                    'thursday': {'start_time': '09:00', 'work_hour': 8},
                    'friday': {'start_time': '09:00', 'work_hour': 8},
                    'saturday': {'start_time': '09:00', 'work_hour': 8}
                }
            ]
        )

    def _create_bank_holiday(self, name=None):
        self.faker.add_provider(person)
        self.faker.add_provider(date_time)

        name = name if name else self.faker.first_name()
        month_day = self.faker.date_between()
        instance = BankHolidayModel.objects.create(
            name=name,
            month=month_day.month,
            day=month_day.day,
            start_date=self.faker.date_between()
        )

        return instance

    def _create_holiday(self, name=None):
        self.faker.add_provider(person)
        self.faker.add_provider(date_time)

        name = name if name else self.faker.first_name()
        start_date = self.faker.future_date()
        finish_date = start_date + datetime.timedelta(days=1)
        instance = HolidayModel.objects.create(
            name=name,
            start_date=start_date,
            finish_date=finish_date
        )

        return instance

    def _create_annual_leave_rule(self, with_finish_date=True):
        self.faker.add_provider(date_time)

        start_date = self.faker.future_date() + datetime.timedelta(days=10)

        finish_date = None
        if with_finish_date:
            finish_date = start_date + datetime.timedelta(days=10)

        staff_type = self._create_staff_type()

        instance = AnnualLeaveRuleModel.objects.create(
            start_date=start_date,
            finish_date=finish_date,
            staff_type=staff_type,
            periods=[
                {'start_year': 4, 'finish_year': 6, 'duration': 1},
                {'start_year': 6, 'duration': 1}
            ],
            duration_type=AnnualLeaveDurationEnum.DAY,
            forward_next_year=True,
            forward_year=1
        )

        return instance

    def _create_business_day(self, with_finish_date=True):
        self.faker.add_provider(person)
        self.faker.add_provider(date_time)

        name = self.faker.bothify(text='Business Day-????-###')
        start_date = self.faker.future_date()
        start_date += datetime.timedelta(days=10)

        finish_date = None
        if with_finish_date:
            finish_date = start_date + datetime.timedelta(days=10)

        staff_type = self._create_staff_type()
        monday = {'start_time': '09:00', 'work_hour': 8}
        tuesday = {'start_time': '09:00', 'work_hour': 8}

        instance = BusinessDayModel.objects.create(
            name=name,
            start_date=start_date,
            finish_date=finish_date,
            staff_type=staff_type,
            monday=monday,
            tuesday=tuesday
        )

        return instance

    def _create_individual_shift(self):
        shift_type = ShiftTypeEnum.OVERTIME
        staff = self._create_staff()
        work_hour = 8
        start_dt = self.faker.future_date()
        while start_dt.weekday() == 6:
            start_dt += datetime.timedelta(days=1)
        start_dt = datetime.datetime.combine(start_dt, datetime.time(hour=8, minute=0, second=0, microsecond=0))
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        return IndividualShiftModel.objects.create(
            start_dt=start_dt,
            finish_dt=finish_dt,
            work_hour=work_hour,
            type=shift_type,
            staff=staff
        )

    def _create_leave_type(self):
        leave_type = self.faker.bothify(text='Leave Type-????-###')
        return LeaveTypeModel.objects.create(type=leave_type)

    def _create_staff_leave(self, staff=None, start_dt=None, finish_dt=None, duration_type=None):
        start_dt = start_dt if start_dt else datetime.datetime.now()
        finish_dt = finish_dt if finish_dt else start_dt + datetime.timedelta(days=1)
        inst_staff = staff if staff else self._create_staff()
        duration_type = duration_type if duration_type else LeaveDurationTypeEnum.DAY
        inst_leave_type = self._create_leave_type()

        inst = StaffLeaveModel.objects.create(
            start_dt=start_dt,
            finish_dt=finish_dt,
            work_start_dt=finish_dt,
            staff=inst_staff,
            leave_type=inst_leave_type,
            duration=1,
            duration_type=duration_type
        )

        return inst
