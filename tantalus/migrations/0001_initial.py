# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-19 17:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0003_historicaltag'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractFileSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('running', models.BooleanField(default=False, verbose_name='Running')),
                ('finished', models.BooleanField(default=False, verbose_name='Finished')),
                ('errors', models.BooleanField(default=False, verbose_name='Errors')),
            ],
        ),
        migrations.CreateModel(
            name='DNALibrary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('library_id', models.CharField(max_length=50, unique=True)),
                ('library_type', models.CharField(choices=[('EXOME', 'Bulk Whole Exome Sequence'), ('WGS', 'Bulk Whole Genome Sequence'), ('RNASEQ', 'Bulk RNA-Seq'), ('SC_WGS', 'Single Cell Whole Genome Sequence'), ('SC_RNASEQ', 'Single Cell RNA-Seq')], max_length=50)),
                ('index_format', models.CharField(choices=[('S', 'Single Index'), ('D', 'Dual Index (i7 and i5)'), ('N', 'No Indexing')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='DNASequences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_sequence', models.CharField(blank=True, max_length=50, null=True)),
                ('dna_library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tantalus.DNALibrary')),
            ],
        ),
        migrations.CreateModel(
            name='FileInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='FileResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('md5', models.CharField(max_length=50, unique=True)),
                ('size', models.BigIntegerField()),
                ('created', models.DateTimeField()),
                ('file_type', models.CharField(choices=[('BAM', 'BAM'), ('BAI', 'BAM Index'), ('FQ', 'Fastq')], max_length=50)),
                ('compression', models.CharField(choices=[('GZIP', 'gzip'), ('BZIP2', 'bzip2'), ('UNCOMPRESSED', 'uncompressed')], max_length=50)),
                ('filename', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='FileTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_filename', models.CharField(max_length=500)),
                ('progress', models.FloatField(default=0.0)),
                ('running', models.BooleanField(default=False, verbose_name='Running')),
                ('finished', models.BooleanField(default=False, verbose_name='Finished')),
                ('success', models.BooleanField(default=False, verbose_name='Success')),
                ('file_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tantalus.FileInstance')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalAbstractFileSet',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('dna_sequences', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.DNASequences')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('polymorphic_ctype', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical abstract file set',
            },
        ),
        migrations.CreateModel(
            name='HistoricalAzureBlobStorage',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('storage_account', models.CharField(max_length=50)),
                ('storage_container', models.CharField(max_length=50)),
                ('storage_key', models.CharField(max_length=200)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('polymorphic_ctype', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical azure blob storage',
            },
        ),
        migrations.CreateModel(
            name='HistoricalBamFile',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('reference_genome', models.CharField(choices=[('hg19', 'Human Genome 19'), ('hg18', 'Human Genome 18'), ('none', 'Unaligned')], max_length=50)),
                ('aligner', models.CharField(max_length=50)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical bam file',
            },
        ),
        migrations.CreateModel(
            name='HistoricalDNALibrary',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('library_id', models.CharField(db_index=True, max_length=50)),
                ('library_type', models.CharField(choices=[('EXOME', 'Bulk Whole Exome Sequence'), ('WGS', 'Bulk Whole Genome Sequence'), ('RNASEQ', 'Bulk RNA-Seq'), ('SC_WGS', 'Single Cell Whole Genome Sequence'), ('SC_RNASEQ', 'Single Cell RNA-Seq')], max_length=50)),
                ('index_format', models.CharField(choices=[('S', 'Single Index'), ('D', 'Dual Index (i7 and i5)'), ('N', 'No Indexing')], max_length=50)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical dna library',
            },
        ),
        migrations.CreateModel(
            name='HistoricalDNASequences',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('index_sequence', models.CharField(blank=True, max_length=50, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('dna_library', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.DNALibrary')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical dna sequences',
            },
        ),
        migrations.CreateModel(
            name='HistoricalFileInstance',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('file_resource', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.FileResource')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical file instance',
            },
        ),
        migrations.CreateModel(
            name='HistoricalFileResource',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('md5', models.CharField(db_index=True, max_length=50)),
                ('size', models.BigIntegerField()),
                ('created', models.DateTimeField()),
                ('file_type', models.CharField(choices=[('BAM', 'BAM'), ('BAI', 'BAM Index'), ('FQ', 'Fastq')], max_length=50)),
                ('compression', models.CharField(choices=[('GZIP', 'gzip'), ('BZIP2', 'bzip2'), ('UNCOMPRESSED', 'uncompressed')], max_length=50)),
                ('filename', models.CharField(max_length=500)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical file resource',
            },
        ),
        migrations.CreateModel(
            name='HistoricalPairedEndFastqFiles',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical paired end fastq files',
            },
        ),
        migrations.CreateModel(
            name='HistoricalSample',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('sample_id_space', models.CharField(choices=[('SA', 'Aparicio'), ('DG', 'Huntsman'), ('O', 'Other')], max_length=50)),
                ('sample_id', models.CharField(db_index=True, max_length=50)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical sample',
            },
        ),
        migrations.CreateModel(
            name='HistoricalSequenceLane',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('flowcell_id', models.CharField(max_length=50)),
                ('lane_number', models.PositiveSmallIntegerField()),
                ('sequencing_centre', models.CharField(max_length=50)),
                ('sequencing_library_id', models.CharField(max_length=50)),
                ('sequencing_instrument', models.CharField(choices=[('HX', 'HiSeqX'), ('H2500', 'HiSeq2500'), ('N550', 'NextSeq550'), ('MI', 'MiSeq'), ('O', 'other')], max_length=50)),
                ('read_type', models.CharField(choices=[('P', 'PET'), ('S', 'SET')], max_length=50)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('dna_library', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.DNALibrary')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical sequence lane',
            },
        ),
        migrations.CreateModel(
            name='HistoricalServerStorage',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('server_ip', models.CharField(max_length=50)),
                ('storage_directory', models.CharField(max_length=500)),
                ('username', models.CharField(max_length=30)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('polymorphic_ctype', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical server storage',
            },
        ),
        migrations.CreateModel(
            name='HistoricalSingleEndFastqFile',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical single end fastq file',
            },
        ),
        migrations.CreateModel(
            name='HistoricalStorage',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('polymorphic_ctype', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical storage',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_id_space', models.CharField(choices=[('SA', 'Aparicio'), ('DG', 'Huntsman'), ('O', 'Other')], max_length=50)),
                ('sample_id', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SequenceLane',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flowcell_id', models.CharField(max_length=50)),
                ('lane_number', models.PositiveSmallIntegerField()),
                ('sequencing_centre', models.CharField(max_length=50)),
                ('sequencing_library_id', models.CharField(max_length=50)),
                ('sequencing_instrument', models.CharField(choices=[('HX', 'HiSeqX'), ('H2500', 'HiSeq2500'), ('N550', 'NextSeq550'), ('MI', 'MiSeq'), ('O', 'other')], max_length=50)),
                ('read_type', models.CharField(choices=[('P', 'PET'), ('S', 'SET')], max_length=50)),
                ('dna_library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tantalus.DNALibrary')),
            ],
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AzureBlobStorage',
            fields=[
                ('storage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tantalus.Storage')),
                ('storage_account', models.CharField(max_length=50)),
                ('storage_container', models.CharField(max_length=50)),
                ('storage_key', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=('tantalus.storage',),
        ),
        migrations.CreateModel(
            name='BamFile',
            fields=[
                ('abstractfileset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tantalus.AbstractFileSet')),
                ('reference_genome', models.CharField(choices=[('hg19', 'Human Genome 19'), ('hg18', 'Human Genome 18'), ('none', 'Unaligned')], max_length=50)),
                ('aligner', models.CharField(max_length=50)),
                ('bam_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bam_file', to='tantalus.FileResource')),
                ('bam_index_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bam_index_file', to='tantalus.FileResource')),
            ],
            bases=('tantalus.abstractfileset',),
        ),
        migrations.CreateModel(
            name='PairedEndFastqFiles',
            fields=[
                ('abstractfileset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tantalus.AbstractFileSet')),
                ('reads_1_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reads_1_file', to='tantalus.FileResource')),
                ('reads_2_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reads_2_file', to='tantalus.FileResource')),
            ],
            bases=('tantalus.abstractfileset',),
        ),
        migrations.CreateModel(
            name='ServerStorage',
            fields=[
                ('storage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tantalus.Storage')),
                ('server_ip', models.CharField(max_length=50)),
                ('storage_directory', models.CharField(max_length=500)),
                ('username', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=('tantalus.storage',),
        ),
        migrations.CreateModel(
            name='SingleEndFastqFile',
            fields=[
                ('abstractfileset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tantalus.AbstractFileSet')),
                ('reads_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reads_file', to='tantalus.FileResource')),
            ],
            options={
                'abstract': False,
            },
            bases=('tantalus.abstractfileset',),
        ),
        migrations.AddField(
            model_name='storage',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_tantalus.storage_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='historicalsingleendfastqfile',
            name='abstractfileset_ptr',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.AbstractFileSet'),
        ),
        migrations.AddField(
            model_name='historicalsingleendfastqfile',
            name='dna_sequences',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.DNASequences'),
        ),
        migrations.AddField(
            model_name='historicalsingleendfastqfile',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalsingleendfastqfile',
            name='polymorphic_ctype',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='historicalsingleendfastqfile',
            name='reads_file',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.FileResource'),
        ),
        migrations.AddField(
            model_name='historicalserverstorage',
            name='storage_ptr',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.Storage'),
        ),
        migrations.AddField(
            model_name='historicalpairedendfastqfiles',
            name='abstractfileset_ptr',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.AbstractFileSet'),
        ),
        migrations.AddField(
            model_name='historicalpairedendfastqfiles',
            name='dna_sequences',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.DNASequences'),
        ),
        migrations.AddField(
            model_name='historicalpairedendfastqfiles',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalpairedendfastqfiles',
            name='polymorphic_ctype',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='historicalpairedendfastqfiles',
            name='reads_1_file',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.FileResource'),
        ),
        migrations.AddField(
            model_name='historicalpairedendfastqfiles',
            name='reads_2_file',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.FileResource'),
        ),
        migrations.AddField(
            model_name='historicalfileinstance',
            name='storage',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.Storage'),
        ),
        migrations.AddField(
            model_name='historicaldnasequences',
            name='sample',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.Sample'),
        ),
        migrations.AddField(
            model_name='historicalbamfile',
            name='abstractfileset_ptr',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.AbstractFileSet'),
        ),
        migrations.AddField(
            model_name='historicalbamfile',
            name='bam_file',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.FileResource'),
        ),
        migrations.AddField(
            model_name='historicalbamfile',
            name='bam_index_file',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.FileResource'),
        ),
        migrations.AddField(
            model_name='historicalbamfile',
            name='dna_sequences',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.DNASequences'),
        ),
        migrations.AddField(
            model_name='historicalbamfile',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalbamfile',
            name='polymorphic_ctype',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='historicalazureblobstorage',
            name='storage_ptr',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tantalus.Storage'),
        ),
        migrations.AddField(
            model_name='filetransfer',
            name='from_storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_transfer_from_storage', to='tantalus.Storage'),
        ),
        migrations.AddField(
            model_name='filetransfer',
            name='to_storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_transfer_to_storage', to='tantalus.Storage'),
        ),
        migrations.AddField(
            model_name='fileinstance',
            name='file_resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tantalus.FileResource'),
        ),
        migrations.AddField(
            model_name='fileinstance',
            name='storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tantalus.Storage'),
        ),
        migrations.AddField(
            model_name='dnasequences',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tantalus.Sample'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='datasets',
            field=models.ManyToManyField(to='tantalus.AbstractFileSet'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='file_transfers',
            field=models.ManyToManyField(blank=True, to='tantalus.FileTransfer'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='from_storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deployment_from_storage', to='tantalus.Storage'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='to_storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deployment_to_storage', to='tantalus.Storage'),
        ),
        migrations.AddField(
            model_name='abstractfileset',
            name='dna_sequences',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tantalus.DNASequences'),
        ),
        migrations.AddField(
            model_name='abstractfileset',
            name='lanes',
            field=models.ManyToManyField(to='tantalus.SequenceLane', verbose_name='Lanes'),
        ),
        migrations.AddField(
            model_name='abstractfileset',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_tantalus.abstractfileset_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='abstractfileset',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterUniqueTogether(
            name='sequencelane',
            unique_together=set([('flowcell_id', 'lane_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='fileinstance',
            unique_together=set([('file_resource', 'storage')]),
        ),
        migrations.AlterUniqueTogether(
            name='dnasequences',
            unique_together=set([('dna_library', 'index_sequence')]),
        ),
        migrations.AlterUniqueTogether(
            name='pairedendfastqfiles',
            unique_together=set([('reads_1_file', 'reads_2_file')]),
        ),
        migrations.AlterUniqueTogether(
            name='bamfile',
            unique_together=set([('bam_file', 'bam_index_file')]),
        ),
    ]
