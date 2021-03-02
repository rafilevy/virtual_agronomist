from django.contrib import admin  # noqa
from .models import PreTrainingData, RequestRecord

# register models
admin.site.register(PreTrainingData)
admin.site.register(RequestRecord)
