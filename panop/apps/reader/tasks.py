from __future__ import print_function
import datetime

from django.utils import timezone

import panop
import panop.apps.reader.models
import panop.apps.reader.utils


@panop.celery_app.task(bind=True)
def write_log(self, test_run_id, context, message):
    test_run = panop.apps.reader.models.TestRun.objects.get(pk=test_run_id)
    try:
        log_file = open(test_run.log_file.name, 'a')
        log_file.write("{0} {1}: {2}\n".format(datetime.datetime.now().strftime("%x %X"), context.upper(), message))
        log_file.close()
    except Exception as e:
        print(e)


@panop.celery_app.task
def monitor_pulse(test_run_id):
    test_run = panop.apps.reader.models.TestRun.objects.get(pk=test_run_id)
    now = timezone.now()
    if now > test_run.start + datetime.timedelta(minutes=test_run.duration):
        test_run.running = False
        test_run.save()
        write_log.delay(test_run_id, 'monitor', 'Test run complete')
        return
    for row in range(len(test_run.get_data_file_rows())):
        panop.apps.reader.utils.campaign_central_row_check(test_run, row)


@panop.celery_app.task
def poll_projects():
    # When scheduling is added, poll for future start times here
    running_tests = panop.apps.reader.models.TestRun.objects.filter(running=True).values_list('pk', flat=True)
    for test in running_tests:
        monitor_pulse.delay(test)
    print('Poll complete')