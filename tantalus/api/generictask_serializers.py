"""Serializers relating to the GenericTask models."""

from rest_framework import serializers
from tantalus.generictask_models import GenericTaskType, GenericTaskInstance


class GenericTaskTypeSerializer(serializers.ModelSerializer):
    """A serializer for a generic task type."""
    class Meta:
        model = GenericTaskType
        fields = ('task_name',
                  'task_script_name',
                  'default_host',
                  'required_and_default_args',)
