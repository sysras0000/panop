from django.forms import ModelForm

from panop.apps.loader.models import Campaign, BatchData


class CampaignForm(ModelForm):
    class Meta:
        model = Campaign
        fields = ['config_file', 'name']


class BatchDataForm(ModelForm):
    class Meta:
        model = BatchData
        fields = ['data_file', 'name', 'type']