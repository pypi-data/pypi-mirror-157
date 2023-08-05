import ipaddress

from assertpy import assert_that

import netdot


def test_parse_data_transfer_object_id():
    # Act
    site = netdot.Site.from_DTO({
        'id': '1',
    })

    # Assert
    assert_that(site.id).is_type_of(int)


def test_parse_data_transfer_object_IPBlock():
    # Act
    ipblock = netdot.IPBlock.from_DTO({
        'id': '1',
        'parent_xlink': 'IPBlock/2',
        'address': '10.0.0.1',
    })

    # Assert
    assert_that(ipblock.id).is_type_of(int)
    assert_that(ipblock.parent_xlink).is_type_of(int)
    assert_that(ipblock.address).is_type_of(ipaddress.IPv4Address)


def test_parse_data_transfer_object_logs_WARNING_about_unparsed_DTO_data(caplog):
    # Arrange
    fake_field_we_forgot_to_add = {
        'field_we_forgot_to_add': 'blah',
    }
    data = {
        'id': '1',
    }
    data.update(fake_field_we_forgot_to_add)

    # Act
    netdot.IPBlock.from_DTO(data)

    # Assert
    assert_that(caplog.text).matches(f"WARNING.*Unparsed.*{fake_field_we_forgot_to_add}")
