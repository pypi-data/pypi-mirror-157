"""
Here is the main initialization code that makes
it easier to access the main features of the
other sub-modules
"""
from .meta import version as __version__, author as __author__
from .serialix import Serialix
from .formats.json import JSON_Format


try:
    from .formats.yaml import YAML_Format
except ImportError:
    pass

try:
    from .formats.toml import TOML_Format
except ImportError:
    pass
