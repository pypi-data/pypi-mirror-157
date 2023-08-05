import ipaddress
import os

import pytest
from assertpy import assert_that

from netdot import Repository
from netdot.mac_address import MACAddress


@pytest.fixture
def repository() -> Repository:
    url = os.environ.get('NETDOT_URL', 'https://is-nsdb.uoregon.edu')
    username = os.environ.get('NETDOT_USERNAME', '')
    password = os.environ.get('NETDOT_PASSWORD', '')
    return Repository(url, username, password, times_to_retry=1)

def test_Repository_initialization_of_methods():
    # Arrange (assert)
    assert_that(Repository._initialized).is_false()

    # Act
    Repository.prepare_class()

    # Assert
    assert_that(Repository._initialized).is_true()
    Repository_attribute_names = vars(Repository).keys()
    assert_that(Repository_attribute_names).contains('get_device')
    assert_that(Repository_attribute_names).contains('get_all_devices')
    assert_that(Repository_attribute_names).contains('get_site')
    assert_that(Repository_attribute_names).contains('get_devices_by_site')
    assert_that(Repository_attribute_names).contains('get_devices_by_asset')
    assert_that(Repository_attribute_names).contains('get_interfaces_by_device')


@pytest.mark.vcr()
def test_discover_sites_devices(repository: Repository):
    # Arrange
    site = repository.get_site(142)  # 142 => 1900 Millrace Drive

    # Act
    devices = site.load_devices()

    # Assert
    assert_that(devices).is_length(3)
    device = devices[0]
    assert_that(device.base_MAC).is_equal_to(MACAddress('F0B2E560AA00'))


@pytest.mark.vcr()
def test_get_devices_by_site(repository: Repository):
    # Arrange
    site = repository.get_site(142)  # 142 => 1900 Millrace Drive

    # Act
    devices = repository.get_devices_by_site(site)

    # Assert
    assert_that(devices).is_length(3)
    device = devices[0]
    assert_that(device.base_MAC).is_equal_to(MACAddress('F0B2E560AA00'))


@pytest.mark.vcr()
def test_get_site_from_device(repository: Repository):
    # Arrange
    MILLRACE_BLDG_NUMBER = '043'
    MILLRACE_DEVICE_ID = 9061  # A device from 1900 Millrace Drive (rrpnet-1900-millrace-drive-poe-sw1.net.uoregon.edu)
    device = repository.get_device(MILLRACE_DEVICE_ID) 

    # Act
    site = device.load_site()

    # Assert
    assert_that(site.number).is_equal_to(MILLRACE_BLDG_NUMBER)


@pytest.mark.vcr()
def test_web_urls(repository: Repository):
    # Arrange
    site = repository.get_site(142)  # 1900 Millrace Drive
    interface = repository.get_interface(87428)  # autzen-idfc-sw1's First interface
    device = repository.get_device(9643)  # alder-building-mdf-poe-sw1

    assert_that(site.web_url).is_equal_to('https://is-nsdb.uoregon.edu/cable_plant/view.html?table=Site&id=142')
    assert_that(device.web_url).is_equal_to('https://is-nsdb.uoregon.edu/management/device.html?id=9643')
    assert_that(interface.web_url).is_equal_to('https://is-nsdb.uoregon.edu/management/interface.html?id=87428')


@pytest.mark.vcr()
def test_discover_device_interfaces(repository: Repository):
    # Arrange
    device = repository.get_device(9643)  # 9643 => alder-building-mdf-poe-sw1

    # Act
    interfaces = device.load_interfaces()

    # Assert
    assert_that(interfaces).is_length(58)
    interface = interfaces[0]
    assert_that(interface.physaddr).is_equal_to(MACAddress('B033A673763B'))


@pytest.mark.vcr()
def test_get_vlan_by_interface(repository: Repository):
    # Act
    vlans = repository.get_vlans_by_interface(87428)  # autzen-idfc-sw1's First interface

    # Assert
    assert_that(vlans).is_length(1)
    vlan = vlans[0]
    assert_that(vlan.vid).is_equal_to(216)
    assert_that(vlan.name).is_equal_to('CC_IS_NGR_216')


@pytest.mark.vcr()
def test_get_vlan_count_by_interface(repository: Repository):
    # Act
    count = repository.get_vlans_count_by_interface(87428)  # autzen-idfc-sw1's First interface

    # Assert
    assert_that(count).is_equal_to(1)


@pytest.mark.vcr()
def test_discover_interface_vlan(repository: Repository):
    # Arrange
    interface = repository.get_interface(87428)  # autzen-idfc-sw1's First interface

    # Act
    vlans = interface.get_vlans()

    # Assert
    assert_that(vlans).is_length(1)
    vlan = vlans[0]
    assert_that(vlan.vid).is_equal_to(216)
    assert_that(vlan.name).is_equal_to('CC_IS_NGR_216')


@pytest.mark.vcr()
def test_get_ipblock_StaticAddress(repository: Repository):
    # Act
    ipblock_address = repository.get_ipblock(177611046)  # "uoregon.edu" IP address

    # Assert
    assert_that(ipblock_address.address).is_equal_to(ipaddress.ip_address('184.171.111.233'))
    assert_that(ipblock_address.prefix).is_equal_to(32)
    assert_that(ipblock_address.status).is_equal_to('Static')
    assert_that(ipblock_address.used_by).is_none()


@pytest.mark.vcr()
def test_get_ipblock_Subnet(repository: Repository):
    # Act
    ipblock_subnet = repository.get_ipblock(271514934)  # Subnet associated to "uoregon.edu" IP address 

    # Assert
    assert_that(ipblock_subnet.address).is_equal_to(ipaddress.ip_address('184.171.111.0'))
    assert_that(ipblock_subnet.prefix).is_equal_to(24)
    assert_that(ipblock_subnet.status).is_equal_to('Subnet')
    assert_that(ipblock_subnet.used_by).is_equal_to('Information Services')


@pytest.mark.vcr()
def test_get_ipblock_Container(repository: Repository):
    # Act
    ipblock_container = repository.get_ipblock(177611409)  # Container associated to "uoregon.edu" Subnet

    # Assert
    assert_that(ipblock_container.address).is_equal_to(ipaddress.ip_address('184.171.96.0'))
    assert_that(ipblock_container.prefix).is_equal_to(19)
    assert_that(ipblock_container.status).is_equal_to('Container')


@pytest.mark.vcr()
def test_discover_ipblock_Subnet_from_StaticAddress(repository: Repository):
    # Arrange
    ipblock_address = repository.get_ipblock(177611046)

    # Act
    ipblock_subnet = ipblock_address.get_parent()

    # Assert
    assert_that(ipblock_subnet.address).is_equal_to(ipaddress.ip_address('184.171.111.0'))
    assert_that(ipblock_subnet.prefix).is_equal_to(24)
    assert_that(ipblock_subnet.status).is_equal_to('Subnet')
    assert_that(ipblock_subnet.used_by).is_equal_to('Information Services')


@pytest.mark.vcr()
def test_get_ipblock_by_address_StaticAddress(repository: Repository):
    # Act
    ipblock_address = repository.get_ipblock_by_address('184.171.111.233')

    # Assert
    assert_that(ipblock_address.address).is_equal_to(ipaddress.ip_address('184.171.111.233'))
    assert_that(ipblock_address.prefix).is_equal_to(32)
    assert_that(ipblock_address.status).is_equal_to('Static')
    assert_that(ipblock_address.used_by).is_none()


@pytest.mark.vcr()
def test_get_ipblock_by_address_StaticAddressIPv6(repository: Repository):
    # Act
    ipblock_address = repository.get_ipblock_by_address('2605:bc80:200f:2::5')

    # Assert
    assert_that(ipblock_address.address).is_equal_to(ipaddress.ip_address('2605:bc80:200f:2::5'))
    assert_that(ipblock_address.prefix).is_equal_to(128)
    assert_that(ipblock_address.status).is_equal_to('Reserved')


@pytest.mark.vcr()
def test_get_ipblock_by_address_Subnet(repository: Repository):
    # Act
    ipblock_subnet = repository.get_ipblock_by_address('184.171.111.0')
    ipblock_subnet.get_children()

    # Assert
    assert_that(ipblock_subnet.address).is_equal_to(ipaddress.ip_address('184.171.111.0'))
    assert_that(ipblock_subnet.prefix).is_equal_to(24)
    assert_that(ipblock_subnet.status).is_equal_to('Subnet')
    assert_that(ipblock_subnet.used_by).is_equal_to('Information Services')


@pytest.mark.vcr()
def test_get_product_with_wierd_name(repository: Repository):
    # Act
    product = repository.get_product(377)

    # Assert
    assert_that(product.name).is_equal_to('800-????5-02')
    assert_that(product.type).is_equal_to('Module')


@pytest.mark.vcr()
def test_get_product(repository: Repository):
    # Act
    product = repository.get_product(802)

    # Assert
    assert_that(product.name).is_equal_to('EX3400-24P')
    assert_that(product.type).is_equal_to('Switch')


@pytest.mark.vcr()
def test_get_products(repository: Repository):
    # Act
    products = repository.get_all_products()

    # Assert
    assert_that(products).is_length(786)


@pytest.mark.vcr()
def test_infer_product(repository: Repository):
    # Arrange
    device = repository.get_device(10091)

    # Act
    product = device.infer_product()

    # Assert;
    assert_that(product.type).is_equal_to('Switch')
    assert_that(product.name).is_equal_to('EX3400-48P')
