"""GenericTask models and related functions."""

import json
import django.contrib.postgres.fields
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


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
                                 unique=True,
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

    # A name for the task instance
    instance_name = models.CharField(max_length=50,
                                     unique=True,
                                     help_text="The name for the instance.")

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
