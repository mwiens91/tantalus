"""Views for the API relating to the GenericTask models."""

from rest_framework import viewsets
from tantalus.api.generictask_serializers import GenericTaskTypeSerializer
from tantalus.generictask_models import GenericTaskType


class GenericTaskTypeViewSet(viewsets.ModelViewSet):
    """A viewset for generic task types."""
    queryset = GenericTaskType.objects.all()
    serializer_class = GenericTaskTypeSerializer