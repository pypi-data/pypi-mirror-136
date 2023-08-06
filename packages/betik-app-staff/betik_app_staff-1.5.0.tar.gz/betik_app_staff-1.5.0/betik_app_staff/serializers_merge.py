from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import serializers

from betik_app_staff.models import DepartmentModel, StaffModel, TitleModel, StaffTypeModel, PassiveReasonModel, \
    PassiveStaffLogModel, DismissReasonModel, DismissStaffLogModel, ActiveReasonModel, ActiveStaffLogModel, \
    BusinessDayModel, AnnualLeaveRuleModel


class DepartmentMergeSerializer(serializers.ModelSerializer):
    source_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=DepartmentModel.objects.all()), min_length=1, write_only=True)
    result = serializers.BooleanField(read_only=True)

    class Meta:
        model = DepartmentModel
        fields = ['source_ids', 'result']

    @transaction.atomic
    def update(self, instance, validated_data):
        sources = validated_data.get('source_ids')
        source_ids = [item.id for item in sources]

        StaffModel.objects.filter(department__id__in=source_ids).update(department=instance)
        DepartmentModel.objects.filter(id__in=source_ids).exclude(id=instance.id).delete()

        return {'result': True}


class TitleMergeSerializer(serializers.ModelSerializer):
    source_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=TitleModel.objects.all()), min_length=1, write_only=True)
    result = serializers.BooleanField(read_only=True)

    class Meta:
        ref_name = "StaffTitleMerge"
        model = TitleModel
        fields = ['source_ids', 'result']

    @transaction.atomic
    def update(self, instance, validated_data):
        sources = validated_data.get('source_ids')
        source_ids = [item.id for item in sources]

        StaffModel.objects.filter(title__id__in=source_ids).update(title=instance)
        TitleModel.objects.filter(id__in=source_ids).exclude(id=instance.id).delete()

        return {'result': True}


class StaffTypeMergeSerializer(serializers.ModelSerializer):
    source_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=StaffTypeModel.objects.all()), min_length=1, write_only=True)
    result = serializers.BooleanField(read_only=True)

    class Meta:
        model = StaffTypeModel
        fields = ['source_ids', 'result']

    @transaction.atomic
    def update(self, instance, validated_data):
        sources = validated_data.get('source_ids')
        source_ids = [item.id for item in sources]

        StaffModel.objects.filter(staff_type__id__in=source_ids).update(staff_type=instance)
        BusinessDayModel.objects.filter(staff_type__id__in=source_ids).update(staff_type=instance)
        AnnualLeaveRuleModel.objects.filter(staff_type__id__in=source_ids).update(staff_type=instance)

        # genel iş vardiyasında, aynı personel tipi için, bir tarihde iki farklı kural gelmemeli
        list_business_day = BusinessDayModel.objects.filter(staff_type=instance)

        for inst_business_day1 in list_business_day:
            for inst_business_day2 in list_business_day:

                if inst_business_day1.is_conflict(inst_business_day2):
                    msg = _('There is a general business rule conflict after this merge.')
                    msg += ' ' + _(
                        'Business rule id #%(id1)d(%(date_range1)s) conflicts with business rule id #%(id2)d(%(date_range2)s)') % {
                               'id1': inst_business_day1.id,
                               'id2': inst_business_day2.id,
                               'date_range1': inst_business_day1.get_formatted_date_range(),
                               'date_range2': inst_business_day2.get_formatted_date_range()
                           }

                    raise serializers.ValidationError({'detail': msg})

        # yıllık izin kurallarında, aynı personel tipi için, bir tarihde iki farklı kural gelmemeli
        list_annual_leave_rule = AnnualLeaveRuleModel.objects.filter(staff_type=instance)

        for inst_annual_leave_rule1 in list_annual_leave_rule:
            for inst_annual_leave_rule2 in list_annual_leave_rule:

                if inst_annual_leave_rule1.is_conflict(inst_annual_leave_rule2):
                    msg = _('There is a annual leave rule conflict after this merge.')
                    msg += ' ' + _(
                        'Annual leave rule id #%(id1)d(%(date_range1)s) conflicts with annual leave rule id #%(id2)d(%(date_range2)s)') % {
                               'id1': inst_annual_leave_rule1.id,
                               'id2': inst_annual_leave_rule2.id,
                               'date_range1': inst_annual_leave_rule1.get_formatted_date_range(),
                               'date_range2': inst_annual_leave_rule2.get_formatted_date_range()
                           }

                    raise serializers.ValidationError({'detail': msg})

        StaffTypeModel.objects.filter(id__in=source_ids).exclude(id=instance.id).delete()

        return {'result': True}


class PassiveReasonMergeSerializer(serializers.ModelSerializer):
    source_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=PassiveReasonModel.objects.all()), min_length=1,
        write_only=True)
    result = serializers.BooleanField(read_only=True)

    class Meta:
        model = PassiveReasonModel
        fields = ['source_ids', 'result']

    @transaction.atomic
    def update(self, instance, validated_data):
        sources = validated_data.get('source_ids')
        source_ids = [item.id for item in sources]

        PassiveStaffLogModel.objects.filter(reason__id__in=source_ids).update(reason=instance)
        PassiveReasonModel.objects.filter(id__in=source_ids).exclude(id=instance.id).delete()

        return {'result': True}


class DismissReasonMergeSerializer(serializers.ModelSerializer):
    source_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=DismissReasonModel.objects.all()), min_length=1,
        write_only=True)
    result = serializers.BooleanField(read_only=True)

    class Meta:
        model = DismissReasonModel
        fields = ['source_ids', 'result']

    @transaction.atomic
    def update(self, instance, validated_data):
        sources = validated_data.get('source_ids')
        source_ids = [item.id for item in sources]

        DismissStaffLogModel.objects.filter(reason__id__in=source_ids).update(reason=instance)
        DismissReasonModel.objects.filter(id__in=source_ids).exclude(id=instance.id).delete()

        return {'result': True}


class ActiveReasonMergeSerializer(serializers.ModelSerializer):
    source_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=ActiveReasonModel.objects.all()), min_length=1,
        write_only=True)
    result = serializers.BooleanField(read_only=True)

    class Meta:
        model = ActiveReasonModel
        fields = ['source_ids', 'result']

    @transaction.atomic
    def update(self, instance, validated_data):
        sources = validated_data.get('source_ids')
        source_ids = [item.id for item in sources]

        ActiveStaffLogModel.objects.filter(reason__id__in=source_ids).update(reason=instance)
        ActiveReasonModel.objects.filter(id__in=source_ids).exclude(id=instance.id).delete()

        return {'result': True}
