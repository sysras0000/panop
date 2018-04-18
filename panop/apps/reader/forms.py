from django.forms import ModelForm, RadioSelect

from panop.apps.reader.models import TestRun


class TestRunForm(ModelForm):
    class Meta:
        model = TestRun
        fields = ['campaign', 'data_file']
        widgets = {'campaign': RadioSelect(), 'data_file': RadioSelect()}