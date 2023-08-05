import ipaddress
import logging
from dataclasses import dataclass
from typing import Dict

import netdot.dataclasses
from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass
from netdot.mac_address import MACAddress

logger = logging.getLogger(__name__)


@dataclass()
class Device(NetdotAPIDataclass, CSVDataclass):
    NETDOT_MENU_URL_PATH = 'management'
    NETDOT_TABLE_NAME = 'Device'
    #
    # Inferred fields
    #
    base_MAC: MACAddress = None
    #
    # Relational fields
    #
    site_xlink: int = None
    site: str = None
    asset_id: str = None
    asset_id_xlink: int = None
    monitorstatus: int = None
    monitorstatus_xlink: int = None
    name: str = None
    name_xlink: int = None
    host_device: str = None
    host_device_xlink: int = None
    bgplocalas: int = None
    bgplocalas_xlink: int = None
    snmp_target: ipaddress.ip_address = None
    snmp_target_xlink: int = None
    room: str = None
    room_xlink: int = None
    owner: str = None
    owner_xlink: int = None
    used_by: str = None
    used_by_xlink: int = None
    #
    # Basic fields
    #
    id: int = None
    name: str = None
    aliases: str = None
    bgpid: str = None
    canautoupdate: bool = None
    collect_arp: bool = None
    collect_fwt: bool = None
    collect_stp: bool = None
    community: str = None
    customer_managed: bool = None
    date_installed: parse.DateTime = None
    down_from: parse.DateTime = None
    down_until: parse.DateTime = None
    info: str = None
    ipforwarding: bool = None
    last_arp: parse.DateTime = None
    last_fwt: parse.DateTime = None
    last_updated: parse.DateTime = None
    layers: str = None
    monitor_config: bool = None
    monitor_config_group: str = None
    monitored: bool = None
    monitoring_path_cost: int = None
    oobname: str = None
    oobnumber: str = None
    os: str = None
    rack: str = None
    snmp_authkey: str = None
    snmp_authprotocol: str = None
    snmp_bulk: bool = None
    snmp_managed: bool = None
    snmp_polling: bool = None
    snmp_privkey: str = None
    snmp_privprotocol: str = None
    snmp_securitylevel: str = None
    snmp_securityname: str = None
    snmp_version: int = None
    stp_enabled: bool = None
    stp_mst_digest: str = None
    stp_mst_region: str = None
    stp_mst_rev: str = None
    stp_type: str = None
    sysdescription: str = None
    syslocation: str = None
    sysname: str = None
    auto_dns: bool = None
    extension: str = None
    snmp_conn_attempts: int = None
    snmp_down: bool = None
    oobname_2: str = None
    oobnumber_2: str = None
    power_outlet: str = None
    power_outlet_2: str = None
    monitoring_template: str = None

    def infer_product(self) -> 'netdot.Product':
        return self.repository.infer_product(self.asset_id)

    @classmethod
    def from_DTO(cls, data: Dict):
        device = super().from_DTO(data)
        if device.asset_id:
            try:
                device.base_MAC = parse.MACAddress_from_asset(device.asset_id)
            except Exception as e:
                logger.warning(f'Parsing error when parsing asset_id: {device.asset_id}. Error: {e}')
        return device
