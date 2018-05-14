from __future__ import unicode_literals

import json
import os
import django
import django.contrib.postgres.fields
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
import simple_history
from simple_history.models import HistoricalRecords
from polymorphic.models import PolymorphicModel


def create_id_field(*args, **kwargs):
    return models.CharField(
        max_length=50,
        *args,
        **kwargs
    )


class Tag(models.Model):
    """
    Simple text tag associated with datasets.
    """
    
    history = HistoricalRecords()

    name = create_id_field(unique=True)

    def __unicode__(self):
        return self.name


class Sample(models.Model):
    """
    Physical tumour or other tissue sample.
    """

    history = HistoricalRecords()

    sample_id = create_id_field(unique=True)

    def __unicode__(self):
        return self.sample_id

    def get_absolute_url(self):
        return reverse("sample-list")


class DNALibrary(models.Model):
    """
    DNA Library, possibly multiplexed.
    """

    history = HistoricalRecords()

    library_id = create_id_field(unique=True)

    EXOME = 'EXOME'
    WGS = 'WGS'
    RNASEQ = 'RNASEQ'
    SINGLE_CELL_WGS = 'SC_WGS'
    SINGLE_CELL_RNASEQ = 'SC_RNASEQ'
    DNA_AMPLICON = 'DNA_AMPLICON'
    BISULFITE = 'BISULFITE'
    CHIP = 'CHIP'
        
    library_type_choices = (
        (EXOME, 'Bulk Whole Exome Sequence'),
        (WGS, 'Bulk Whole Genome Sequence'),
        (RNASEQ, 'Bulk RNA-Seq'),
        (SINGLE_CELL_WGS, 'Single Cell Whole Genome Sequence'),
        (SINGLE_CELL_RNASEQ, 'Single Cell RNA-Seq'),
        (DNA_AMPLICON, 'Targetted DNA Amplicon Sequence'),
        (BISULFITE, 'Bisulfite Sequence'),
        (CHIP, 'Chromatin Immunoprecipitation Sequence'),
    )

    library_type = models.CharField(
        max_length=50,
        choices=library_type_choices,
    )

    SINGLE_INDEX = 'S'
    DUAL_INDEX = 'D'
    NO_INDEXING = 'N'

    index_format_choices = (
        (SINGLE_INDEX, 'Single Index'),
        (DUAL_INDEX, 'Dual Index (i7 and i5)'),
        (NO_INDEXING, 'No Indexing')
    )

    index_format = models.CharField(
        max_length=50,
        choices=index_format_choices,
    )

    def __unicode__(self):
        return '{}_{}'.format(self.library_type, self.library_id)


class SequenceLane(models.Model):
    """
    Lane of Illumina Sequencing.
    """

    history = HistoricalRecords()

    flowcell_id = create_id_field()

    lane_number_choices = [('', '')] + [(str(a), str(a)) for a in range(1, 10)]

    lane_number = models.CharField(
        max_length=50,
        choices=lane_number_choices,
        blank=True,
    )

    GSC = 'GSC'
    BRC = 'BRC'

    sequencing_centre_choices = (
        (GSC, 'Genome Science Centre'),
        (BRC, 'Biomedical Research Centre'),
    )

    sequencing_centre = models.CharField(
        max_length=50,
        choices=sequencing_centre_choices,
    )

    sequencing_instrument = models.CharField(
        max_length=50,
    )

    PAIRED = 'P'
    SINGLE = 'S'

    read_type_choices = (
        (PAIRED, 'Paired end tags'),
        (SINGLE, 'Single end tags')
    )

    read_type = models.CharField(
        max_length=50,
        choices=read_type_choices,
    )

    def __unicode__(self):
        if self.lane_number == '':
            return '{}_{}'.format(self.sequencing_centre, self.flowcell_id)
        else:
            return '{}_{}_{}'.format(self.sequencing_centre, self.flowcell_id, self.lane_number)

    class Meta:
        unique_together = ('flowcell_id', 'lane_number')


class ReadGroup(models.Model):
    """
    Group of reads from a specific sample, library, lane and index sequence.
    """

    history = HistoricalRecords()

    sample = models.ForeignKey(
        Sample,
        on_delete=models.CASCADE,
    )

    dna_library = models.ForeignKey(
        DNALibrary,
        on_delete=models.CASCADE,
    )

    index_sequence = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    sequence_lane = models.ForeignKey(
        SequenceLane,
        on_delete=models.CASCADE,
    )

    sequencing_library_id = create_id_field(
        null=True,
    )

    class Meta:
        unique_together = ('sample', 'dna_library', 'index_sequence', 'sequence_lane')


class FileResource(models.Model):
    """
    Sequence data file.
    """

    history = HistoricalRecords()

    md5 = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    size = models.BigIntegerField()

    created = models.DateTimeField()

    BAM = 'BAM'
    BAI = 'BAI'
    FQ = 'FQ'

    file_type_choices = (
        (BAM, 'BAM'),
        (BAI, 'BAM Index'),
        (FQ, 'Fastq'),
    )

    file_type = models.CharField(
        max_length=50,
        choices=file_type_choices,
    )

    read_end = models.PositiveSmallIntegerField(
        null=True,
    )

    GZIP = 'GZIP'
    BZIP2 = 'BZIP2'
    UNCOMPRESSED = 'UNCOMPRESSED'

    compression_choices = (
        (GZIP, 'gzip'),
        (BZIP2, 'bzip2'),
        (UNCOMPRESSED, 'uncompressed'),
    )

    compression = models.CharField(
        max_length=50,
        choices=compression_choices,
    )

    filename = models.CharField(
        max_length=500,
        unique=True,
    )

    is_folder = models.BooleanField(
        default=False,
    )

    def __unicode__(self):
        return '{}'.format(self.md5)

    def get_filename_time(self):
        return self.created.strftime('%Y%m%d_%H%M%S')

    def get_filename_uid(self):
        return self.md5[:8]

    def get_compression_suffix(self):
        return {
            self.GZIP: '.gz',
            self.BZIP2: '.bz2',
            self.UNCOMPRESSED: '',
        }[self.compression]


class AbstractDataSet(PolymorphicModel):
    """
    General Sequence Dataset.
    """

    history = HistoricalRecords()

    tags = models.ManyToManyField(Tag)

    read_groups = models.ManyToManyField(
        ReadGroup,
    )
    
    file_resources = models.ManyToManyField(
        FileResource,
        blank=True,
    )

    def get_libraries(self):
        return set([r.dna_library.library_id for r in self.read_groups.all()])

    def get_library_type(self):
        return set([r.dna_library.library_type for r in self.read_groups.all()])

    def get_samples(self):
        return set([r.sample for r in self.read_groups.all()])

    def get_storage_names(self):
        return set([i.storage.name for f in self.get_file_resources() for i in f.fileinstance_set.all()])

    def get_file_resources(self):
        raise NotImplementedError()

    def save(self, *args, **kwargs):
        super(AbstractDataSet, self).save(*args, **kwargs)
        self.file_resources.clear()
        for file_resource in self.get_file_resources():
            self.file_resources.add(file_resource)


class BCLFolder(AbstractDataSet):
    """
    BCL folder.
    """

    history = HistoricalRecords()

    folder = models.OneToOneField(
        FileResource,
        on_delete=models.CASCADE,
        related_name='bcl_folder',
    )

    def get_file_resources(self):
        return [self.folder]


class SingleEndFastqFile(AbstractDataSet):
    """
    Fastq file of single ended Illumina Sequencing.
    """

    history = HistoricalRecords()

    reads_file = models.OneToOneField(
        FileResource,
        on_delete=models.CASCADE,
        related_name='reads_file',
    )

    dataset_type_name = 'Single End FASTQ'

    def __str__(self):
        return "SingleEndFastQ {}".format(self.id)

    def get_file_resources(self):
        return [self.reads_file]


class PairedEndFastqFiles(AbstractDataSet):
    """
    Fastq file of paired ended Illumina Sequencing.
    """

    history = HistoricalRecords()

    reads_1_file = models.ForeignKey(
        FileResource,
        on_delete=models.CASCADE,
        related_name='reads_1_file',
    )

    reads_2_file = models.ForeignKey(
        FileResource,
        on_delete=models.CASCADE,
        related_name='reads_2_file',
    )

    dataset_type_name = 'Paired End FASTQ'

    def __str__(self):
        return "PairedEndFastq {}".format(self.id)

    def get_file_resources(self):
        return [self.reads_1_file, self.reads_2_file]

    class Meta:
        unique_together = ('reads_1_file', 'reads_2_file')


class BamFile(AbstractDataSet):
    """
    Base class of bam files.
    """

    history = HistoricalRecords()

    HG19 = 'HG19'
    HG18 = 'HG18'
    UNALIGNED = 'UNALIGNED'
    UNUSABLE = 'UNUSABLE'

    reference_genome_choices = (
        (HG19, 'Human Genome 19'),
        (HG18, 'Human Genome 18'),
        (UNALIGNED, 'Not aligned to a reference'),
        (UNUSABLE, 'Alignments are not usable'),
    )

    reference_genome = models.CharField(
        max_length=50,
        default=UNALIGNED,
    )

    aligner = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default=None,
    )

    bam_file = models.OneToOneField(
        FileResource,
        on_delete=models.CASCADE,
        related_name='bam_file',
    )

    bam_index_file = models.ForeignKey(
        FileResource,
        on_delete=models.SET_NULL,
        related_name='bam_index_file',
        null=True,
    )

    dataset_type_name = 'BAM'

    def get_file_resources(self):
        if self.bam_index_file is None:
            return [self.bam_file]
        else:
            return [self.bam_file, self.bam_index_file]

    def __str__(self):
        return "BamFile ID: {}".format(self.id)


class Storage(PolymorphicModel):
    """
    Details of a specific file storage location.
    """

    history = HistoricalRecords()

    name = models.CharField(
        max_length=50,
        unique=True,
    )

    def __unicode__(self):
        return '{}'.format(self.name)

    def get_filepath(self, file_resource):
        raise NotImplementedError()

    @property
    def is_read_only(self):
        return False


class ServerStorage(Storage):
    """
    Server file storage for sequence data files.
    """

    history = HistoricalRecords()

    server_ip = models.CharField(
        max_length=50,
    )

    storage_directory = models.CharField(
        max_length=500,
    )

    username = models.CharField(
        max_length=30,
    )

    queue_prefix = models.CharField(
        max_length=50,
    )

    read_only = models.BooleanField(
        default=True,
    )

    def get_storage_directory(self):
        if not django.conf.settings.IS_PRODUCTION and not self.read_only:
            return self.storage_directory.rstrip('/') + '_test'
        return self.storage_directory

    def get_md5_queue_name(self):
        return self.queue_prefix + '.md5'

    def get_db_queue_name(self):
        return self.queue_prefix + '.db'

    def get_filepath(self, file_resource):
        return os.path.join(
            str(self.get_storage_directory()),
            file_resource.filename.strip('/'))

    @property
    def is_read_only(self):
        return self.read_only

    has_transfer_queue = True

    storage_type = 'server'


class AzureBlobCredentials(models.Model):
    """
    Azure blob credentials.
    """

    history = HistoricalRecords()

    storage_key = models.CharField(
        max_length=200,
    )


class AzureBlobStorage(Storage):
    """
    Azure blob storage for sequence files.
    """

    history = HistoricalRecords()

    storage_account = models.CharField(
        max_length=50,
    )

    storage_container = models.CharField(
        max_length=50,
    )

    credentials = models.ForeignKey(
        AzureBlobCredentials,
        on_delete=models.CASCADE,
    )

    def get_storage_container(self):
        if not django.conf.settings.IS_PRODUCTION:
            return self.storage_container + '-test'
        return self.storage_container

    def get_filepath(self, file_resource):
        # strip the slash, otherwise this creates an additional
        # <no name> root folder
        blobname = file_resource.filename.strip('/')
        blobpath = '/'.join([self.get_storage_container(), blobname])
        return blobpath

    has_transfer_queue = False

    storage_type = 'blob'


class FileInstance(models.Model):
    """
    Instance of a file in storage.
    """

    history = HistoricalRecords()

    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE,
    )

    file_resource = models.ForeignKey(
        FileResource,
        on_delete=models.CASCADE,
    )

    filename_override = models.CharField(
        max_length=500,
        blank=True,
        default='',
    )

    def get_filepath(self):
        if self.filename_override is not '':
            return self.filename_override

        return self.storage.get_filepath(self.file_resource)

    class Meta:
        unique_together = ('file_resource', 'storage')


class SimpleTask(models.Model):
    """
    Base model for task run with celery.
    """

    running = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    success = models.BooleanField(default=False)
    stopping = models.BooleanField(default=False)
    state = models.TextField(blank=True)

    def get_queue_name(self):
        raise NotImplementedError()

    def get_absolute_url(self):
        return reverse(self.view)

    class Meta:
        abstract = True


class BRCFastqImport(SimpleTask):
    """
    When given an output dir + metadata, generate fastq files.
    """

    view = 'brcfastqimport-list'

    task_name = 'import_brc_fastqs_into_tantalus'

    output_dir = models.CharField(
        max_length=500,
    )

    storage = models.ForeignKey(
        ServerStorage,
        on_delete=models.CASCADE,
    )

    flowcell_id = models.CharField(
        max_length=50,
    )

    def get_queue_name(self):
        return self.storage.get_db_queue_name()


class FileTransfer(SimpleTask):
    """
    File transfer from one storage to another.
    """

    view = 'filetransfer-list'

    task_name = 'transfer_files'

    name = models.CharField(
        max_length=50,
        unique=True,
    )

    tag_name = models.CharField(
        max_length=50,
    )

    from_storage = models.ForeignKey(
        Storage,
        related_name='filetransfer_from_storage',
    )

    to_storage = models.ForeignKey(
        Storage,
        related_name='filetransfer_to_storage',
    )

    def get_count_total(self):
        return AbstractDataSet.objects.filter(tags__name=self.tag_name).count()

    def get_count_finished(self):
        return AbstractDataSet.objects.filter(tags__name=self.tag_name, file_resources__fileinstance__storage=self.to_storage).distinct().count()

    def get_queue_name(self):
        if self.to_storage.has_transfer_queue:
            return self.to_storage.queue_prefix + '.transfer'
        elif self.from_storage.has_transfer_queue:
            return self.from_storage.queue_prefix + '.transfer'
        else:
            raise Exception('no transfer queue for transfer')

    def __unicode__(self):
        return self.name


class ReservedFileInstance(models.Model):
    """
    Lock on specific file instance being transferred to.
    """

    file_resource = models.ForeignKey(
        FileResource,
        on_delete=models.CASCADE,
    )

    to_storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE,
    )

    file_transfer = models.ForeignKey(
        FileTransfer,
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('file_resource', 'to_storage')


class MD5Check(SimpleTask):
    """
    Check of set MD5 task.
    """

    task_name = 'check_or_update_md5'

    file_instance = models.ForeignKey(
        FileInstance,
    )


class GscWgsBamQuery(SimpleTask):
    """
    Query GSC API for WGS Bam data paths.
    """

    view = 'gscwgsbamquery-list'

    task_name = 'query_gsc_for_wgs_bams'

    library_ids = django.contrib.postgres.fields.ArrayField(
        models.CharField(max_length=50),
    )

    def get_queue_name(self):
        return get_object_or_404(ServerStorage, name='gsc').get_db_queue_name()


class GscDlpPairedFastqQuery(SimpleTask):
    """
    Query GSC API for DLP paired fastq data paths.
    """

    view = 'gscdlppairedfastqquery-list'

    task_name = 'query_gsc_for_dlp_fastqs'

    dlp_library_id = models.CharField(
        max_length=50,
        unique=True,
    )

    gsc_library_id = models.CharField(
        max_length=50,
        unique=True,
    )

    def get_queue_name(self):
        return get_object_or_404(ServerStorage, name='gsc').get_db_queue_name()


class ImportDlpBam(SimpleTask):
    """
    Import BAMs from DLP pipeline.
    """

    view = 'importdlpbam-list'

    task_name = 'import_dlp_bams'

    storage = models.ForeignKey(
        Storage,
    )

    bam_paths = django.contrib.postgres.fields.ArrayField(
        models.CharField(max_length=500),
    )

    def get_queue_name(self):
        if self.storage.has_transfer_queue:
            return self.storage.get_db_queue_name()
        else:
            return get_object_or_404(ServerStorage, name='shahlab').get_db_queue_name()


def return_gen_task_type_arg_default():
    """Essentially a lambda function that returns a dict.

    For technical reasons, we can't use a lambda function in the default
    to the JSON field for GenericTaskType above; but defining a function
    in the module scope works.
    """
    return {'arg1': None, 'arg2': 'default2'}


class GenericTaskType(models.Model):
    """A type of generic task you can perform.

    Comparing this with SimpleTask, the benefits of this are that you
    can run scripts with arbitrary parameters. The negatives are that
    you can't validate the attributes as well as with the SimpleTask
    structure.
    """
    # The name of the generic task type
    task_name = models.CharField(max_length=50,
                                 help_text="The name of the task.")

    # The name of the script used by this generic task type. This needs
    # to be "task_script_name", where the script associated with this
    # task is found at, starting from the root of the repository,
    # tantalus/tantalus/backend/task_scripts/{task_script_name}.py
    task_script_name = models.CharField(
                          max_length=50,
                          help_text=("The name of the task script name,"
                                     " where the name you enter here refers"
                                     " to 'script_name' in the path to the"
                                     " script "
                                     "tantalus/tantalus/backend/task_scripts/"
                                     "{task_script_name}.py, relative to the"
                                     " root of the Tantalus respository."))

    # What arguments the above script requires. Probably the easiest way
    # to use this field is to pass in a dictionary, and let's use that
    # as an example: (Though don't forget the versitility of this field;
    # see
    # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#django.contrib.postgres.fields.JSONField
    # for more details.)
    #
    # To specify the arguments that the above script requires, pass in a
    # dictionary with the argument names as keys and the None type as
    # their corresponding values. E.g.,
    #
    # {'arg1': None, 'arg2': None, 'arg3': None}
    #
    # Any argument not specified when creating an instance of this task
    # type will result in an exception being raised. If you want to
    # provide default values for the arguments such that the task
    # instances will take on the default argument values if they aren't
    # instantiated with the argument, then simply provide the defaults
    # as keys.  E.g., to give a default value to 'arg2', use
    #
    # {'arg1': None, 'arg2': 'default_val', 'arg3': None}
    required_and_default_args = django.contrib.postgres.fields.JSONField(
                                 verbose_name="script arguments",
                                 default=return_gen_task_type_arg_default,
                                 help_text=(
                                    "The arguments that the task requires as"
                                    " a JSON object. Looking at the object as"
                                    " a dictionary, the keys are the argument"
                                    " names and the corresponding values are"
                                    " the default values for these arguments."
                                    " To specify no default argument, simply"
                                    " use 'null' as the value."),
                                 null=True,
                                 blank=True,)


class GenericTaskInstance(models.Model):
    """An instance of a generic task type."""
    # The type of task that this is
    task_type = models.ForeignKey(GenericTaskType)

    # What arguments the script for this task should be called with.
    # These will be validated in the function
    # validate_generic_task_instance_args right after instantiating an
    # instance of the task.
    args = django.contrib.postgres.fields.JSONField(default=dict,
                                                    null=True,
                                                    blank=True,)

    # Job state parameters. These variables conform to the SimpleTask
    # state representation structure.
    running = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    success = models.BooleanField(default=False)
    stopping = models.BooleanField(default=False)
    state = models.TextField(blank=True)

    # NOTE what the hell is this method for?
    def get_queue_name(self):
        raise NotImplementedError()


class ScaryException(Exception):
    pass


@receiver(pre_save, sender=GenericTaskInstance)
def validate_generic_task_instance_args(instance, **_):
    """Validate a GenericTaskInstance against its task types.

    Check that each argument in the instance has the arguments required
    in the task type. If an argument in the instance is missing and a
    default exists in task type, then add in missing argument from the
    instance with the default from its task type; otherwise throw an
    exception

    This is called before each GenericTaskInstance is saved.

    Arg:
        instance: The GenericTaskInstance just about to be saved.
    Raises:
        A terrible exception (TODO determine this exception type) if the
        instance fails to validate.
    """
    # Un-JSONize the task and instance arguments
    task_type_args_dict = json.loads(
                            instance.task_types.required_and_default_args)
    task_instance_args_dict = json.loads(instance.args)

    # Confirm that the instance arguments is a subset of the task type
    # arguments
    if not set(task_type_args_dict).issubset(set(task_instance_args_dict)):
        # The task instance has unrecognized arguments
        raise ScaryException

    # Now go through each argument from the type and make sure the
    # instance has a value
    for arg, value in task_type_args_dict:
        if arg not in task_instance_args_dict.keys():
            # Argument is missing from instance. If the task type has a
            # default value use that; otherwise, raise an exception.
            if value:
                # Use the default provided by the task type
                task_instance_args_dict[arg] = value
            else:
                # Instance is missing required argument
                raise ScaryException

    # Store any tacked on arguments to the instance
    instance.args = json.dumps(task_instance_args_dict)
