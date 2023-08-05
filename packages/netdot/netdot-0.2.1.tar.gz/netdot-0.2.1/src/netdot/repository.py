from __future__ import absolute_import

import logging
import textwrap
from getpass import getpass
from typing import Callable, List, TypeVar

import uologging

import netdot.dataclasses

from . import client, defaults, utils, validate

# TODO Is __future__  needed anymore?

logger = logging.getLogger(__name__)
trace = uologging.trace(logger)


T = TypeVar('T', bound='netdot.dataclasses.NetdotAPIDataclass')


class Repository:
    """Work with Netdot API using Python objects.
    """
    _initialized = False
    _existing_connection = None

    def __init__(self, netdot_url, user, password, **kwargs):
        Repository.prepare_class()
        self._netdot_url = netdot_url
        self._user = user
        self._connection = client.Client(netdot_url, user, password, **kwargs)
        self._products_indexed_by_name = None

    def __str__(self):
        return f"Repository('{self._netdot_url}', '{self._user}')"

    @classmethod
    def _attach_methods(cls, methods):
        for method in methods:
            setattr(cls, method.__name__, method)

    @classmethod
    def prepare_class(cls):
        if not cls._initialized:
            netdot.dataclasses.initialize()
            dataclasses = netdot.dataclasses.NetdotAPIDataclass.__subclasses__()
            cls._attach_methods(
                cls._getters_for_all_dataclasses(dataclasses))
            cls._initialized = True

    @classmethod
    def connect(cls, _input=input, _getpass=getpass):
        """Connect to NetDot within a python REPL session.

        Example:
        This method is interactive, and requires you to provide your username and password everytime you call it.
             >> repo = Repository.connect()
            What is the URL of the NetDot server? [https://nsdb.uoregon.edu]: ('enter' to use default)
            NetDot username: myusername
            NetDot password: (uses getpass module, to securely collect your password)

        With the repository, you can now retrieve data and better understand the capabilities of this API.
        As an example, you may retrieve ipblock information about a particular IP address.

             >> repo.get_ipblock_by_address('10.0.0.0')
            [IPBlock(id=5065, address=IPv4Address('10.0.0.0'), description='RFC1918 Addresses', ... omitted for brevity...

        Returns:
            netdot.Repository: A repository. Use `help(repo)` to learn more.
        """
        # Offer to return an existing connection that has been established before
        if cls._existing_connection:
            yes_or_no = _input(textwrap.dedent(
                f"""
                Noticed an existing connection: 
                    {cls._existing_connection}

                Would you like to retrieve it instead of setting up a new connection? 
                Reply 'yes', or 'no' [yes]: """
            ))
            if not yes_or_no.lower().startswith('n'):
                return cls._existing_connection

        connection = cls._connect(_input, _getpass)
        cls._existing_connection = connection
        return connection

    @classmethod
    def _connect(cls, _input=input, _getpass=getpass):
        default_netdot_url = 'https://nsdb.uoregon.edu'
        netdot_url = (
            _input(
                f'What is the URL of the NetDot server? [{default_netdot_url}]: ')
            or default_netdot_url
        )
        user = input('NetDot username: ')
        password = _getpass('NetDot password: ')
        return cls(netdot_url, user, password)

    @property
    def connection(self) -> 'client.Client':
        if not self._connection:
            raise AttributeError(
                'Must establish a connection before using this repository.')
        return self._connection

    def get_ipblock_children(self, id: int) -> List['netdot.dataclasses.IPBlock']:
        data = self.connection.get_object_by_filter(
            netdot.dataclasses.IPBlock.NETDOT_TABLE_NAME, 'parent', str(id))
        return [
            netdot.dataclasses.IPBlock.from_DTO(
                ipblock).with_repository(self)
            for ipblock in data
        ]

    def get_ipblock_by_address(self, address: str) -> 'netdot.dataclasses.IPBlock':
        """Get some IP Block from Netdot Address Space.

        Args:
            address (str): The IP Address to lookup, e.g. "10.0.0.0"


        Returns:
            IPBlock: The IPBlock object that matched the provided address, or None.
        """
        data = self.connection.get_object_by_filter(
            netdot.dataclasses.IPBlock.NETDOT_TABLE_NAME, 'address', address)
        matching_ipblocks = [
            netdot.dataclasses.IPBlock.from_DTO(
                ipblock).with_repository(self)
            for ipblock in data
        ]
        if len(matching_ipblocks) > 1:
            logger.warning(
                f'Found more than one matching address for {address}: {matching_ipblocks}')
        elif len(matching_ipblocks) < 1:
            return None
        return matching_ipblocks[0]

    def get_vlans_by_interface(self, interface_id: int) -> List['netdot.dataclasses.VLAN']:
        vlan_ids = self._get_valid_VLAN_ids_by_interface(interface_id)
        vlans_data = [
            self.connection.get_object_by_id(
                netdot.dataclasses.VLAN.NETDOT_TABLE_NAME, id)
            for id in vlan_ids
        ]
        vlans_data = list(filter(None, vlans_data))
        return [
            netdot.dataclasses.VLAN.from_DTO(
                vlan).with_repository(self)
            for vlan in vlans_data
        ]

    def _get_valid_VLAN_ids_by_interface(self, interface_id: int) -> List[int]:
        interface_vlans = self.connection.get_object_by_filter(
            'InterfaceVlan', 'interface', interface_id)
        vlan_netdot_ids = [int(interface_vlan['vlan'])
                           for interface_vlan in interface_vlans]
        try:
            map(validate.VLAN_id, vlan_netdot_ids)
        except ValueError as e:
            logger.error(e.message)
        return vlan_netdot_ids

    def get_vlans_count_by_interface(self, interface_id: int) -> int:
        return len(self._get_valid_VLAN_ids_by_interface(interface_id))

    def infer_product(self, device_asset_id: str) -> 'netdot.dataclasses.Product':
        return self.infer_product_from_asset(device_asset_id)

    def _load_product_index(self):
        products = self.get_all_products()
        self._products_indexed_by_name = {
            product.name: product for product in products}

    def infer_product_from_asset(self, asset: str) -> 'netdot.dataclasses.Product':
        if not self._products_indexed_by_name:
            self._load_product_index()
        asset_tokens = asset.split(',')
        asset_tokens = utils.flatten(
            [token.split(' ') for token in asset_tokens])
        for token in asset_tokens:
            if token in self._products_indexed_by_name:
                return self._products_indexed_by_name[token]

    @trace
    def update_site(self, site_id, new_data: 'netdot.dataclasses.Site'):
        self.connection.post(
            f'/{new_data.NETDOT_TABLE_NAME}/{site_id}', new_data.to_DTO())

    @trace
    def create_site(self, new_site: 'netdot.dataclasses.Site'):
        self.connection.create_object(
            new_site.NETDOT_TABLE_NAME, new_site.to_DTO())

    @trace
    def delete_site(self, site_id):
        raise NotImplementedError()

    @classmethod
    def _getters_for_all_dataclasses(cls, dataclasses) -> List:
        getters = []
        for dataclass in dataclasses:
            getters.extend(
                cls._getters_for_dataclass(dataclass))
        return getters

    @classmethod
    def _getters_for_dataclass(cls, dataclass: T) -> List:
        getters_for_dataclass = generate_xlink_getters(dataclass) + [
            generate_by_id_getter(dataclass),
            generate_all_getter(dataclass)
        ]
        cls._attach_methods(getters_for_dataclass)
        return getters_for_dataclass


def generate_by_id_getter(dataclass: T):
    #
    # Generate a custom `get_by_id` method for dataclass
    #
    def get_by_id(repo: Repository, id: int) -> T:
        site_data = repo.connection.get_object_by_id(
            dataclass.NETDOT_TABLE_NAME, str(id))
        return dataclass.from_DTO(site_data).with_repository(repo)
    get_by_id.__doc__ = f"""Get info about a {dataclass.__name__} from Netdot.

        Args:
            id (int): The ID of the {dataclass.__name__} to retrieve.

        Returns:
            netdot.{dataclass.__name__}: The {dataclass.__name__} with `id`. (raises ValueError if `id` is unfound)

        Raises:
            ValueError: if the {dataclass.__name__} cannot be retrieved for some reason.
            NetdotError: if some internal error happens (in this Python Netdot API wrapper, or on the Netdot Server itself).
        """
    get_by_id.__name__ = f'get_{dataclass._pep8_method_friendly_name()}'
    return get_by_id


def generate_all_getter(dataclass) -> Callable:
    def get_all(repo: Repository) -> List[T]:
        data_list = repo.connection.get_all(dataclass.NETDOT_TABLE_NAME)
        return [
            dataclass.from_DTO(data).with_repository(repo)
            for data in data_list
        ]
    get_all.__doc__ = f"""Get info about all {dataclass.__name__} from Netdot.

        Returns:
            List[netdot.{dataclass.__name__}]: All {dataclass.__name__} from Netdot.

        Raises:
            NetdotError: if some internal error happens (in this Python Netdot API wrapper, or on the Netdot Server itself).
        """
    get_all.__name__ = f'get_all_{dataclass._pep8_method_friendly_name()}s'
    return get_all


def _generate_xlink_by_id_getter(dataclass, xlink_class):
    def xlink_by_id_getter(repo: 'Repository', entity_id: int):
        # TODO can we remove NETDOT_TABLE_NAME field and instead ensure that all Dataclasses are appropriately named?
        # Only issue so far seems that: (Pythoninc) IPBlock != Ipblock (Netdot)
        # Otherwise, infer NETDOT_TABLE_NAME from referencing_class_name somehow...
        data_list = repo.connection.get_object_by_filter(
            dataclass._pep8_method_friendly_name(), xlink_class, entity_id)
        return [
            dataclass.from_DTO(data).with_repository(repo)
            for data in data_list
        ]
    return xlink_by_id_getter


def _generate_xlink_getter(dataclass, xlink_class):

    def xlink_getter(repo: 'Repository', entity: xlink_class) -> List[dataclass]:
        property_name = f'{dataclass._pep8_method_friendly_name()}s'
        if not hasattr(entity, property_name):
            data_list = repo.connection.get_object_by_filter(
                dataclass.NETDOT_TABLE_NAME, entity.NETDOT_TABLE_NAME, entity.id)
            object_list = [
                dataclass.from_DTO(data).with_repository(repo)
                for data in data_list
            ]
            # 1. Attach the provided 'entity' to each of the returned 'dataclass objects'
            with_entity_function = getattr(dataclass, f'with_{entity._pep8_method_friendly_name()}')
            object_list = [
                with_entity_function(object, entity)
                for object in object_list
            ]            
            # 2. Attach all the loaded 'dataclass objects' to the 'entity'
            # TODO, make it more clear that this setattr statement adds a new field (and that it follows naming convention) 
            setattr(
                entity, f'{dataclass._pep8_method_friendly_name()}s', object_list)
        return object_list
    return xlink_getter


def generate_xlink_getters(my_cls) -> List:
    """Generate custom `get_A[s]_by_B` methods for dataclass, based on its foreign_key_field_names."""
    xlink_getters = []

    xlink_class_index = my_cls._related_classes()
    xlink_by_id_class_index = dict(
        filter(lambda elem: elem[0].endswith('_xlink'), xlink_class_index.items()))
    xlink_by_entity_class_index = dict(
        filter(lambda elem: not elem[0].endswith('_xlink'), xlink_class_index.items()))

    for xlink, other_cls in xlink_by_id_class_index.items():
        xlink_by_id_getter = _generate_xlink_by_id_getter(my_cls, other_cls)
        xlink_by_id_getter.__doc__ = f"""Get the list of {my_cls.__name__}s associated to a particular {other_cls}.

        Args:
            entity_id (int): Gather all {other_cls.__name__}s that are associated to {my_cls.__name__} with id.

        Returns:
            List[netdot.{my_cls.__name__}]: The list of {my_cls.__name__}s associated to {my_cls.__name__} with id.
        """
        xlink_by_id_getter.__name__ = f'get_{my_cls._pep8_method_friendly_name()}s_by_{xlink}'
        xlink_getters.append(xlink_by_id_getter)

    for xlink, other_cls in xlink_by_entity_class_index.items():
        xlink_getter = _generate_xlink_getter(my_cls, other_cls)
        xlink_getter.__doc__ = f"""Get the list of {my_cls.__name__}s associated to a particular {other_cls.__name__}.

        Args:
            entity (netdot.{other_cls.__name__}): The central entity -- will gather its {my_cls.__name__}s.

        Returns:
            List[netdot.{my_cls.__name__}]: The list of {my_cls.__name__}s.
        """
        xlink_getter.__name__ = f'get_{my_cls._pep8_method_friendly_name()}s_by_{xlink}'
        xlink_getters.append(xlink_getter)
    return xlink_getters
