"""Forms relating to the GenericTask models."""

from django import forms
from django.utils.safestring import mark_safe
from tantalus.generictask_models import GenericTaskType, GenericTaskInstance


class GenericTaskTypeCreateForm(forms.ModelForm):
    """A form to create a GenericTask."""
    class Meta:
        model = GenericTaskType
        fields = ('task_name',
                  'task_script_name',
                  'default_host',
                  'required_and_default_args',)


class GenericTaskInstanceCreateForm(forms.Form):
    """A form to create a GenericTask.

    This requires some extra processing be done in view in which this is
    instantiated, both for creating and validating the form.
    """
    instance_name = forms.CharField(max_length=50,
                                    help_text="The name of the instance.",)

    def __init__(self, *args, **kwargs):
        """Create argument fields specific to the task type.

        Expects the arguments dictionary to be included in the keyword
        arguments with key 'task_args'.
        """
        # Get the arguments and call the parent constructor
        task_args = kwargs.pop('task_args')
        super(GenericTaskInstanceCreateForm, self).__init__(*args, **kwargs)

        # Create fields for each of the task arguments
        for i, task_arg in enumerate(task_args.iteritems(), 1):
            # Create the 'required' setting and appropriate help text
            if task_arg[1]:
                # There's a default
                help_text = mark_safe(
                    'Defaults to <code>%s</code> if left blank' % task_arg[1])
                required_setting = False
            else:
                help_text = 'This is a required argument'
                required_setting = True

            # Create the field
            self.fields['task_arg_%s' % i] = forms.CharField(
                                                    required=required_setting,
                                                    label=task_arg[0],
                                                    widget=forms.Textarea(
                                                            attrs={'rows': 4}),
                                                    help_text=help_text)

    def clean(self):
        """Remove args that have been left blank.

        A hook that runs prior to saving a model will add in the
        defaults, provided those defaults exit. The condition they check
        for argument existence is existence of the argument key, which
        is what we need to remove in this function for the hook to
        operate as expected.
        """
        # Get the cleaned data from the parent's version of this
        # function
        cleaned_data = super(GenericTaskInstanceCreateForm, self).clean()

        # Remove any arguments with empty strings
        for key in cleaned_data.keys():
            if key.startswith('task_arg_') and not cleaned_data[key]:
                # Remove the argument
                del cleaned_data[key]
        return cleaned_data

    def yield_task_args(self):
        """Yields the task arguments and values as 2-tuples."""
        # Find the task arguments
        for name, value in self.cleaned_data.items():
            if name.startswith('task_arg_'):
                # Yield the 2-tuple
                yield (self.fields[name].label, value)
