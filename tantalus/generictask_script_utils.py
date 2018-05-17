"""Functions for running scripts associated with GenericTasks."""

import errno
import os
import signal
import subprocess
import time
import celery
import django.conf


def get_script_path_for_generic_task_type(task_type):
    """Gets the script path for a generic task type.

    The path is
    $DJANGO_BASE_DIR/tantalus/backend/generic_task_scripts/script.py.
    """
    return os.path.join(django.conf.settings.BASE_DIR,
                        'tantalus',
                        'backend',
                        'generic_task_scripts',
                        task_type.task_script_name + '.py')


def get_log_path_for_generic_task_instance(instance, logfile=None):
    """Gets the log path for a generic task intance.

    The path is $TASK_LOG_DIRECTORY/task_type/instance_pk/{logfile}.txt.
    If logfile is None or an empty string, then this function returns
    the log directory path.
    """
    # Escape the task name
    escaped_task_name = instance.task_type.task_name.replace(" ", "-")

    # Get path for log directory
    log_dir = os.path.join(django.conf.settings.TASK_LOG_DIRECTORY,
                           escaped_task_name,
                           str(instance.pk),)

    if logfile:
        # Return the specific log file path
        return os.path.join(log_dir, logfile + '.txt')

    # Return the log directory path
    return log_dir


@celery.shared_task
def start_generic_task_instance(instance):
    """Start a generic task instance.

    This is *very* similar to the simple_task_wrapper function in the
    tasks module, and is different only in that it accomodates the
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
    stderr_filename = get_log_path_for_generic_task_instance(instance,
                                                             'stderr')

    # Start the script
    with open(stdout_filename, 'a', 0) as stdout_file,\
         open(stderr_filename, 'a', 0) as stderr_file:

        # Get the script path
        script_path = get_script_path_for_generic_task_type(instance.task_type)

        # Start the task
        task = subprocess.Popen(['python',
                                 '-u',              # force unbuffered output
                                 script_path,       # script path
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

            if instance.stopping:
                # Stop message received. Ask the job nicely to stop and
                # give it a minute to do so.
                stderr_file.write("!! Sending interrupt to task process !!\n")
                task.send_signal(signal.SIGINT)
                time.sleep(60)

                if task.poll() is None:
                    # The job is still running and has either ignored
                    # our request to stop or is taking to long. Kill the
                    # task.
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
