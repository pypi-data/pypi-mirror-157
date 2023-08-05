from dataclasses import dataclass

from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass
from netdot.mac_address import MACAddress


@dataclass
class Asset(NetdotAPIDataclass, CSVDataclass):
    NETDOT_MENU_URL_PATH = 'management'
    NETDOT_TABLE_NAME = 'Asset'
    XLINK_ALIAS = 'asset_id'
    #
    # Relational fields
    #
    product_id: str = None
    product_id_xlink: int = None    
    physaddr: MACAddress = None
    physaddr_xlink: int = None
    maint_contract: str = None
    maint_contract_xlink: int = None
    #
    # Basic fields
    #
    custom_serial: str = None
    updated: parse.DateTime = None
    description: str = None
    id: int = None
    info: str = None
    inventory_number: str = None
    maint_from: parse.DateTime = None
    maint_until: parse.DateTime = None
    po_number: str = None
    reserved_for: str = None
    serial_number: str = None
