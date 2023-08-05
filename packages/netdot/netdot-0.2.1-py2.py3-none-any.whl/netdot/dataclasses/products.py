from dataclasses import dataclass

from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass


@dataclass
class ProductType(NetdotAPIDataclass, CSVDataclass):
    
    NETDOT_MENU_URL_PATH = 'management'
    NETDOT_TABLE_NAME = 'ProductType'
    id: int = None
    info: str = None
    name: str = None


@dataclass
class Product(NetdotAPIDataclass, CSVDataclass):
    XLINK_ALIAS = 'product_id'
    NETDOT_MENU_URL_PATH = 'management'
    NETDOT_TABLE_NAME = 'Product'
    description: str = None
    id: int = None
    info: str = None
    manufacturer: str = None
    manufacturer_xlink: int = None
    name: str = None
    sysobjectid: str = None
    type: str = None
    type_xlink: int = None
    latest_os: str = None
    part_number: str = None
    config_type: str = None
