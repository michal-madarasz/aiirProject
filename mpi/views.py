import os
from subprocess import Popen, PIPE, TimeoutExpired
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.base import ContentFile
from time import gmtime, strftime

from .forms import MpiParameters, DocumentForm
from .models import Document, ResultDocument


@login_required
def task(request):
    if request.method == 'POST':
        m_form = MpiParameters(request.user, request.POST)
        if m_form.is_valid():
            n_process = m_form.cleaned_data['amount_of_process']
            document_id = m_form.cleaned_data['document_id']
            document = Document.objects.filter(id=document_id)[0]
            document_path = os.path.join(settings.MEDIA_ROOT, document.file.name)
            # print(document.file.name)

            # create empty file to save
            content = ''.encode()
            time = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
            resultDocument = ResultDocument();
            resultDocument.name = document.name + '_' + time
            resultDocument.user = request.user
            resultDocument.file.save('result.txt', ContentFile(content))
            resultDocument.save()
            result_document_path = os.path.join(settings.MEDIA_ROOT, resultDocument.file.name)

            filename = 'clustering.py'

            for root, dirs, files in os.walk('.'):
                if filename in files:
                    filename = os.path.join(root, filename)

            mpi = Popen(['mpirun', '--allow-run-as-root', '-n', n_process, 'python3', filename, document_path, result_document_path], stdout=PIPE)

            try:
                outs, error = mpi.communicate(timeout=15)
            except TimeoutExpired:
                mpi.kill()
                outs, error = mpi.communicate()

            if outs != '':
                print(str(outs, 'utf-8'))
                messages.success(request, f'mpirun succesful')
            else:
                messages.error(request, f'mpi failure')
            redirect('task')
    else:
        messages.error(request, f'No POST')

    if request.user.is_superuser:
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(user=request.user)

    context = {
        'm_form': MpiParameters(request.user),
        'documents': documents,
    }

    return render(request, 'task.html', context)


@login_required
def document(request):
    if request.method == 'POST':
        d_form = DocumentForm(request.POST, request.FILES)
        if d_form.is_valid():
            document = Document()
            document.name = d_form.cleaned_data['name']
            document.file = d_form.cleaned_data['file']
            document.user = request.user
            document.save()
            messages.success(request, f'Your file has been added!')
        else:
            messages.error(request, f'Your file has not been added!')

        return redirect('document')

    if request.user.is_superuser:
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(user=request.user)

    context = {
        'd_form': DocumentForm(),
        'documents': documents,
    }

    return render(request, 'document.html', context)


@login_required
def documentDelete(request, delete_id):
    document = Document.objects.get(id=delete_id)

    if document.user == request.user or request.user.is_superuser:
        if document.delete():
            messages.success(request, f'File has been deleted.')
        else:
            messages.error(request, f'File hasn\'t been delete.')
    else:
        messages.error(request, f'It isn\'t your file.')

    return redirect('document')


@login_required
def resultDocument(request):
    if request.user.is_superuser:
        resultDocuments = ResultDocument.objects.all()
    else:
        resultDocuments = ResultDocument.objects.filter(user=request.user)

    context = {
        'resultDocuments': resultDocuments,
    }

    return render(request, 'result.html', context)