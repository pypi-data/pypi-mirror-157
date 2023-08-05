from dataclasses import dataclass

from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass


@dataclass
class VLAN(NetdotAPIDataclass, CSVDataclass):
    NETDOT_MENU_URL_PATH = 'management'
    NETDOT_TABLE_NAME = 'Vlan'
    description: str = None
    info: str = None
    name: str = None
    vid: int = None
    vlangroup: int = None

    @property
    def has_valid_vid(self):
        if self.vid is None:
            return False
        try:
            validate.VLAN_id(self.vid)
            return True
        except ValueError:
            return False
