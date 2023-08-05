from . import _version
from .wXs_node import WXSNodeOperation, WXSServiceNode, \
    WXSNodeOperationGetCapabilities

__version__ = _version.get_versions()['version']
__all__ = [
    'WXSNodeOperationGetCapabilities',
    'WXSNodeOperation',
    'WXSServiceNode'
]
