from __future__ import unicode_literals
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


class Campaign(models.Model):
    config_file = models.FileField(upload_to='campaigns')
    name = models.CharField(max_length=40)

    @python_2_unicode_compatible
    def __str__(self):
        return self.name

    def get_config(self):
        """Returns a ConfigParser object with the contents of config_file"""
        config = ConfigParser.ConfigParser()
        self.config_file.open()
        config.read(self.config_file.path)
        return config


class BatchData(models.Model):
    DELIMITED = 0
    CSV = 1
    TYPE_CHOICES = ((DELIMITED, 'delimited'), (CSV, 'csv'))

    data_file = models.FileField(upload_to='data')
    name = models.CharField(max_length=40)
    type = models.IntegerField(choices=TYPE_CHOICES, default=DELIMITED)

    @python_2_unicode_compatible
    def __str__(self):
        return self.name
