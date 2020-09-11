from django.shortcuts import render
from pmedian.tasks import *
from pandas import errors
from prsapp.common.utilities import *
import json
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
import glob
import os.path


@csrf_exempt
def extract_csv(request):
    """
    Getting a (two-column) csv and returning it as a json
    **Expected a lat/lon csv with headers
    """
    if request.method == 'POST' and request.FILES['myfile']:

        if not validate_upload(request, '.csv'):
            return HttpResponseBadRequest("Data error: Please provide a valid csv file")

        try:
            # expecting csv with headers
            df = pd.read_csv(request.FILES['myfile'])
            if column_numeric(df[df.columns[0]]) and column_numeric(df[df.columns[1]]) and not df.isnull().values.any():
                df.columns = ['latitude', 'longitude']
                return HttpResponse(df.to_json(orient='records'))
            else:
                return HttpResponseBadRequest("Data input error: Ensure data is numeric and no missing values exist")

        except errors.EmptyDataError:
            return HttpResponse('CSV file is empty')

    else:
        # In case of GET request, just show the form
        return render(request, 'file_upload.html', locals())


@csrf_exempt
def create_task(request):
    if request.method == 'POST':
        try:
            args = json.loads(request.POST.get('data'))  # error checking
            input_df = pd.read_csv(request.FILES['myfile'], header=0)
            task = p_median_calculation_task.delay(input_df.to_json(), args)
            return HttpResponse("Task-id=" + str(task))

        except MultiValueDictKeyError:
            return HttpResponseBadRequest("Please provide the correct input data")
    else:
        return HttpResponse(status=405, reason="Method not allowed")


@csrf_exempt
def get_task(request):
    """
    Return the status of a task given it's id
    """
    try:
        task_id = request.GET['task-id']
        result = AsyncResult(task_id)
        result_dct = {result.task_id: {'status': result.status, 'date_done': str(result.date_done)}}

        result_dct[result.task_id]['result'] = result.result
        if isinstance(result_dct[result.task_id]['result'], ValueError):
            result_dct[result.task_id]['result'] = 'Calculation ongoing'

        return HttpResponse(json.dumps(result_dct))

    except KeyError:
        return HttpResponseBadRequest("Please provide a valid task-id")


@csrf_exempt
def get_all_tasks(request):
    """
    Get all celery tasks from  and return id, status (json)
    """

    path = "/tmp/results/celery-task-meta-*"
    results = (glob.glob(path))

    result_array = []
    for result in results:
        result_dct = {result[len(path) - 1:]: {'status': AsyncResult(result[len(path) - 1:]).status,
                                               'date_done': str(AsyncResult(result[len(path) - 1:]).date_done)}}

        if os.path.exists('output/' + result[len(path) - 1:] + ".json"):
            result_dct[result[len(path) - 1:]]['result'] = "http://localhost:8000/pmedian/get-file?filename=" + result[len(path) - 1:] + ".json"
        else:
            result_dct[result[len(path) - 1:]]['result'] = 'Calculation ongoing'
        result_array.append(result_dct)

    return HttpResponse(json.dumps(result_array))


@csrf_exempt
def get_file(request):
    """
    Download output file to disk.
    """
    return download_output_file(request)
