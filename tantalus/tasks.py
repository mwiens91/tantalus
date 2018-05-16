from __future__ import absolute_import

import os
import errno
import subprocess
import time
import signal
import django
import tantalus.models
from celery import shared_task


def simple_task_wrapper(id_, model):
    log_dir = os.path.join(django.conf.settings.TASK_LOG_DIRECTORY, model.task_name, str(id_))

    try:
        os.makedirs(log_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    stdout_filename = os.path.join(log_dir, 'stdout.txt')
    stderr_filename = os.path.join(log_dir, 'stderr.txt')

    with open(stdout_filename, 'a', 0) as stdout_file, open(stderr_filename, 'a', 0) as stderr_file:
        script = os.path.join(django.conf.settings.BASE_DIR, 'tantalus', 'backend', 'task_scripts', model.task_name + '.py')

        task = subprocess.Popen(['python', '-u', script, str(id_)], stdout=stdout_file, stderr=stderr_file)

        stdout_file.write('!! Started task process with id {} !!\n'.format(task.pid))
        stderr_file.write('!! Started task process with id {} !!\n'.format(task.pid))

        while task.poll() is None:
            time.sleep(10)

            if model.objects.get(pk=id_).stopping == True:
                stderr_file.write('!! Sending interrupt to task process !!\n')
                task.send_signal(signal.SIGINT)
                time.sleep(60)

                if task.poll() is None:
                    stderr_file.write('!! Sending kill to task process !!\n')
                    task.kill()

                model_instance = model.objects.get(pk=id_)
                model_instance.stopping = False
                model_instance.running = False
                model_instance.finished = True
                model_instance.save()

        stdout_file.write('!! Finished task process with id {} !!\n'.format(task.pid))
        stderr_file.write('!! Finished task process with id {} !!\n'.format(task.pid))


@shared_task
def transfer_files_task(file_transfer_id):
    simple_task_wrapper(
        id_=file_transfer_id,
        model=tantalus.models.FileTransfer,
    )


@shared_task
def check_md5_task(md5_check_id):
    simple_task_wrapper(
        id_=md5_check_id,
        model=tantalus.models.MD5Check,
    )


@shared_task
def query_gsc_wgs_bams_task(query_id):
    simple_task_wrapper(
        id_=query_id,
        model=tantalus.models.GscWgsBamQuery,
    )


@shared_task
def query_gsc_dlp_paired_fastqs_task(query_id):
    simple_task_wrapper(
        id_=query_id,
        model=tantalus.models.GscDlpPairedFastqQuery,
    )


@shared_task
def import_brc_fastqs_task(query_id):
    simple_task_wrapper(
        id_=query_id,
        model=tantalus.models.BRCFastqImport,
    )


@shared_task
def import_dlp_bams_task(query_id):
    simple_task_wrapper(
        id_=query_id,
        model=tantalus.models.ImportDlpBam,
    )


def get_log_path_for_generic_task_instance(instance, logfile=None):
    """Gets the log path for a generic task intance.

    The path is $TASK_LOG_DIRECTORY/task_type/instance_pk/{logfile}.txt.
    If logfile is None or an empty string, then this function returns
    the log directory path.
    """
    # Get path for log directory
    log_dir = os.path.join(django.conf.settings.TASK_LOG_DIRECTORY,
                           instance.task_type.task_name,
                           str(instance.pk),)

    if logfile:
        # Return the specific log file path
        return os.path.join(log_dir, logfile + '.txt')
    else:
        # Return the log directory path
        return log_dir


@shared_task
def start_generic_task_instance(instance):
    """Start a generic task instance.

    This is *very* similar to the simple_task_wrapper function at the
    top of this module, and is different only in that it accomodates the
    GenericTask model structure (which simple_task_wrapper can't
    accomodate).
    """
    # Get the log directory, and create it if it doesn't exist
    log_dir = get_log_path_for_generic_task_instance(instance)

    try:
        # Make the directory
        os.makedirs(log_dir)
    except OSError as e:
        # Only allow exceptions raised due to the directory already
        # existing; otherwise, pass along the original exception.
        if e.errno != errno.EEXIST:
            raise

    # File paths for stdout and stderr
    stdout_filename = get_log_path_for_generic_task_instance(instance,
                                                             'stdout')
    stdout_filename = get_log_path_for_generic_task_instance(instance,
                                                             'stderr')

    # Start the script
    with open(stdout_filename, 'a', 0) as stdout_file,\
         open(stderr_filename, 'a', 0) as stderr_file:

        # Get the script path
        script_path = os.path.join(django.conf.settings.BASE_DIR,
                                   'tantalus',
                                   'backend',
                                   'task_scripts',
                                   instance.task_type.task_script_name + '.py')

        # Start the task
        task = subprocess.Popen(['python',
                                 '-u',              # force unbuffered output
                                 script,            # script path
                                 str(instance.pk)   # instance pk as only argument
                                 ],
                                 stdout=stdout_file,
                                 stderr=stderr_file)

        # Write a start message to both stdout and stderr
        start_message = "!! Started task process with id {} !!\n".format(task.pid)
        stdout_file.write(start_message)
        stderr_file.write(start_message)

        # Listen for stop signals every 10 seconds while the task is in
        # progress
        while task.poll() is None:
            # Wait
            time.sleep(10)

            if instance.stopping == True:
                # Stop message received. Ask the job nicely to stop and
                # give it a minute to do so.
                stderr_file.write("!! Sending interrupt to task process !!\n")
                task.send_signal(signal.SIGINT)
                time.sleep(60)

                if task.poll() is None:
                    # The job is still running and has either ignored
                    # our request to stop or is taking to long. Kill the
                    # task
                    stderr_file.write("!! Sending kill to task process !!\n")
                    task.kill()

                instance.stopping = False
                instance.running = False
                instance.finished = True
                instance.save()

        # Write a completion message to both stdout and stderr
        done_message = "!! Finished task process with id {} !!\n".format(task.pid)
        stdout_file.write(done_message)
        stderr_file.write(done_message)
