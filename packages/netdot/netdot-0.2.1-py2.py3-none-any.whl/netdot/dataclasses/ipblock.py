import ipaddress
import logging
from dataclasses import dataclass
from typing import Dict, List

from netdot import defaults, parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass

logger = logging.getLogger(__name__)


@dataclass()
class IPBlock(NetdotAPIDataclass, CSVDataclass):
    """Represents either a subnet or an individual address.

    TODO: consider making aliases for this class: NetdotContainer NetdotAddress, NetdotSubnet
    """
    NETDOT_MENU_URL_PATH = 'management'
    NETDOT_TABLE_NAME = 'Ipblock'
    id: int = None
    address: ipaddress.ip_address = None
    description: str = None
    first_seen: str = None
    monitored: bool = None
    use_network_broadcast: bool = None
    asn: int = None
    used_by: str = None
    version: str = None
    vlan: str = None
    status_xlink: int = None
    status: str = None 
    rir: str = None
    prefix: int = None
    parent: str = None
    parent_xlink: int = None
    owner_xlink: int = None
    owner: str = None
    last_seen: str = None
    interface: str = None
    info: str = None
    _parent: List['IPBlock'] = None

    def get_parent(self) -> 'IPBlock':
        if self._parent is None:
            self._parent = self.repository.get_ipblock(self.parent_xlink)
        return self._parent

    def get_children(self) -> List['IPBlock']:
        return self.repository.get_ipblock_children(self.id)

    @classmethod
    def from_DTO(cls, data: Dict):
        return super().from_DTO(data, cls.default_DTO_parsers({
            'used_by': lambda data: 
                data if data != '0' and bool(data) else None,
        }))
