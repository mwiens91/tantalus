"""Views relating to the GenericTask models."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, render
from tantalus.forms import GenericTaskTypeCreateForm
from tantalus.models import GenericTaskType


class GenericTaskTypeListView(TemplateView):
    """A view to list GenericTaskTypes."""
    template_name = 'tantalus/generictasktype_list.html'

    def get_context_data(self):
        return {'tasktypes': GenericTaskType.objects.all()}


class GenericTaskTypeCreateView(LoginRequiredMixin, TemplateView):
    """A view to create GenericTaskTypes."""
    template_name = 'tantalus/generictasktype_create.html'

    def get(self, request):
        """Resolves a GET."""
        form = GenericTaskTypeCreateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Resolves a POST."""
        form = GenericTaskTypeCreateForm(request.POST)
        if form.is_valid():
            # Success!
            instance = form.save()

            # Log a message
            msg = "Successfully created generic task type %s." % instance.task_name
            messages.success(request, msg)

            return HttpResponseRedirect(reverse('generictasktype-list'))
        else:
            # Not success!
            msg = ("Failed to create the generic task type."
                   " Please fix the errors below.")
            messages.error(request, msg)
        # Return the invalid form
        return render(request, self.template_name, {'form': form})


class GenericTaskTypeDetailView(DetailView):
    """A view to see a specific GenericTaskType."""
    template_name = 'tantalus/generictasktype_detail.html'
    model = GenericTaskType


class GenericTaskTypeDeleteView(LoginRequiredMixin, View):
    """A view to create GenericTaskTypes."""
    def get(self, request, pk):
        # Delete the Task Type
        get_object_or_404(GenericTaskType, pk=pk).delete()

        # Log a message
        msg = "Successfully deleted the generic task type."
        messages.success(request, msg)

        return HttpResponseRedirect(reverse('generictasktype-list'))
