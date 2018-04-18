from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from panop.apps.reader.models import TestRun
from panop.apps.reader.utils import get_jdbc_cursor, campaign_central_row_check, sftp_query, loader_table_query


def run_overview(request, test_id):
    test_run = get_object_or_404(TestRun, pk=test_id)
    return render(request, 'run_overview.html', {'test_run': test_run})


def campaign_central_summary(request, test_id):
    test_run = get_object_or_404(TestRun, pk=test_id)
    row = request.GET['row']
    field = campaign_central_row_check(test_run, int(row))
    return JsonResponse({'field': field, 'row': row})


def campaign_central_detail(request):
    return render(request, 'db_detail.html', {'p': "Hello, world!"})


def sftp_check(request, test_id):
    test_run = get_object_or_404(TestRun, pk=test_id)
    status = sftp_query(test_run.pk)
    return JsonResponse({'status': status})


def loader_table_check(request, test_id):
    test_run = get_object_or_404(TestRun, pk=test_id)
    headers, values = loader_table_query(test_run)
    return JsonResponse({'headers': headers, 'values': values})