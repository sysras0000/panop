"""panop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from panop.apps.loader import views as loader_views
from panop.apps.help import views as help_views
from panop.apps.reader import views as reader_views

urlpatterns = [
    url(r'^panop/admin/', admin.site.urls),
    url(r'^panop/$', loader_views.home, name='home'),
    url(r'^panop/start/$', loader_views.start_test, name='start'),
    url(r'^panop/test/(?P<test_id>\d+)/$', reader_views.run_overview, name='run_overview'),
    url(r'^panop/test/(?P<test_id>\d+)/ccsummary/$', reader_views.campaign_central_summary, name='cc_summary'),
    url(r'^panop/test/(?P<test_id>\d+)/sftp/$', reader_views.sftp_check, name='sftp_check'),
    url(r'^panop/test/(?P<test_id>\d+)/loader/$', reader_views.loader_table_check, name='loader_check'),
    url(r'^panop/help/$', help_views.help, name='help'),
    url(r'^panop/upload_config/$', loader_views.upload_config, name='upload_config'),
    url(r'^panop/upload_batch/$', loader_views.upload_batch, name='upload_batch'),
    url(r'^panop/download_batch/(?P<data_id>\d+)/?$', loader_views.download_data, name='download_batch'),
    url(r'^panop/download_config/(?P<campaign_id>\d+)/?$', loader_views.download_campaign, name='download_config'),
    url(r'^panop/download_log/(?P<test_id>\d+)/?$', loader_views.download_log, name='download_log'),
]
