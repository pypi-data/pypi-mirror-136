from betik_app_document.models import DocumentTypeModel, DocumentModel
from betik_app_document.serializers import DocumentSerializerForParent, BulkDocumentSerializerForParent
from betik_app_util.mixins import SetCreatedUpdatedUserFromSerializerContextMixin
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from betik_app_person.models import NaturalPersonModel
from betik_app_person.serializers import NaturalPersonSerializer
from betik_app_util import resolvers
from betik_app_util.table_fields import IntegerField, StringField, DateField, DateTimeField
from rest_framework import serializers

from betik_app_staff.enums import StaffStatusEnum
from betik_app_staff.models import DepartmentModel, TitleModel, StaffTypeModel, StaffModel


class DepartmentSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    class Meta:
        model = DepartmentModel
        fields = ['id', 'name', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        read_only_fields = ['id', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        table_fields = [
            IntegerField('id', _('Department ID')),
            StringField('name', _('Department')),
            DateTimeField('created_dt', _('Created Time')),
            StringField('created_user', _('Created User')),
            DateTimeField('updated_dt', _('Updated Time')),
            StringField('updated_user', _('Updated User'))
        ]


class TitleSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    class Meta:
        ref_name = "StaffTitle"
        model = TitleModel
        fields = ['id', 'name', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        read_only_fields = ['id', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        table_fields = [
            IntegerField('id', _('Title ID')),
            StringField('name', _('Title')),
            DateTimeField('created_dt', _('Created Time')),
            StringField('created_user', _('Created User')),
            DateTimeField('updated_dt', _('Updated Time')),
            StringField('updated_user', _('Updated User'))
        ]


class StaffTypeSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    class Meta:
        model = StaffTypeModel
        fields = ['id', 'name', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        read_only_fields = ['id', 'created_dt', 'created_user', 'updated_dt', 'updated_user']
        table_fields = [
            IntegerField('id', _('Staff Type ID')),
            StringField('name', _('Staff Type')),
            DateTimeField('created_dt', _('Created Time')),
            StringField('created_user', _('Created User')),
            DateTimeField('updated_dt', _('Updated Time')),
            StringField('updated_user', _('Updated User'))
        ]


class StaffSerializer(SetCreatedUpdatedUserFromSerializerContextMixin, serializers.ModelSerializer):
    status_code = serializers.ChoiceField(choices=StaffStatusEnum.types, source='status', read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    person_id = serializers.PrimaryKeyRelatedField(queryset=NaturalPersonModel.objects.all(), source='person',
                                                   write_only=True)
    person = NaturalPersonSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=DepartmentModel.objects.all(), source='department',
                                                       write_only=True)
    department = DepartmentSerializer(read_only=True)
    staff_type_id = serializers.PrimaryKeyRelatedField(queryset=StaffTypeModel.objects.all(), source='staff_type',
                                                       write_only=True)
    staff_type = StaffTypeSerializer(read_only=True)
    title_id = serializers.PrimaryKeyRelatedField(queryset=TitleModel.objects.all(), source='title',
                                                  write_only=True)
    title = TitleSerializer(read_only=True)

    file_employment_agreement = DocumentSerializerForParent(required=False, allow_null=True)
    file_statement_of_insured_employment = DocumentSerializerForParent(required=False, allow_null=True)
    files = BulkDocumentSerializerForParent(many=True, required=False, allow_null=True)

    class Meta:
        model = StaffModel
        fields = [
            'id', 'person_id', 'person', 'registration_number', 'department_id', 'department', 'staff_type_id',
            'staff_type', 'title_id', 'title', 'start_date', 'finish_date', 'status_code', 'status', 'created_dt',
            'created_user', 'updated_dt', 'updated_user', 'file_statement_of_insured_employment',
            'file_employment_agreement', 'files'
        ]
        read_only_fields = [
            'id', 'finish_date', 'status_code', 'status', 'person', 'department', 'staff_type', 'title', 'status',
            'created_dt', 'created_user', 'updated_dt', 'updated_user'
        ]

        @staticmethod
        def table_fields():
            fields = [
                IntegerField('id', 'ID'),
                IntegerField('status_code', _('Status Code')),
                StringField('status', _('Status')),
                StringField('registration_number', _('Registration Number')),
                DateField('start_date', _('Start Date')),
                DateField('finish_date', _('Finish Date')),
                DateTimeField('created_dt', _('Created Time')),
                StringField('created_user', _('Created User')),
                DateTimeField('updated_dt', _('Updated Time')),
                StringField('updated_user', _('Updated User'))

            ]

            person_fields = resolvers.get_table_fields_from_serializer_class(NaturalPersonSerializer)
            for k, v in enumerate(person_fields):
                v.code = 'person.' + v.code
                if v.code == 'id':
                    v.label = _('Person ID')
                fields.append(v)

            department_fields = resolvers.get_table_fields_from_serializer_class(DepartmentSerializer)
            for k, v in enumerate(department_fields):
                department_fields[k].code = 'department.' + v.code

            staff_type_fields = resolvers.get_table_fields_from_serializer_class(StaffTypeSerializer)
            for k, v in enumerate(staff_type_fields):
                staff_type_fields[k].code = 'staff_type.' + v.code

            title_fields = resolvers.get_table_fields_from_serializer_class(TitleSerializer)
            for k, v in enumerate(title_fields):
                title_fields[k].code = 'title.' + v.code

            return fields

    def validate(self, attrs):
        attrs = super().validate(attrs)
        finish_date = attrs.get('finish_date', None)

        if self.instance:
            if self.instance.finish_date and not finish_date:
                raise serializers.ValidationError({'finish_date': [_('Required for inactive staff')]})
            elif not self.instance.finish_date and finish_date:
                raise serializers.ValidationError({'finish_date': [_('Not required for active staff')]})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        file_statement_of_insured_employment = validated_data.pop('file_statement_of_insured_employment', None)
        file_employment_agreement = validated_data.pop('file_employment_agreement', None)
        files = validated_data.pop('files', [])

        instance = super().create(validated_data)

        doc_owner_tags = f"{instance.person.identity},{instance.person.name} {instance.person.last_name}"

        ##################################
        # Statement of Insured Employment
        ##################################
        if file_statement_of_insured_employment:
            doc_desc = _(
                "Statement of insured employment of staff who has identity number %(identity)s and register number %(register_no)s and name %(name)s %(last_name)s") % {
                           'identity': instance.person.identity,
                           'name': instance.person.name,
                           'last_name': instance.person.last_name,
                           'register_no': instance.registration_number
                       }
            inst_doc_type = DocumentTypeModel.objects.get(code=DocumentTypeModel.STATEMENT_OF_INSURED_EMPLOYMENT)
            inst_file_statement_of_insured_employment = DocumentModel.objects.create(
                **file_statement_of_insured_employment,
                document_type=inst_doc_type,
                document_owner_tags=doc_owner_tags,
                description=doc_desc,
                content_object=instance,
                parent_document_code=1
            )
            instance.file_statement_of_insured_employment = inst_file_statement_of_insured_employment
            instance.save()

        ##########################
        # Employment agreement
        ##########################
        if file_employment_agreement:
            doc_desc = _(
                "Employment agreement of staff who has identity number %(identity)s and register number %(register_no)s and name %(name)s %(last_name)s") % {
                           'identity': instance.person.identity,
                           'name': instance.person.name,
                           'last_name': instance.person.last_name,
                           'register_no': instance.registration_number
                       }
            inst_doc_type = DocumentTypeModel.objects.get(code=DocumentTypeModel.EMPLOYMENT_AGREEMENT)
            inst_file_employment_agreement = DocumentModel.objects.create(
                **file_employment_agreement,
                document_type=inst_doc_type,
                document_owner_tags=doc_owner_tags,
                description=doc_desc,
                content_object=instance,
                parent_document_code=2
            )
            instance.file_employment_agreement = inst_file_employment_agreement
            instance.save()

        ##############
        # Files
        ##############
        for file in files:
            instance.files.create(
                **file,
                content_object=instance,
                document_owner_tags=doc_owner_tags,
                parent_document_code=3
            )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        file_statement_of_insured_employment = validated_data.pop('file_statement_of_insured_employment', None)
        file_employment_agreement = validated_data.pop('file_employment_agreement', None)
        files = validated_data.pop('files', [])

        instance = super().update(instance, validated_data)

        doc_owner_tags = f"{instance.person.identity},{instance.person.name} {instance.person.last_name}"

        content_type = ContentType.objects.get_for_model(StaffModel)

        ##################################
        # Statement of Insured Employment
        ##################################
        if file_statement_of_insured_employment:
            doc_desc = _(
                "Statement of insured employment of staff who has identity number %(identity)s and register number %(register_no)s and name %(name)s %(last_name)s") % {
                           'identity': instance.person.identity,
                           'name': instance.person.name,
                           'last_name': instance.person.last_name,
                           'register_no': instance.registration_number
                       }
            inst_doc_type = DocumentTypeModel.objects.get(code=DocumentTypeModel.STATEMENT_OF_INSURED_EMPLOYMENT)
            file_statement_of_insured_employment.update({
                "document_owner_tags": doc_owner_tags,
                "description": doc_desc,
                "content_object": instance,
                "document_type": inst_doc_type
            })

            inst_file_statement_of_insured_employment, is_created = DocumentModel.objects.update_or_create(
                defaults=file_statement_of_insured_employment,
                content_type__pk=content_type.id,
                object_id=instance.id,
                parent_document_code=1
            )
            instance.file_statement_of_insured_employment = inst_file_statement_of_insured_employment
            instance.save()
        elif not self.partial:
            doc = instance.file_statement_of_insured_employment
            if doc:
                instance.file_statement_of_insured_employment = None
                instance.save()
                doc.delete()

        ###########################
        # Employment Agreement
        ###########################
        if file_employment_agreement:
            doc_desc = _(
                "Employment agreement of staff who has identity number %(identity)s and register number %(register_no)s and name %(name)s %(last_name)s") % {
                           'identity': instance.person.identity,
                           'name': instance.person.name,
                           'last_name': instance.person.last_name,
                           'register_no': instance.registration_number
                       }
            inst_doc_type = DocumentTypeModel.objects.get(code=DocumentTypeModel.EMPLOYMENT_AGREEMENT)
            file_employment_agreement.update({
                "document_owner_tags": doc_owner_tags,
                "description": doc_desc,
                "content_object": instance,
                "document_type": inst_doc_type
            })

            inst_file_employment_agreement, is_created = DocumentModel.objects.update_or_create(
                defaults=file_employment_agreement,
                content_type__pk=content_type.id,
                object_id=instance.id,
                parent_document_code=2

            )
            instance.file_employment_agreement = inst_file_employment_agreement
            instance.save()
        elif not self.partial:
            doc = instance.file_employment_agreement
            if doc:
                instance.file_employment_agreement = None
                instance.save()
                doc.delete()

        ##############
        # Files
        ##############
        if not self.partial:
            instance.files.clear()

            DocumentModel.objects.filter(
                content_type__id=content_type.id,
                object_id=instance.id,
                parent_document_code=3
            ).delete()

        if files:
            for file in files:
                instance.files.create(
                    **file,
                    content_object=instance,
                    document_owner_tags=doc_owner_tags,
                    parent_document_code=3
                )

        return instance
