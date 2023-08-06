import logging

try:
    from importlib_metadata import entry_points
except ImportError:
    from importlib.metadata import entry_points


logger = logging.getLogger(__name__)


CONVERTERS = {}
for ep in entry_points(group="henkou.backends"):
    try:
        converter = ep.load()
    except ImportError:
        logger.error("Error loading %s.%s %s", ep.group, ep.name, ep.module)
    else:
        logger.debug("Loaded %s.%s %s", ep.group, ep.name, ep.module)
        CONVERTERS[f"{ep.group}.{ep.name}"] = converter

DEFAULT_CONVERTER = "henkou.backends.default"
