from django.db import transaction
from rest_framework import serializers

from betik_app_staff.models import DepartmentModel, StaffModel, TitleModel, StaffTypeModel, PassiveReasonModel, \
    PassiveStaffLogModel, DismissReasonModel, DismissStaffLogModel


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
