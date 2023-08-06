from betik_app_staff.enums import ShiftTypeEnum
from betik_app_staff.models import IndividualShiftModel, ShiftRuleModel, BusinessDayModel, BankHolidayModel, \
    HolidayModel


def find_working_hour_in_date(date, staff):
    ret_val = []
    # personelin mesai saati şu şekilde bulunur;
    # öncelik sırası vardır.
    # 1- Özel vardiyaya bakılır.
    # 2- Vardiya kuralına göre, çalışma saatine bakılır.
    # 3- Genel iş kuralına göre çalışma saatine bakılır.

    # EXCHANGE tipi normal mesai saati ile yer değiştirmesi anlamına gelir.
    # verilen tarihde böyle bir özel vardiya eklenmişse, diğer vardiya ve genel iş kuralına bakılmaz. Çünkü
    # personel o tarihde zaten normal mesai saatini almıştır.

    # OVERTIME tipi fazla mesai demektir. O gün personel hem normal mesaisi + fazla mesaisi vardır demek.
    # eğer özel mesai olarak normal mesai girilmemişse, vardiyaya ve genel iş günü kuralına bakarak
    # o günkü normal mesai saatlei bulunur

    # eğer WEEKEND özel mesaisi girilmişse, o gün normal mesaisi yoktur diğerlerine bakılmaz
    # eğer HOLIDAY özel mesaisi girilmişse, o gün normal mesaisi yoktur diğerlerine bakılmaz

    is_bank_holiday = BankHolidayModel.objects.is_holiday(date)
    is_holiday = HolidayModel.objects.is_holiday(date)

    # normal emsai tipleri
    normal_shift_type = [
        ShiftTypeEnum.NORMAL,
        ShiftTypeEnum.HOLIDAY,
        ShiftTypeEnum.WEEKEND
    ]

    # özel vardiyada birden fazla kayıt gelebilir
    individual_business_days = IndividualShiftModel.objects.list_business_day_on_date(date, staff)

    has_normal_shift = False
    if individual_business_days:
        for inst_bd in individual_business_days:

            working_time = {
                'start_dt': inst_bd.start_dt,
                'finish_dt': inst_bd.finish_dt,
                'work_hour': inst_bd.work_hour,
                '_instance': inst_bd
            }
            ret_val.append(working_time)

            if inst_bd.type in normal_shift_type:
                has_normal_shift = True

    # eğer özel vardiyası yoksa, sırasıyla diğer kurallara bakarak çalışma saatleri bulunur
    # özel vardiya olarak OVERTIME(fazla mesai eklenmişse), normal mesaisini bulmak için diğer kurallara bakılır
    # özel vardiya olarak EXCHANGE(normal mesai), WEEKEND(pazar mesaisi), HOLIDAY(tatil mesaisi) eklenmişse
    # diğer kurallara bakılmaz
    if not is_holiday and not is_bank_holiday:
        if not individual_business_days or not has_normal_shift:
            inst_shift_business_day = ShiftRuleModel.objects.get_shift_rule_on_date(date, staff)
            if inst_shift_business_day:
                working_time = inst_shift_business_day.get_business_day_on_date(date, staff)

                # bu gün çalışma varsa
                if working_time:
                    ret_val.append(working_time)

            # genel vardiyası yoksa, bu tarihdeki genel iş gününe göre çalışma saatini al
            if not inst_shift_business_day:
                inst_business_day = BusinessDayModel.objects.get_business_rule_on_date(date, staff)

                if inst_business_day:
                    working_time = inst_business_day.get_business_day_on_date(date)

                    # bu gün çalışma varsa
                    if working_time:
                        ret_val.append(working_time)
                else:
                    # personelin, bu tarihdeki çalışma saati, belirlenmemiş
                    # yada artık bu personelin bu tarihden sonra çalışması istenmemiş
                    pass

    return ret_val
