import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

logger = logging.getLogger(__name__)


class HistoryManager(models.Manager):
    def get_history(self, instance):
        self.model.objects.filter(content_object=instance)


class HistoryBaseEntry(models.Model):
    class Action(models.TextChoices):
        CREATED = "Created"
        UPDATED = "Updated"
        DELETED = "Deleted"

    data = models.JSONField(encoder=DjangoJSONEncoder)
    updated = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=10, choices=Action.choices)

    objects = HistoryManager()

    class Meta:
        abstract = True


class HistoryEntry(HistoryBaseEntry):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")


class UUIDHistoryEntry(HistoryBaseEntry):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
