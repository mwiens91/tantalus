from rest_framework import serializers
import tantalus.models
from taggit_serializer.serializers import (
    TagListSerializerField,
    TaggitSerializer)
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from rest_framework.exceptions import ValidationError
from tantalus.utils import start_transfers

class SampleSerializer(serializers.HyperlinkedModelSerializer):
    sample_id = serializers.CharField(
        validators=[
            UniqueValidator(queryset=tantalus.models.Sample.objects.all())
        ]
    )
    class Meta:
        model = tantalus.models.Sample
        fields = '__all__'


class SequenceDataFileSerializer(serializers.HyperlinkedModelSerializer):
    md5 = serializers.CharField(
        validators=[
            UniqueValidator(queryset=tantalus.models.SequenceDataFile.objects.all())
        ]
    )
    class Meta:
        model = tantalus.models.SequenceDataFile
        fields = '__all__'


class DNALibrarySerializer(serializers.HyperlinkedModelSerializer):
    library_id = serializers.CharField(
        validators=[
            UniqueValidator(queryset=tantalus.models.DNALibrary.objects.all())
        ]
    )
    class Meta:
        model = tantalus.models.DNALibrary
        fields = '__all__'


class DNASequencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = tantalus.models.DNASequences
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=tantalus.models.DNASequences.objects.all(),
                fields=('dna_library', 'index_sequence')
            )
        ]



class SequenceLaneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = tantalus.models.SequenceLane
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=tantalus.models.SequenceLane.objects.all(),
                fields=('flowcell_id', 'lane_number')
            )
        ]


class SequenceDatasetSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model = tantalus.models.SequenceDataset
        fields = '__all__'
    def to_representation(self, obj):
        if isinstance(obj, tantalus.models.SingleEndFastqFile):
            return SingleEndFastqFileSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, tantalus.models.PairedEndFastqFiles):
           return PairedEndFastqFilesSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, tantalus.models.BamFile):
           return BamFileSerializer(obj, context=self.context).to_representation(obj)
        return super(SequenceDatasetSerializer, self).to_representation(obj)


class SingleEndFastqFileSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model = tantalus.models.SingleEndFastqFile
        exclude = ['polymorphic_ctype']


class PairedEndFastqFilesSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model = tantalus.models.PairedEndFastqFiles
        exclude = ['polymorphic_ctype']


class BamFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = tantalus.models.BamFile
        exclude = ['polymorphic_ctype']


class StorageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = tantalus.models.Storage
        exclude = ['polymorphic_ctype']
    def to_representation(self, obj):
        if isinstance(obj, tantalus.models.ServerStorage):
            return ServerStorageSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, tantalus.models.AzureBlobStorage):
            return AzureBlobStorageSerializer(obj, context=self.context).to_representation(obj)
        return super(StorageSerializer, self).to_representation(obj)


class ServerStorageSerializer(serializers.HyperlinkedModelSerializer):
    # generic_url = serializers.SerializerMethodField(method_name='_get_generic_url')

    class Meta:
        model = tantalus.models.ServerStorage
        exclude = ['polymorphic_ctype']

    def to_representation(self, obj):
        res = super(ServerStorageSerializer, self).to_representation(obj)
        return res




class AzureBlobStorageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = tantalus.models.AzureBlobStorage
        exclude = ['polymorphic_ctype']


class FileInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = tantalus.models.FileInstance
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=tantalus.models.FileInstance.objects.all(),
                fields=('file_resource', 'storage')
            )
        ]


class DeploymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = tantalus.models.Deployment
        fields = '__all__'

    def create(self, validated_data):
        try:
            #remove many2many relationships from validated_data
            datasets = validated_data.pop('datasets', [])
            file_transfers = validated_data.pop('file_transfers', [])

            instance = tantalus.models.Deployment(**validated_data)
            instance.save()
            instance.datasets = datasets
            instance.file_transfers = file_transfers
            start_transfers(instance)
            return instance

        except ValueError as e:
            raise ValidationError(" ".join(e.args), code=None)


class FileTransferSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = tantalus.models.FileTransfer
        fields = '__all__'


