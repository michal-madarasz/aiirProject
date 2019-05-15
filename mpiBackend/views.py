from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from subprocess import Popen, PIPE
from django.contrib import messages


@login_required
def home(request):
    if request.method == 'POST':
        mpi = Popen(["mpirun", "-n", "3", "python3", "/home/misiek/3rok/mpi/Clustering_MPI.py"], stdout=PIPE)
        if mpi != "":
            messages.success(request, f'mpirun succesful')
        else:
            messages.error(request, f'mpi failure')

    return render(request, 'mpiBackend/home.html')
