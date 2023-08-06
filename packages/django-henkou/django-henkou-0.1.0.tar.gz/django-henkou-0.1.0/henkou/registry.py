import logging

from . import models
from .backends import CONVERTERS, DEFAULT_CONVERTER

from django.conf import settings
from django.db.models import fields
from django.db.models.signals import post_delete, post_save

logger = logging.getLogger(__name__)

if settings.DEBUG:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


class Registry:
    def __init__(self):
        self._registry = {}
        self._entry_map = {
            fields.UUIDField: models.UUIDHistoryEntry,
        }

    def register(self, model, converter):
        from . import signals  # NOQA

        if converter is None:
            converter = DEFAULT_CONVERTER

        try:
            self._registry[model] = CONVERTERS[converter]
        except KeyError:
            logger.warning("Unknown converter: %s", converter)
        else:
            logger.debug("Registering %s for %s", converter, model)
            post_save.connect(signals.post_save_history, sender=model)
            post_delete.connect(signals.post_delete_history, sender=model)

    def log_action(self, instance, action, **kwargs):
        converter = self.converter_class(instance)
        return self.log_class(instance).objects.create(
            data=converter.data,
            content_object=instance,
            action=action,
        )

    def log_class(self, instance):
        return self._entry_map.get(
            type(instance._meta.pk),
            models.HistoryEntry,
        )

    def converter_class(self, model):
        return self._registry[model._meta.label]()


default_registry = Registry()
