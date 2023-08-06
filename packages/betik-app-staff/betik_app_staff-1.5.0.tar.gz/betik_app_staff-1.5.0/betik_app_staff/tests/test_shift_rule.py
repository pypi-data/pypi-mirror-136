import datetime

from django.urls import reverse
from django.utils.translation import gettext as _

from betik_app_staff.enums import ShiftTypeEnum
from betik_app_staff.models import ShiftRuleModel, ShiftRuleStaffModel, IndividualShiftModel
from betik_app_staff.serializers.shift_rule import ShiftRuleSerializer
from betik_app_staff.tests.base import TestBase


class TestShiftRuleBase(TestBase):
    def _create_post_data(self):
        future_date = self.faker.future_date()
        future_date += datetime.timedelta(days=10)
        day_diff = future_date.weekday() - 0

        start_date = future_date - datetime.timedelta(days=day_diff)
        name = self.faker.bothify(text='Shift Rule-????-###')

        return {
            'name': name,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'finish_date': None,
            'period_duration': 2,
            'business_days': [
                {
                    'shift_no': 1,
                    'monday': {'start_time': '11:00', 'work_hour': 8},
                    'tuesday': {'start_time': '11:00', 'work_hour': 8},
                    'wednesday': {'start_time': '11:00', 'work_hour': 8},
                    'thursday': {'start_time': '11:00', 'work_hour': 8},
                    'friday': {'start_time': '11:00', 'work_hour': 8},
                    'saturday': {'start_time': '11:00', 'work_hour': 8},
                    'sunday': {'start_time': '11:00', 'work_hour': 8}
                },
                {
                    'shift_no': 2,
                    'monday': {'start_time': '19:00', 'work_hour': 8},
                    'tuesday': {'start_time': '19:00', 'work_hour': 8},
                    'wednesday': {'start_time': '19:00', 'work_hour': 8},
                    'thursday': {'start_time': '19:00', 'work_hour': 8},
                    'friday': {'start_time': '19:00', 'work_hour': 8},
                    'saturday': {'start_time': '19:00', 'work_hour': 8},
                    'sunday': {'start_time': '19:00', 'work_hour': 8}
                }
            ]
        }


class TestCRUD(TestShiftRuleBase):
    def test_create(self):
        post_data = self._create_post_data()

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        inst = ShiftRuleModel.objects.get(id=1)
        serializer_data = ShiftRuleSerializer(instance=inst).data
        self.assertDictEqual(response.data, serializer_data)

    def test_update(self):
        inst = self._create_shift_rule()

        put_data = self._create_post_data()

        url = reverse('betik_app_staff:shift-rule-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 200, response.data)

        inst = ShiftRuleModel.objects.get(id=1)
        serializer_data = ShiftRuleSerializer(instance=inst).data
        self.assertDictEqual(response.data, serializer_data)

    def test_delete(self):
        inst = self._create_shift_rule()

        url = reverse('betik_app_staff:shift-rule-delete', kwargs={'pk': inst.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)

    def test_paginate(self):
        self._create_shift_rule()
        self._create_shift_rule()

        url = reverse('betik_app_staff:shift-rule-paginate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

        instances = ShiftRuleModel.objects.all().order_by('-start_date', '-id')
        serializer_dict = ShiftRuleSerializer(instance=instances, many=True).data
        self.assertListEqual(response.data['results'], serializer_dict)

        count = 2
        self.assertEqual(count, response.data['count'])


class TestCreateFail(TestShiftRuleBase):
    def test_finish_date_is_bigger_than_start_date(self):
        """
            bitiş tarihi, başlama tarihinden sonra olmalı
        """
        post_data = self._create_post_data()

        start_date = datetime.datetime.strptime(post_data['start_date'], "%Y-%m-%d")
        finish_date = start_date - datetime.timedelta(days=1)

        post_data['finish_date'] = finish_date.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:shift-rule-create')

        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than start date(%(date)s)') % {'date': start_date.strftime('%d %B %Y')}
        self.assertDictEqual(response.data, {'finish_date': [msg]})

        post_data['finish_date'] = post_data['start_date']
        response = self.client.post(url, post_data, format='json')
        self.assertDictEqual(response.data, {'finish_date': [msg]})

    def test_start_date_must_fall_on_monday(self):
        """
            başlama tarihi pazartesi gününe denk gelmeli
        """
        post_data = self._create_post_data()

        start_date = None
        while start_date is None or start_date.weekday() == 0:
            start_date = self.faker.future_date()
        post_data['start_date'] = start_date.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:shift-rule-create')

        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must fall on monday')
        self.assertDictEqual(response.data, {'start_date': [msg]})

    def test_finish_date_must_fall_on_monday(self):
        """
            bitiş tarihi pazartesi gününe denk gelmeli
        """
        post_data = self._create_post_data()

        start_date = datetime.datetime.strptime(post_data['start_date'], "%Y-%m-%d")
        finish_date = start_date + datetime.timedelta(days=1)
        while finish_date.weekday() == 0:
            finish_date += datetime.timedelta(days=1)
        post_data['finish_date'] = finish_date.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:shift-rule-create')

        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('must fall on monday')
        self.assertDictEqual(response.data, {'finish_date': [msg]})

    def test_start_date_is_bigger_than_today(self):
        """
            başlama tarihi bugünden sonraki bir tarih olmalı
        """
        today = datetime.datetime.today().date()
        while today.weekday() != 0:
            today -= datetime.timedelta(days=1)

        post_data = self._create_post_data()

        post_data['start_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:shift-rule-create')

        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'start_date': [msg]})

    def test_shift_numbers_must_be_consecutive_starting_from_1(self):
        """
            vardiya numaraları 1'den başlayarak ardışık olmalıdır
        """
        post_data = self._create_post_data()

        # 1. vardiyanın numarasını 2 yap
        post_data['business_days'][0]['shift_no'] = 2

        url = reverse('betik_app_staff:shift-rule-create')

        response = self.client.post(url, post_data, format='json')

        msg = _('must be %(no)d') % {'no': 1}
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {0: {'shift_no': [msg]}}})

        post_data = self._create_post_data()

        # 2. vardiyanın numarasını 3 yap, ardışıklığı boz
        post_data['business_days'][1]['shift_no'] = 3

        response = self.client.post(url, post_data, format='json')

        msg = _('must be %(no)d') % {'no': 2}
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {1: {'shift_no': [msg]}}})

    def test_finish_time_of_last_day_of_n_shift_cannot_be_greater_than_start_time_of_first_day_of_n1_shift(self):
        """
            n. vardiyanın son gününün bitiş saati, (n+1). vardiyanın ilk gününün başlangıç saatinden büyük olamaz.
        """
        # n. vardiyadan, (n+1). vardiyaya geçiş

        post_data = self._create_post_data()

        # 1. vardiyanın son gün çalışma saatleri
        # ...
        # 'sunday': {
        #     'start_time': '11:00',
        #     'work_hour': 8
        # }

        # 2. vardiyanın ilk gün çalışma saatleri
        # {
        # 'monday': {
        #     'start_time': '19:00',
        #     'work_hour': 8
        # }...

        # bir sonraki vardiyanın ilk gününün başlama saati ile çakışması
        # n. vardiyanın son günü pazar, (n+1). vardiyanın ilk günü pazartesi
        # hafta değişimi var

        n = 0
        # n. vardiyanın son gününün(pazar), çalışma aaati uzatıldı,
        # bitiş saati pazartesi günü, saat 07:00 olarak ayarlandı
        post_data['business_days'][n]['sunday']['work_hour'] = 20

        # (n+1). vardiyanın ilk gününün(pazartesi), başlama saati 06:00 olarak ayarlandı
        post_data['business_days'][n + 1]['monday']['start_time'] = '06:00'

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('bigger than or equal %(time)s') % {'time': '07:00'}
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {n + 1: {'monday': {'start_time': [msg]}}}})

        # bir sonraki vardiyanın ilk gününün başlama saati ile çakışması
        # hafta değişimi yok

        post_data = self._create_post_data()

        # n. vardiya pazartesi,salı,çarşamba çalışsın
        post_data['business_days'][n]['thursday'] = None
        post_data['business_days'][n]['friday'] = None
        post_data['business_days'][n]['saturday'] = None
        post_data['business_days'][n]['sunday'] = None

        # (n+1). vardiya perşembe, cuma,cumartesi,pazar çalışasın
        post_data['business_days'][n + 1]['monday'] = None
        post_data['business_days'][n + 1]['tuesday'] = None
        post_data['business_days'][n + 1]['wednesday'] = None

        # n. vardiyanın son gününün(çarşamba), çalışma aaati uzatıldı,
        # bitiş saati perşembe günü, saat 07:00 olarak ayarlandı
        post_data['business_days'][n]['wednesday']['work_hour'] = 20

        # (n+1). vardiyanın ilk gününün(perşembe), başlama saati 06:00 olarak ayarlandı
        post_data['business_days'][n + 1]['thursday']['start_time'] = '06:00'

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('bigger than or equal %(time)s') % {'time': '07:00'}
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {n + 1: {'thursday': {'start_time': [msg]}}}})

    def test_finish_time_of_last_day_of_last_shift_cannot_be_greater_than_start_time_of_first_day_of_first_shift(self):
        """
            Son vardiyanın son gününün bitiş zamanı, ilk vardiyanın ilk gününün başlama zamanından büyük olamaz.
        """
        # sonuncu vardiyadan, ilk vardiyaya geçiş

        post_data = self._create_post_data()

        # ilk vardiyanın ilk gün çalışma saatleri
        # 'monday': {
        #     'start_time': '11:00',
        #     'work_hour': 8
        # }
        # ...

        # son vardiyanın son gün çalışma saatleri
        # ...
        # 'sunday': {
        #     'start_time': '19:00',
        #     'work_hour': 8
        # }

        last = 1
        first = 0
        # sonuncu vardiyanın son gününün(pazar), çalışma aaati uzatıldı,
        # bitiş saati pazartesi günü, saat 15:00 olarak ayarlandı
        post_data['business_days'][last]['sunday']['work_hour'] = 20

        # ilk vardiyanın ilk gününün(pazartesi), başlama saati 06:00 olarak ayarlandı
        post_data['business_days'][first]['monday']['start_time'] = '06:00'

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('bigger than %(time)s') % {'time': '15:00'}
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {first: {'monday': {'start_time': [msg]}}}})

    def test_incorrect_data_type_of_business_days_item(self):
        """
            business_days datasının elemanları dict tipinde olmalı
        """
        post_data = self._create_post_data()
        index = 1
        data = 20
        post_data['business_days'][index] = data

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('Incorrect type. Expected a dict, but got %s') % type(data).__name__
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: [msg]}})

    def test_shift_no_required(self):
        """
            herbir vardiya için, vardiya numarası tanımlanmalı
        """
        post_data = self._create_post_data()
        index = 1
        post_data['business_days'][index]['shift_no'] = None

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('required')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'shift_no': [msg]}}})

    def test_shift_no_must_be_a_number(self):
        """
            vardiya numarası sayı olmalı
        """
        post_data = self._create_post_data()
        index = 1
        post_data['business_days'][index]['shift_no'] = 'ae'

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('must be a number')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'shift_no': [msg]}}})

    def test_shift_no_is_bigger_than_zero(self):
        """
            vardiya numarası sıfırdan büyük bir sayı olmalı
        """
        post_data = self._create_post_data()
        index = 1
        post_data['business_days'][index]['shift_no'] = -1

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('must be bigger than 0')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'shift_no': [msg]}}})

        post_data['business_days'][index]['shift_no'] = 0

        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'shift_no': [msg]}}})

    def test_day_of_the_week_not_found(self):
        """
            haftanın tüm günleri, datanın içinde key olarak bulunması lazım
        """
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for d in days:
            post_data = self._create_post_data()
            index = 1
            del post_data['business_days'][index][d]

            url = reverse('betik_app_staff:shift-rule-create')
            response = self.client.post(url, post_data, format='json')

            msg = _('not found')
            self.assertEqual(response.status_code, 400, response.data)
            self.assertDictEqual(response.data, {'business_days': {index: {d: [msg]}}})

    def test_start_time_required(self):
        """
            her gün için başlama saati girilmeli
        """

        post_data = self._create_post_data()
        index = 1
        post_data['business_days'][index]['monday']['start_time'] = None

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('required')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'monday': {'start_time': [msg]}}}})

    def test_start_time_incorrect_format(self):
        """
            başlama saati HH:MM formatında olmalı
        """

        post_data = self._create_post_data()
        index = 1
        post_data['business_days'][index]['monday']['start_time'] = "25:45"

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('Incorrect time format. Expected `%H:%M`')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'monday': {'start_time': [msg]}}}})

        post_data['business_days'][index]['monday']['start_time'] = "AA"

        response = self.client.post(url, post_data, format='json')

        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'monday': {'start_time': [msg]}}}})

    def test_work_hour_required(self):
        """
            her gün için çalışma saati girilmeli
        """

        post_data = self._create_post_data()
        index = 1
        post_data['business_days'][index]['monday']['work_hour'] = None

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('required')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'monday': {'work_hour': [msg]}}}})

    def test_work_hour_must_be_a_number(self):
        """
            çalışma saati sayı olmalı
        """
        post_data = self._create_post_data()
        index = 1
        post_data['business_days'][index]['monday']['work_hour'] = "k"

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('must be a number')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'monday': {'work_hour': [msg]}}}})

    def test_work_hour_is_bigger_than_zero(self):
        """
            çalışma saati sıfırdan büyük bir sayı olmalı
        """
        post_data = self._create_post_data()
        index = 1
        post_data['business_days'][index]['monday']['work_hour'] = -1

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('must be bigger than 0')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'monday': {'work_hour': [msg]}}}})

        post_data['business_days'][index]['monday']['work_hour'] = 0

        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'monday': {'work_hour': [msg]}}}})

    def test_work_hour_is_less_than_24(self):
        """
            çalışma saati 24 saatten fazla olamaz
        """
        post_data = self._create_post_data()
        index = 1
        post_data['business_days'][index]['monday']['work_hour'] = 25

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('must be less than %(hour)d') % {'hour': 24}
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {index: {'monday': {'work_hour': [msg]}}}})

    def test_n_end_time_of_day_n1_cannot_be_greater_than_start_time_of_day(self):
        """
            n. günün bitiş saati, (n+1). günün başlangıç saatinden büyük olamaz.
        """
        # aynı vardiyada bir sonraki güne geçiş

        post_data = self._create_post_data()

        # bitiş saati salı günü, saat 15:00 olarak ayarlandı
        post_data['business_days'][0]['monday']['work_hour'] = 20

        # salı başlama saati 06:00 olarak ayarlandı
        post_data['business_days'][0]['tuesday']['start_time'] = '06:00'

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('bigger than or equal %(time)s') % {'time': '07:00'}
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {0: {'tuesday': {'start_time': [msg]}}}})

    def test_finish_time_of_last_day_in_same_shift_cannot_be_greater_than_start_time_of_first_day(self):
        """
            pazar günü vardiyası, pazartesi günü bitiyorsa, pazartesi günü başlayan vardiyanın başlama saatini geçmesin
        """

        post_data = self._create_post_data()

        # bitiş saati salı günü, saat 15:00 olarak ayarlandı
        post_data['business_days'][0]['sunday']['work_hour'] = 20

        # salı başlama saati 06:00 olarak ayarlandı
        post_data['business_days'][0]['monday']['start_time'] = '06:00'

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('bigger than or equal %(time)s') % {'time': '07:00'}
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'business_days': {0: {'monday': {'start_time': [msg]}}}})

    def test_duplicate_name(self):
        """
            aynı ada sahip birden fazla vardiya kuralı olamaz
        """

        inst = self._create_shift_rule()
        post_data = self._create_post_data()

        post_data['name'] = inst.name

        url = reverse('betik_app_staff:shift-rule-create')
        response = self.client.post(url, post_data, format='json')

        msg = _('shift rule model with this name already exists.')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertDictEqual(response.data, {'name': [msg]})


class TestUpdateFail(TestShiftRuleBase):
    def test_anything_other_than_finish_date_of_active_registrations_cannot_be_changed(self):
        """
            aktif kayıtların sadece bitiş tarihleri değiştirilebilir
        """
        today = datetime.datetime.today().date()

        inst = self._create_shift_rule()
        inst.start_date = today
        inst.save()

        put_data = self._create_post_data()
        url = reverse('betik_app_staff:shift-rule-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('Anything other than the finish date of active registrations cannot be changed')
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_expired_records_cannot_be_changed_in_any_way(self):
        """
            geçmişte kalan kayıtlar değiştirilemez
        """
        today = datetime.datetime.today().date()
        yesterday = today - datetime.timedelta(days=1)

        inst = self._create_shift_rule()
        inst.start_date = yesterday
        inst.finish_date = today
        inst.save()

        put_data = self._create_post_data()
        url = reverse('betik_app_staff:shift-rule-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('expired records cannot be changed in any way')
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_start_date_bigger_than_today(self):
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        inst = self._create_shift_rule()
        inst.start_date = tomorrow
        inst.save()

        put_data = self._create_post_data()
        put_data['start_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:shift-rule-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'start_date': [msg]})

    def test_finish_date_bigger_than_today(self):
        today = datetime.datetime.today().date()
        tomorrow = today + datetime.timedelta(days=1)

        inst = self._create_shift_rule()
        inst.start_date = tomorrow
        inst.save()

        put_data = self._create_post_data()
        put_data['finish_date'] = today.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:shift-rule-update', kwargs={'pk': inst.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('bigger than today')
        self.assertDictEqual(response.data, {'finish_date': [msg]})

    def test_conflict_date_that_belongs_same_staff(self):
        inst_staff = self._create_staff()

        today = datetime.datetime.today().date()
        next_20_day = today + datetime.timedelta(days=20)

        day_diff = next_20_day.weekday() - 0
        next_20_day = next_20_day - datetime.timedelta(days=day_diff)
        next_13_day = next_20_day - datetime.timedelta(days=7)

        inst_shift_rule1 = self._create_shift_rule()
        inst_shift_rule1.start_date = today
        inst_shift_rule1.finish_date = next_20_day
        inst_shift_rule1.save()

        inst_shift_rule2 = self._create_shift_rule()

        ShiftRuleStaffModel.objects.create(staff=inst_staff, shift_rule=inst_shift_rule1, shift_no=1)
        ShiftRuleStaffModel.objects.create(staff=inst_staff, shift_rule=inst_shift_rule2, shift_no=1)

        put_data = self._create_post_data()
        put_data['start_date'] = next_13_day.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:shift-rule-update', kwargs={'pk': inst_shift_rule2.id})
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        msg = _(
            'There are %(count)d joint staff both in this shift and in the shift named %(shift_name)s. Unable to edit because the dates of these two shifts overlap') % {
                  'count': 1,
                  'shift_name': inst_shift_rule1.name
              }

        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_after_update_date_conflict_staff_individual_shift(self):
        """
            vardiya kuralının başlama veya bitiş tarihi güncellendikden sonra, bu vardiyaya kayıtlı personellerin, özel vardiyalarıyla olan çakışması
        """
        # personel oluştur
        inst_staff = self._create_staff()

        # 10 gün sonra başlayacak vardiya kuralı oluştur ve bu kurala üstteki personeli ekle
        after_10days = datetime.datetime.today() + datetime.timedelta(days=10)
        inst_shift_rule = self._create_shift_rule()
        inst_shift_rule.start_date = after_10days
        inst_shift_rule.business_days = [
            {
                'shift_no': 1,
                'monday': {'start_time': '09:00', 'work_hour': 8},
                'tuesday': {'start_time': '09:00', 'work_hour': 8},
                'wednesday': {'start_time': '09:00', 'work_hour': 8},
                'thursday': {'start_time': '09:00', 'work_hour': 8},
                'friday': {'start_time': '09:00', 'work_hour': 8},
                'saturday': {'start_time': '09:00', 'work_hour': 8},
                'sunday': {'start_time': '09:00', 'work_hour': 8}
            },
            {
                'shift_no': 2,
                'monday': {'start_time': '09:00', 'work_hour': 8},
                'tuesday': {'start_time': '09:00', 'work_hour': 8},
                'wednesday': {'start_time': '09:00', 'work_hour': 8},
                'thursday': {'start_time': '09:00', 'work_hour': 8},
                'friday': {'start_time': '09:00', 'work_hour': 8},
                'saturday': {'start_time': '09:00', 'work_hour': 8},
                'sunday': {'start_time': '09:00', 'work_hour': 8}
            }
        ]
        inst_shift_rule.save()

        ShiftRuleStaffModel.objects.create(
            shift_rule=inst_shift_rule,
            staff=inst_staff,
            shift_no=1
        )

        # personele yarından sonra başlayacak olan bir özel vardiya ekle.
        # tarih en az iki gün sonra ilk salı günü 16:00 - çarşamba 00:00 arasında
        tuesday = datetime.datetime.today() + datetime.timedelta(days=2)
        work_hour = 8
        while tuesday.weekday() != 1:
            tuesday += datetime.timedelta(days=1)
        start_dt = datetime.datetime.combine(tuesday, datetime.time(hour=16))
        finish_dt = start_dt + datetime.timedelta(hours=work_hour)

        inst_staff_ind_shift = IndividualShiftModel.objects.create(
            start_dt=start_dt,
            finish_dt=finish_dt,
            work_hour=work_hour,
            type=ShiftTypeEnum.OVERTIME,
            staff=inst_staff
        )

        # vardiya kuralının başlangıç tarihini pazartesi yap
        # böylece yukarıdaki personelin özel vardiyasıyla çakışsın
        monday = tuesday - datetime.timedelta(days=1)
        post_data = self._create_post_data()
        post_data['business_days'] = inst_shift_rule.business_days
        post_data['start_date'] = monday.strftime("%Y-%m-%d")

        url = reverse('betik_app_staff:shift-rule-update', kwargs={'pk': inst_shift_rule.id})
        response = self.client.put(url, data=post_data, format='json')
        self.assertEqual(response.status_code, 400, response.data)

        tuesday_business_day = inst_shift_rule.get_business_day_on_date(tuesday, inst_staff)

        msg = _('Conflicts detected on %(count)d shift times') % {
            'count': 1
        }

        msg_item = _('Staff named %(name)s %(last_name)s with ID number %(identity)s,') % {
            'name': inst_staff.person.name,
            'last_name': inst_staff.person.last_name,
            'identity': inst_staff.person.identity
        }

        msg_item += " " + _(
            'working hours depending on the individual shift id #%(id)d(%(date1)s - %(date2)s)') % {
                        'id': 1,
                        'date1': start_dt.strftime("%d %B %Y %H:%M"),
                        'date2': finish_dt.strftime("%d %B %Y %H:%M")
                    }

        msg_item += " " + _("with")

        msg_item += " " + _(
            'working hours depending on the shift rule name %(name)s(%(date1)s - %(date2)s)') % {
                        'name': post_data['name'],
                        'date1': tuesday_business_day.get('start_dt').strftime("%d %B %Y %H:%M"),
                        'date2': tuesday_business_day.get('finish_dt').strftime("%d %B %Y %H:%M")
                    }

        msg_item += " " + _('overlap')

        self.assertDictEqual(response.data, {'detail': msg, 'staff_errors': [msg_item]})


class TestDeleteFail(TestShiftRuleBase):
    def test_active_record_can_not_be_deleted(self):
        """
            aktif kayıt silinemez
        """
        today = datetime.datetime.today().date()

        inst = self._create_shift_rule()
        inst.start_date = today
        inst.save()

        url = reverse('betik_app_staff:shift-rule-delete', kwargs={'pk': inst.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('active record can not be deleted')
        self.assertDictEqual(response.data, {'detail': [msg]})

    def test_outdated_record_can_not_be_deleted(self):
        """
            geçmişte kalan kayıt silinemez
        """
        today = datetime.datetime.today().date()
        yesterday = today - datetime.timedelta(days=1)

        inst = self._create_shift_rule()
        inst.start_date = yesterday
        inst.finish_date = today
        inst.save()

        url = reverse('betik_app_staff:shift-rule-delete', kwargs={'pk': inst.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400, response.data)

        msg = _('outdated record can not be deleted')
        self.assertDictEqual(response.data, {'detail': [msg]})
