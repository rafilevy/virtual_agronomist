from django.db import models
from common.models import IndexedTimeStampedModel


class PreTrainingData(models.Model):
    user_data = models.TextField()
    meta_data = models.TextField()
    seen = models.BooleanField(default=False)


class RequestRecord(IndexedTimeStampedModel):
    question = models.TextField()
    extracted = models.TextField()
    answer = models.TextField()
