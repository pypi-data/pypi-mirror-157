"""Functions to help validate the correctness of arbitrary values.

Note: Raise an Error validation fails.
"""

from netdot.exceptions import NetdotError


def VLAN_id(vlan_id: int):
    # ensure: 1 <= vid <= 4094
    if vlan_id < 1 or vlan_id > 4094:
        raise ValueError(f'VLAN ID outside of valid range: {vlan_id}')


def RESTful_XML(content):
    expected_root_token = '<opt'
    xml_message = str(content)
    if expected_root_token not in xml_message:
        raise NetdotError(f'Expected {expected_root_token} to be root of XML response. Response: {xml_message[:256]}... trimmed for brevity...')
