from django.contrib import admin

from panop.apps.loader.models import Campaign, BatchData

# Register your models here.

admin.site.register(Campaign)
admin.site.register(BatchData)