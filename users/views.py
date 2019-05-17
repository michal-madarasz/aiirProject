import os
from subprocess import Popen, PIPE, TimeoutExpired

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, MpiParameters


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)


@login_required
def file_upload(request):
    save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', request.FILES['file'])
    path = default_storage.save(save_path, request.FILES['file'])
    return default_storage.path(path)


@login_required
def task(request):
    if request.method == 'POST':
        m_form = MpiParameters(request.POST)
        if m_form.is_valid():
            n_process = m_form.cleaned_data['amount_of_process']
            mpi = Popen(["mpirun", "-n", n_process, "python3", "/home/misiek/3rok/mpi/Clustering_MPI.py"], stdout=PIPE)

            try:
                outs, error = mpi.communicate(timeout=15)
            except TimeoutExpired:
                mpi.kill()
                outs, error = mpi.communicate()

            if outs != "":
                print(str(outs, 'utf-8'))
                messages.success(request, f'mpirun succesful')
            else:
                messages.error(request, f'mpi failure')
            redirect('task')
    else:
        m_form = MpiParameters()
        messages.error(request, f'No POST')

    return render(request, 'users/task.html', {'m_form': m_form})
