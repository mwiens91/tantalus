"""Forms relating to the GenericTask models."""

from django import forms
from tantalus.generictask_models import GenericTaskType, GenericTaskInstance


class GenericTaskTypeCreateForm(forms.ModelForm):
    """A form to create a GenericTask."""
    class Meta:
        model = GenericTaskType
        fields = ('task_name',
                  'task_script_name',
                  'required_and_default_args',)


class GenericTaskInstanceCreateForm(forms.ModelForm):
    """A form to create a GenericTask."""
    class Meta:
        model = GenericTaskInstance
        fields = ('task_type',
                  'args',)
