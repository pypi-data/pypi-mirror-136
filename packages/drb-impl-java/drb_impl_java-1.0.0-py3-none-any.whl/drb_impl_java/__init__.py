
from . import _version

__version__ = _version.get_versions()['version']

from .drb_impl_java_node import DrbJavaBaseNode

from .drb_impl_java_node import DrbJavaNode

del _version

__all__ = [
    'DrbJavaNode',
    'DrbJavaBaseNode'
]
