from django.apps import AppConfig
from django.conf import settings


class HistoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "henkou"

    def ready(self):
        # Load registry here, so that we can delay loading
        # until our app is ready
        from .registry import default_registry

        models = getattr(settings, "DJANGO_HISTORY_MODELS", [])

        # For each entry, we want to see if it is a tuple or just
        # a string, and then call our register model accordingly
        for entry in models:
            if isinstance(entry, (tuple, list)):
                model, converter = entry[0], entry[1]
            else:
                model, converter = entry, None

            default_registry.register(model=model, converter=converter)
