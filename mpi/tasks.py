import os, time 
from subprocess import Popen, PIPE, TimeoutExpired
from background_task import background
from .models import ResultDocument
from django.conf import settings

@background(schedule=1)
def mpiTask(n_process, document_path, result_document_path, result_document_id):
    result_document = ResultDocument.objects.filter(id=result_document_id)[0]

    filename = 'clustering.py'

    for root, dirs, files in os.walk('.'):
        if filename in files:
            filename = os.path.join(root, filename)

    start_time = time.time()
    mpi = Popen(['mpirun', '--allow-run-as-root', '-n', n_process, 'python3', filename, document_path, result_document_path], stdout=PIPE)

    try:
        outs, error = mpi.communicate()
        end_time = time.time()
    except TimeoutExpired:
        mpi.kill()
        outs, error = mpi.communicate()

    if outs != '':
    	result_document.time = end_time - start_time
    	result_document.ready = True
    	result_document.nr_process = n_process
    	result_document.save()

    print('Done')
