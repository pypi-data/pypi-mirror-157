from .asset import Asset
from .base import NetdotAPIDataclass
from .device import Device
from .interface import Interface
from .ipblock import IPBlock
from .products import Product, ProductType
from .site import Site
from .vlan import VLAN

_initialzied = False

def initialize():
    # TODO can these just be at module-level insted of having this be a runtime function?
    global _initialzied
    if not _initialzied:
        Asset()
        Device()
        Interface()
        IPBlock()
        Product()
        ProductType()
        Site()
        VLAN()
        _initialzied = True


__all__ = [
    'initialize', 'Asset', 'Device', 'Interface', 'IPBlock',
    'Product', 'ProductType', 'Site', 'VLAN', 'NetdotAPIDataclass',
]
