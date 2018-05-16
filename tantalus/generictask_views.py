"""Views relating to the GenericTask models."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, render
from tantalus.generictask_forms import (GenericTaskTypeCreateForm,
                                        GenericTaskInstanceCreateForm,)
from tantalus.generictask_models import GenericTaskType, GenericTaskInstance


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
            msg = ("Successfully created generic task type %s."
                                                % instance.task_name)
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
    """A view to delete GenericTaskTypes."""
    def get(self, request, pk):
        # Delete the Task Type
        get_object_or_404(GenericTaskType, pk=pk).delete()

        # Log a message
        msg = "Successfully deleted the generic task type."
        messages.success(request, msg)

        return HttpResponseRedirect(reverse('generictasktype-list'))


class GenericTaskInstanceSubMenuView(TemplateView):
    """A submenu to specify which types of instances to view.

    This gives is similar to the GenericTaskTypeListView, except
    clicking on a generic task type here will give you a list of its
    corresponding instances.
    """
    template_name = 'tantalus/generictaskinstance_submenu.html'

    def get_context_data(self):
        return {'tasktypes': GenericTaskType.objects.all()}


class GenericTaskInstanceListView(TemplateView):
    """A view to list instances of a given task type."""
    template_name = 'tantalus/generictaskinstance_list.html'

    def get(self, request, task_type_pk):
        # Get the task type we need the instances of
        task_type = GenericTaskType.objects.get(pk=task_type_pk)

        # Get the instances
        instances = task_type.generictaskinstance_set.all()

        # Build up the context
        context = {'task_type': task_type,
                   'instances': instances,}

        # Render the context
        return render(request, self.template_name, context)


class GenericTaskInstanceCreateView(LoginRequiredMixin, TemplateView):
    """A view to create GenericTaskInstances."""
    template_name = 'tantalus/generictaskinstance_create.html'

    def get(self, request, task_type_pk):
        """Resolves a GET."""
        # Get the task type for this instance
        task_type = GenericTaskType.objects.get(pk=task_type_pk)

        # Create a form
        form = GenericTaskInstanceCreateForm(
                    default_host=task_type.default_host,
                    task_args=task_type.required_and_default_args)

        # Create the context
        context = {'form': form,
                   'task_type': task_type,}

        # Render the context
        return render(request, self.template_name, context)

    def post(self, request, task_type_pk):
        """Resolves a POST."""
        # Get the task type for this instance
        task_type = GenericTaskType.objects.get(pk=task_type_pk)

        # The form
        form = GenericTaskInstanceCreateForm(
                    request.POST,
                    default_host=task_type.default_host,
                    task_args=task_type.required_and_default_args)

        if form.is_valid():
            # Success! Get the name of the instance
            instance_name = form.cleaned_data['instance_name']

            # Get the host of the instance
            host = form.cleaned_data['host']

            # Get all of the instance arguments and put them into a
            # dictionary
            arg_dict = dict()

            for arg, value in form.yield_task_args():
                arg_dict[arg] = value

            # Build the instance and save it
            instance = GenericTaskInstance(task_type=task_type,
                                           instance_name=instance_name,
                                           host=host,
                                           args=arg_dict)
            instance.save()

            # Log a message
            msg = "Successfully created %s instance %s." % (
                                                           task_type.task_name,
                                                           instance_name)
            messages.success(request, msg)

            return HttpResponseRedirect(reverse('generictaskinstance-list',
                                                args=(task_type_pk,)))
        else:
            # Not success!
            msg = ("Failed to create the " + task_type.task_name + " instance."
                             " Please fix the errors below.")
            messages.error(request, msg)
        # Return the invalid form
        return render(request, self.template_name, {'form': form})


class GenericTaskInstanceDetailView(TemplateView):
    """A view to see a specific GenericTaskInstance.

    This will need to be updated once the Celery hooks are in. What's
    here is a placeholder until then.
    """
    template_name = 'tantalus/generictaskinstance_detail.html'

    def get(self, request, task_type_pk, instance_pk):
        # Build the context
        task_type = GenericTaskType.objects.get(pk=task_type_pk)
        instance = GenericTaskInstance.objects.get(pk=instance_pk)
        context = {'task_type': task_type,
                   'instance': instance,}

        # Render the context
        return render(request, self.template_name, context)


class GenericTaskInstanceDeleteView(LoginRequiredMixin, View):
    """A view to delete GenericTaskInstances."""
    def get(self, request, task_type_pk, instance_pk):
        # Delete the instance
        get_object_or_404(GenericTaskInstance, pk=instance_pk).delete()

        # Log a message
        msg = "Successfully deleted the generic task instance."
        messages.success(request, msg)

        return HttpResponseRedirect(reverse('generictaskinstance-list',
                                            args=(task_type_pk,)))


class GenericTaskInstanceRestartView(LoginRequiredMixin, View):
    """A view to restart GenericTaskInstances."""
    def get(self, request, task_type_pk, instance_pk):
        # Get the instance
        instance = get_object_or_404(GenericTaskInstance, pk=instance_pk)

        # Start the task
        if not instance.running:
            # Change the state
            instance.state = (instance.task_nametask_name.replace('_', ' ')
                              + ' queued')
            instance.save()

            # Restart the job
            instance.start_task()

            # Log a message
            msg = ("Successfully restarted the " + instance.task_type.task_name
                   + " instance " + instance.instance_name + ".")
            messages.success(request, msg)
        else:
            # Don't restart if the task is already running. Log a
            # message.
            msg = ("The " + self.instance.task_type.task_name
                   + " instance " + instance.instance_name
                   + "is already running.")
            messages.warning(request, msg)

        # Render the instance detail page
        return HttpResponseRedirect(reverse('generictaskinstance-detail',
                                            args=(task_type_pk,
                                                  instance_pk)))


class GenericTaskInstanceStopView(LoginRequiredMixin, View):
    """A view to stop GenericTaskInstances."""
    def get(self, request, task_type_pk, instance_pk):
        # Get the instance
        instance = get_object_or_404(GenericTaskInstance, pk=instance_pk)

        # Stop the task
        if not instance.stopping:
            # Set the stopping signal to true
            instance.stopping = True
            instance.save()

            # Log a message
            msg = ("Stopping the " + instance.task_type.task_name
                   + " instance " + instance.instance_name + ".")
            messages.success(request, msg)
        else:
            # The job is already stopping
            msg = ("The " + self.instance.task_type.task_name
                   + " instance " + instance.instance_name
                   + "is already stopping.")
            messages.warning(request, msg)

        # Render the instance detail page
        return HttpResponseRedirect(reverse('generictaskinstance-detail',
                                            args=(task_type_pk,
                                                  instance_pk)))
