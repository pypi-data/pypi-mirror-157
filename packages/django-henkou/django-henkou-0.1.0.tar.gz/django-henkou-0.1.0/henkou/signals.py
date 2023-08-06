import logging

from .models import HistoryEntry
from .registry import default_registry

logger = logging.getLogger(__name__)


def post_save_history(raw, created, **kwargs):
    if raw:
        return

    default_registry.log_action(
        action=HistoryEntry.Action.CREATED if created else HistoryEntry.Action.UPDATED,
        raw=raw,
        created=created,
        **kwargs,
    )


def post_delete_history(**kwargs):
    default_registry.log_action(
        action=HistoryEntry.Action.DELETED,
        **kwargs,
    )
