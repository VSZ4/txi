import mimetypes
from wsgiref.util import FileWrapper

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from labworks.models import Lab
from tasks.models import Task
from .forms import LabForm
from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import user_passes_test


class LabListView(ListView):
    model = Lab


def user_check(user):
    if user.groups.filter(name__in=['Students']) or user.groups.filter(name__in=['Teachers']) or user.is_superuser:
        return True
    else:
        return False


def student_check(user):
    if user.groups.filter(name__in=['Students']):
        return True
    else:
        return False


def admin_check(user):
    if user.groups.filter(name__in=['Teachers']) or user.is_superuser:
        return True
    else:
        return False


@user_passes_test(student_check)
def create(request, task_id):
    if request.method == "POST":
        form = LabForm(request.POST, request.FILES)
        if form.is_valid():
            labwork = form.save(commit=False)
            labwork.author = request.user
            labwork.task = Task.objects.get(id=task_id)
            labwork.save()
            return redirect(reverse('taskDetail', args=[task_id]))
    else:
        form = LabForm()
    return render(request, 'labworks/create_lab.html', {'form': form})


@user_passes_test(student_check)
def edit(request, lab_id):
    post = get_object_or_404(Lab, pk=lab_id)
    context = {'edit_lab': post}

    if request.method == "POST":
        taskId = request.POST.get('task_id')
        task = get_object_or_404(Task, pk=taskId)

        form = LabForm(request.POST, instance=post)
        if form.is_valid():
            labwork = form.save()
            labwork.author = request.user
            labwork.task = task
            labwork.condition = post.CONDITION_NOT_CHECKED
            labwork.save()
            return redirect(reverse('taskDetail', args=[task.pk]))
    else:
        form = LabForm(instance=post)
    return render(request, 'labworks/edit_lab.html', context)


@user_passes_test(admin_check)
def check(request, lab_id):
    post = get_object_or_404(Lab, pk=lab_id)
    context = {'check_lab': post}

    if request.method == "POST":
        taskId = post.task.pk
        task = get_object_or_404(Task, pk=taskId)

        form = LabForm(request.POST, instance=post)
        if form.is_valid():
            labwork = form.save()
            labwork.author = post.author
            labwork.task = task
            labwork.condition = post.CONDITION_CHECKED
            labwork.save()
            return redirect(reverse('taskDetail', args=[task.pk]))
    else:
        form = LabForm(instance=post)
    return render(request, 'labworks/check_lab.html', context)


@user_passes_test(user_check)
def download_file(request, lab_id):
    myfile = Lab.objects.get(pk=lab_id).file
    myfile.open('r')
    wrapper = FileWrapper(myfile)
    mt = mimetypes.guess_type(myfile.name)[0]
    response = HttpResponse(wrapper, content_type=mt)

    response['Content-Length'] = myfile.size
    response['Content-Disposition'] = 'attachment; filename={0}'.format(myfile.name)

    return response
