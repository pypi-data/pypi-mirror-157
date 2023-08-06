from pkg_resources import get_distribution

__version__ = get_distribution("marshmallow-jsonschema-3").version
__license__ = "MIT"

from .base import JSONSchema
from .exceptions import UnsupportedValueError

__all__ = ("JSONSchema", "UnsupportedValueError")
