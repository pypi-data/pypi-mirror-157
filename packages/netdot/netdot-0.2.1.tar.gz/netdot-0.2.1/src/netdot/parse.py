"""Functions for parsing strings.
"""
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List

from netdot import validate
from netdot.mac_address import MACAddress

NETDOT_TIME_FORMAT_STRINGS = [
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d',
]
NETDOT_START_OF_TIME_STRINGS = [
    '0',
    '0000-00-00',
    '0000-00-00 00:00:00',
]

logger = logging.getLogger(__name__)


def RESTful_XML(xml):
    """This is a VERY simple parser specifically built to parse the NetDot-XML Objects.

    Returns: 
      Multi-level dictionary.
    """
    validate.RESTful_XML(xml)
    data = {}
    # TODO Sanitize the xml before trying to parse! E.g. b'C3KX\\x04\\xc3\\xb6\\xc2\\xb6L1G' does not parse correctly!
    xml_root = ET.fromstring(xml)
    if xml_root.attrib:
        # root has attributes, so we're likely
        # receiving a single object
        data = xml_root.attrib
    else:
        # No root attributes means that we're
        # receiving a list of objects
        for child in xml_root:
            if child.tag in data:
                data[child.tag][child.attrib["id"]] = child.attrib
            else:
                data[child.tag] = {}
                data[child.tag][child.attrib["id"]] = child.attrib
    return data


def split_asset_string(asset: str) -> List[str]:
    asset_items = asset.split(', ')
    asset_items = list(map(str.strip, asset_items))
    return asset_items


def MACAddress_from_asset(asset: str) -> MACAddress:
    """Parse a MACAddress out of Netdot 'asset string'.

    Args:
        asset (str): The asset string, of form "<Make Model>, <S/N>, <Base MAC Address>"

    Example: 
        >>> MACAddress_from_asset("Cisco Systems (Airspace) AIR-AP1815W-B-K9, FJC25101LUN, AABBCCDDEEFF")
        MACAddress(raw="AABBCCDDEEFF")

    Returns:
        MACAddress: The Base MAC Address from the asset string.
    """
    asset_tokens = split_asset_string(asset)
    if asset == '0' or len(asset_tokens) != 3:
        logger.debug(f'Unsure how to parse MACAddress from asset string: {asset}')
        return None
    raw_mac_address = split_asset_string(asset)[2]
    return MACAddress(raw_mac_address)


def DateTime(time: str) -> datetime:
    if time in NETDOT_START_OF_TIME_STRINGS:
        return datetime.fromtimestamp(0)

    for time_fmt in NETDOT_TIME_FORMAT_STRINGS:
        try:
            return datetime.strptime(time, time_fmt)
        except ValueError:
            continue

    EXPECTED_FORMATTING = f'datetime should be formatted as one of: {NETDOT_TIME_FORMAT_STRINGS + NETDOT_START_OF_TIME_STRINGS}'
    raise ValueError(
        f'Unable to parse DateTime from: {time} -- {EXPECTED_FORMATTING}')


def ID_from_xlink(xlink_str):
    EXPECTED_FORMATTING = "xlink is formatted: <TableName>/<ID>. E.g. 'Site/41'"
    try:
        # xlink_str is formatted: <TableName>/<ID>
        # E.g. 'Site/41'
        int_str = xlink_str.split('/')[1]
        return int(int_str)
    except IndexError:
        raise ValueError(
            f'Unable to parse id out of xlink value: {xlink_str} -- {EXPECTED_FORMATTING}')
