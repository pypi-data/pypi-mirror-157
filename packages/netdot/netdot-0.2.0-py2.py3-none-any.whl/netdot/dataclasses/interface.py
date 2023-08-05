import logging
from dataclasses import dataclass
from typing import List

from netdot import defaults, parse
from netdot.csv_util import CSVDataclass
from netdot.mac_address import MACAddress
from netdot.dataclasses.base import NetdotAPIDataclass
import netdot.dataclasses

logger = logging.getLogger(__name__)


def is_up(up_str: str):
    return up_str.lower().strip() == 'up'


@dataclass
class Interface(NetdotAPIDataclass, CSVDataclass):
    NETDOT_MENU_URL_PATH = 'management'
    NETDOT_TABLE_NAME = 'Interface'
    id: int = None
    physaddr: MACAddress = None 
    name: str = None
    device: str = None
    device_xlink: str = None
    oper_status: str = None
    admin_status: str = None
    _vlans: 'netdot.dataclasses.VLAN' = None
    # admin_duplex: str = None
    # bpdu_filter_enabled: bool = None
    # bpdu_guard_enabled: bool = None
    # contactlist: int = None
    # description: str = None
    # doc_status: str = None
    # down_from: datetime = None
    # down_until: datetime = None
    # dp_remote_id: str = None
    # dp_remote_ip: str = None
    # dp_remote_port: str = None
    # dp_remote_type: str = None
    # info: str = None
    # jack: int = None
    # jack_char: str = None
    # loop_guard_enabled: bool = None
    # monitored: bool = None
    # monitorstatus: int = None
    neighbor: str = None
    # neighbor_fixed: bool = None
    # neighbor_missed: int = None
    # number: str = None
    # oper_duplex: str = None
    # overwrite_descr: bool = None
    # room_char: str = None
    # root_guard_enabled: bool = None
    # snmp_managed: bool = None
    # speed: int = None
    # stp_id: str = None
    # type : str = None
    # ignore_ip: bool = None
    # auto_dns: bool = None
    # circuit: int = None
    # dlci: str = None

    @property
    def oper_up(self):
        return is_up(self.oper_status)

    @property
    def admin_up(self):
        return is_up(self.admin_status)

    def is_up(self):
        """An interface is 'up' a VLAN assigned is an Access Port.
        """
        return self.oper_up and self.admin_up

    def _is_access_port(self):
        """TODO Is this an access port? (best-effort, may also include non-access ports) 

        An Access Port is one that is used by the actual access layer, e.g. desktops, servers, laptops.

        We determine whether this interface may be an access first by checking for the following:
        * a single VLAN,
        * named like a physical interface...* TODO

        Then, we can look for any signs any signs it is NOT an access port:
        * has a 'neighboring interface',

        TODO: Is this valid we have LLDP-MED access ports?
        """
        if self.neighbor is None:
            return False
        vlans = self.get_vlans()
        if len(vlans) != 1:
            return False
        return True

    def get_vlans_count(self) -> List['netdot.VLAN']:
        if self._vlans is None: 
            self._vlans = self.repository.get_vlans_count_by_interface(self.id)
        return self._vlans

    def get_vlans(self) -> List['netdot.VLAN']:
        if self._vlans is None: 
            self._vlans = self.repository.get_vlans_by_interface(self.id)
        return self._vlans
