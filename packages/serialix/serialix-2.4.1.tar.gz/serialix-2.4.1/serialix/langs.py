"""
This module was marked as deprecated in ``2.4.0``
and will be removed in ``3.0.0``.
Use ``serialix.formats`` module instead.
"""

from .formats.json import JSON_Format
from .formats.toml import TOML_Format
from .formats.yaml import YAML_Format

from .core import deprecation_mark


deprecation_mark(
    "Module '{}' was deprecated in version '2.4.0' and will be removed in '3.0.0'."
    " Use 'serialix.formats' module instead."
    .format(__name__)
)
