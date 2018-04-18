from __future__ import print_function
try:
    import ConfigParser
    from ConfigParser import NoOptionError
except ImportError:
    import configparser as ConfigParser
    from configparser import NoOptionError
import os

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

from panop.apps.loader.models import Campaign, BatchData
from panop.apps.loader.forms import CampaignForm, BatchDataForm
from panop.apps.loader.utils import batch_file_upload, real_time_bulk_insert
from panop.apps.reader.models import TestRun
from panop.apps.reader.forms import TestRunForm
from panop.apps.reader.tasks import write_log


def home(request):

    return render(request, 'home.html', {'configs': Campaign.objects.all(),
                                         'data': BatchData.objects.all(),
                                         'runs': TestRun.objects.all().order_by('-pk')[:25],
                                         'run_form': TestRunForm(),
                                         'config_form': CampaignForm(),
                                         'data_form': BatchDataForm()})


def upload_config(request):
    form = CampaignForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save()
    else:
        print(form.errors.as_data())
    return redirect('home')


def upload_batch(request):
    form = BatchDataForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save()
    else:
        print(form.errors.as_data())
    return redirect('home')


def start_test(request):
    form = TestRunForm(request.POST)
    if form.is_valid():
        test_run = form.save(commit=False)
        parser = ConfigParser.ConfigParser()
        config_field = test_run.campaign.config_file
        parser.read(config_field.path)
        print("=====PARSER=====")
        print(parser.sections())
        try:
            test_run.duration = parser.get('run', 'poll_total_minutes')
        except NoOptionError as error:
            test_run.duration = 30
        test_run.save()
        f = open(os.path.join(settings.MEDIA_ROOT, 'logs/' + str(test_run.pk)) + '.txt', 'w')
        f.close()
        test_run.log_file.name = f.name
        test_run.save()
        if 'sftp' in parser.sections():
            write_log.delay(test_run.pk, "startup", "Attempting batch file upload")
            try:
                batch_file_upload(local_file=test_run.data_file.data_file,
                                  destination_host=parser.get('sftp', 'host'),
                                  destination_directory=parser.get('sftp', 'target'),
                                  destination_filename=parser.get('sftp', 'filename'),
                                  username=parser.get('sftp', 'user'),
                                  password=parser.get('sftp', 'password'))
                write_log.delay(test_run.pk, "startup", "Batch file uploaded")
            except Exception as e:
                write_log.delay(test_run.pk, "startup", "(ERROR) Batch file upload failed!")
                messages.warning(request, "Batch file upload failed! " + "|".join(e.args))
                print(e.args)

        elif 'realtime insert' in parser.sections():
            write_log.delay(test_run.pk, "startup", "Attempting KVP RTI")
            try:
                real_time_bulk_insert(filename=test_run.data_file.data_file.path,
                                      url=parser.get('realtime insert', 'url'),
                                      soapaction=parser.get('realtime insert', 'soapaction'),
                                      format_table=parser.get('campaign table', 'table'),
                                      authscheme=parser.get('realtime insert', 'authscheme'),
                                      auth={'name': parser.get('realtime insert', 'name'),
                                            'password': parser.get('realtime insert', 'password')})
            except Exception as e:
                print(e)
                write_log.delay(test_run.pk, 'startup', "(ERROR) KVP RTI failed!")
                messages.warning(request, "Real time insert failed!")
        write_log.delay(test_run.pk, "startup", "Startup routine complete")
        return redirect('run_overview', test_run.pk)
    else:
        messages.warning(request, "Test runs require both a campaign configuration and a data file")
        print(form.errors.as_data())
        return redirect('home')


def download_data(request, data_id):
    data = get_object_or_404(BatchData, pk=data_id)
    response = HttpResponse(data.data_file.read(), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="{0}.txt"'.format(data.name)
    return response


def download_campaign(request, campaign_id):
    data = get_object_or_404(Campaign, pk=campaign_id)
    response = HttpResponse(data.config_file.read(), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="{0}.txt"'.format(data.name)
    return response


def download_log(request, test_id):
    data = get_object_or_404(TestRun, pk=test_id)
    response = HttpResponse(data.log_file.read(), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="testlog.txt"'
    return response
