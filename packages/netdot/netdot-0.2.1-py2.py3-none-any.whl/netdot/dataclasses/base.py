import copy
import logging
from typing import Callable, Dict, List, Set

from netdot import parse

logger = logging.getLogger(__name__)


def convert_None_values_to_empty_str(diict):
    ret = dict()
    for key, val in diict.items():
        if val is None:
            ret[key] = ''
        else:
            ret[key] = val
    return ret


class NetdotAPIDataclass():
    _logged_unused_fields: Set = None
    NETDOT_TABLE_NAME: str
    NETDOT_MENU_URL_PATH: str  # Useful for generating web_url
    DEFAULT_DTO_FIELD_PARSERS = {
        '*_xlink': parse.ID_from_xlink,
    }

    _initialized = False

    def __post_init__(self):
        cls = type(self)
        if not cls._initialized:
            cls._generate_and_attach_others_getAll_methods()
            cls._generate_and_attach_my_getter_methods()
            cls._generate_and_attach_my_setter_methods()
            cls._logged_unused_fields = set()
            cls._initialized = True

    @classmethod
    def _attach_methods(cls, methods):
        for method in methods:
            setattr(cls, method.__name__, method)

    @classmethod
    def _pep8_method_friendly_name(cls):
        return cls.__name__.lower()

    @classmethod
    def _xlink_field_name(cls):
        # TODO 
        if hasattr(cls, 'XLINK_ALIAS'):
            return cls.XLINK_ALIAS
        return cls._pep8_method_friendly_name()

    @classmethod
    def default_DTO_parsers(cls, additional_parsers: Dict[str, Callable] = None) -> Dict[str, Callable]:
        default_parsers_copy = dict(cls.DEFAULT_DTO_FIELD_PARSERS.copy())
        default_parsers_copy.update(additional_parsers)
        return default_parsers_copy

    def __init__(self):
        # Enable a discoverable API by attaching the 'repository' to every data object it produces.
        self.id = None
        self._repository = None

    @classmethod
    def foreign_key_field_names(cls) -> List:
        # Get all keys ending with the _xlink suffix. Example: asset_id_xlink 
        # 
        foreign_key_field_name_indicator = '_xlink'
        # old_keys = vars(cls).keys()
        new_keys = cls.__dataclass_fields__.keys()
        foreign_keys = list(filter(
            lambda field_name: field_name.endswith(
                foreign_key_field_name_indicator),
            new_keys
        ))
        # Copy all those keys without the _xlink suffix. Example: asset_id_xlink => asset_id
        foreign_keys.extend([
            key[:-len(foreign_key_field_name_indicator)]
            for key in foreign_keys
        ])
        # Copy all those keys without the _id_xlink suffix. Example: asset_id_xlink => asset
        foreign_key_field_name_indicator = '_id_xlink'
        foreign_keys_need_simplify = list(filter(
            lambda field_name: field_name.endswith(
                foreign_key_field_name_indicator),
            vars(cls).keys()
        ))
        foreign_keys.extend([
            key[:-len(foreign_key_field_name_indicator)]
            for key in foreign_keys_need_simplify
        ])
        return foreign_keys    

    @classmethod
    def _related_classes(cls) -> Dict[str, 'NetdotAPIDataclass']:
        related_object_types = {}
        for xlink in cls.foreign_key_field_names():
            for other_dataclass in NetdotAPIDataclass.__subclasses__():
                if xlink == other_dataclass.__name__.lower():
                    related_object_types[xlink] = other_dataclass

        return related_object_types

    def to_DTO(self) -> Dict:
        """Convert to a Data Transfer Object (compliant with NetDot REST API).

        Returns:
            Dict: Use as input to Netdot API POST calls, for creation/update operations.
        """
        my_updatable_fields = list(filter(
            lambda field_name:
                # Filter 'private' (start with _)
                not field_name.startswith('_')
                # Filter 'id' (should only be provided via URL path)
                and not field_name == 'id'
                # Filter foreign keys
                and field_name not in self.foreign_key_field_names()
                and not field_name.endswith('_xlink'),
            vars(self).keys()
        ))
        data_transfer_object = {
            field: vars(self)[field]
            for field in my_updatable_fields
        }
        return convert_None_values_to_empty_str(data_transfer_object)

    @classmethod
    def from_DTO(cls, DTO_data: Dict, DTO_field_parsers: Dict = DEFAULT_DTO_FIELD_PARSERS) -> 'NetdotAPIDataclass':
        """Parse data retrieved from Netdot API into a NetdotAPIDataclass.

        Args:
            data_transfer_object (Dict): Dictionary of raw data returned from Netdot API.
            dto_field_parsers (Dict, optional): A dictionary holding field_name -> parse_field() functions. 
                This is useful for when data returned from the NetDot API is not a string but actually some other data type.
                Defaults to DEFAULT_STRING_PARSERS. By default, all fields are parsed as strings.
                field_name may contain a single wildcard at the begining, e.g. *_xlink will expand to used_by_xlink, owner_xlink, parent_xlink, etc... 

        Returns:
            NetdotAPIDataclass: The appropriate subclass of NetdotAPIDataclass.
        """
        if not DTO_data:
            return None
        data = dict(DTO_data.copy())
        if DTO_field_parsers:
            field_parsers = dict(DTO_field_parsers.copy())
            field_parsers.update(cls.infer_base_parsers())
            field_parsers.update(cls.expand_wildcard_parsers(field_parsers))
            for field_name, string_parser in field_parsers.items():
                try:
                    data[field_name] = string_parser(data[field_name])
                except KeyError as e:
                    # If it is a KeyError indicating 'DTO was missing just this field', just log a DEBUG msg
                    if field_name in e.args and len(e.args) == 1 and not field_name.startswith('_'):
                        logger.debug(
                            f'DTO recieved from NetDot missing {field_name} for {cls.__module__}.{cls.__name__}')
                except Exception as e:
                    if bool(data[field_name]) and data[field_name] != '0':
                        logger.warning(
                            f'Unable to parse {field_name} for {cls.__module__}.{cls.__name__}, value: {data[field_name]} (using {str(string_parser)}) Error: {e}')
        return cls._parse_data_transfer_obj(data)

    @classmethod
    def _parse_data_transfer_obj(cls, data_transfer_object):
        """Parse some data retrieved from Netdot into a proper NetdotAPIDataclass.

        Args:
            data_transfer_object (Dict): Dictionary of raw data returned from Netdot API.

        Returns:
            NetdotAPIDataclass: The appropriate subclass of NetdotAPIDataclass.
        """
        valid_fields = set(cls.__dataclass_fields__.keys())
        provided_fields = set(data_transfer_object.keys())
        cls._log_unused_fields(valid_fields, provided_fields, data_transfer_object)

        # Construct the new object!
        fields_to_parse = provided_fields.intersection(valid_fields)
        data_to_parse = {
            key: data_transfer_object[key] for key in fields_to_parse}
        return cls(**data_to_parse)

    @classmethod
    def _log_unused_fields(cls, valid_fields, provided_fields, data_transfer_object):
        unused_fields = provided_fields.difference(valid_fields)
        if unused_fields:
            # Always log a debug message with ALL the data
            unused_data = {
                key: data_transfer_object[key] for key in unused_fields}
            logger.debug(
                f'Unparsed data ({cls.__module__}.{cls.__name__}): {unused_data}')
            # If this is the first time we've seen these 'unused field(s)', then log a warning!
            if not unused_fields.issubset(cls._logged_unused_fields):
                cls._logged_unused_fields = cls._logged_unused_fields.union(unused_fields)
                logger.warning(
                    f'Unparsed fields (to resolve, add dataclass field(s) to {cls.__module__}.{cls.__name__}): {unused_data}')

    @classmethod
    def expand_wildcard_parsers(cls, DTO_field_parsers: Dict[str, Callable]) -> None:
        """Expand any 'wildcard' parsers.
        NOTICE: This method updates the provided Dict in place.

        If any of DTO_field_parsers starts with "*", they will be expandeFd to match any of the fields available in DTO_data.

        Example:

            Assume we have NatdotAPIDataclass FooAddress.

            >> from dataclasses import dataclass
            >> @dataclass()
            .. class FooAddress(NetdotAPIDataclass): 
            ..     local_addr: ipaddress.ip_address
            ..     mgmt_addr: ipaddress.ip_address

            >> DTO_field_parsers = { '*_addr': ipaddress.ip_address }

            >> FooAddress.expand_wildcard_parsers(DTO_field_parsers)
            {'local_addr': <function ip_address ...>, 'mgmt_addr': <function ip_address ...>}
        """
        def is_wildcard_pattern(field_name):
            return field_name.startswith('*') or field_name.endswith('*')
        wildcard_patterns = filter(is_wildcard_pattern, DTO_field_parsers)
        wildcard_parsers = {
            pattern: DTO_field_parsers[pattern] for pattern in wildcard_patterns}
        for wildcard_pattern, parser in wildcard_parsers.items():
            del DTO_field_parsers[wildcard_pattern]
            pattern = wildcard_pattern.strip('*')
            for actual_field_name in cls.__dataclass_fields__:
                if (wildcard_pattern.startswith('*')
                    and actual_field_name.endswith(pattern)
                    ) or (wildcard_pattern.endswith('*')
                          and actual_field_name.startswith(pattern)):
                    DTO_field_parsers[actual_field_name] = parser
        return DTO_field_parsers

    @classmethod
    def infer_base_parsers(cls) -> Dict[str, Callable]:
        return {
            field_name: dataclass_field.type
            for field_name, dataclass_field in cls.__dataclass_fields__.items()
            if dataclass_field.type is not str
        }

    @property
    def web_url(self) -> str:
        submenu_web_url = {
            'cable_plant': self.web_url2,
            'management': self.web_url1,
        }
        web_url_function = submenu_web_url[self.NETDOT_MENU_URL_PATH]
        return web_url_function()

    def web_url1(self) -> str:
        url_path = f'/{self.NETDOT_MENU_URL_PATH}/{self.NETDOT_TABLE_NAME.lower()}.html'
        return f'{self.server_url}{url_path}?id={self.id}'

    def web_url2(self) -> str:
        url_path = f'/{self.NETDOT_MENU_URL_PATH}/view.html'
        params = f'table={self.NETDOT_TABLE_NAME}&id={self.id}'
        return f'{self.server_url}{url_path}?{params}'

    @property
    def server_api_url(self):
        return self.repository.connection.netdot_api_url

    @property
    def server_url(self):
        return self.repository.connection.netdot_url

    @property
    def repository(self):
        return self._repository

    def with_repository(self, repository: 'netdot.Repository') -> 'NetdotAPIDataclass':
        """Add a repository to this object.

        Example:
            This can be used as a 'fluent builder API.'
            >> repository = 'not_actually_a_repo'
            >> from dataclasses import dataclass
            >> @dataclass
            >> class Borg(NetdotAPIDataclass):
            ..     pass
            >> b = Borg().with_repository(repository)
            >> b.repository
            'not_actually_a_repo'
        """
        self._repository = repository
        return self

    @classmethod
    def _generate_and_attach_my_setter_methods(cls):
        for xlink, xlink_dataclass in cls._related_classes().items():
            xlink_setter = cls._generate_xlink_setter(xlink, xlink_dataclass)
            cls._attach_methods([xlink_setter])

    @classmethod
    def _generate_and_attach_my_getter_methods(cls):
        for xlink, xlink_dataclass in cls._related_classes().items():
            xlink_loader = cls._generate_my_xlink_load_method(xlink, xlink_dataclass)
            xlink_getter = cls._generate_my_xlink_get_method(xlink, xlink_dataclass)
            cls._attach_methods([xlink_getter, xlink_loader])

    @classmethod
    def _generate_and_attach_others_getAll_methods(cls):
        """Generate all the 'load_XXXs' methods for classes that this class is referenced by.
        """
        for xlink, xlink_dataclass in cls._related_classes().items():
            xlink_loader = cls._generate_your_xlink_load_method(xlink, xlink_dataclass)
            xlink_getter = cls._generate_your_xlink_get_method(xlink, xlink_dataclass)
            xlink_dataclass._attach_methods([xlink_loader, xlink_getter])

    @staticmethod
    def _xlink_object_fieldname(xlink):
        return f'_{xlink}_obj'

    @classmethod
    def _generate_my_xlink_load_method(my_cls, xlink, other_cls):
        """Generate the `load_xlink()` method to be attached to cls. 

        E.g. will generate load_site() when xlink_dataclass is netdot.Site.
        """
        def xlink_loader(self: 'netdot.T') -> other_cls: 
            xlink_object_field = my_cls._xlink_object_fieldname(xlink)
            if not hasattr(self, xlink_object_field):
                xlink_id = getattr(self, f'{other_cls._xlink_field_name()}_xlink')  # TODO: Refactor/rethink the whole _xlink_field_name/XFIELD_ALIAS solution
                download_function_name = f'get_{other_cls._pep8_method_friendly_name()}'
                download_function = getattr(self.repository, download_function_name)
                downloaded_obj = download_function(xlink_id)
                setattr(self, xlink_object_field, downloaded_obj)                
            return getattr(self, xlink_object_field)
        xlink_loader.__doc__ = f"""Load the {other_cls.__name__}s associated to this {my_cls.__name__}.

            Returns:
                netdot.{other_cls.__name__}: The full {other_cls.__name__} object that is related to this {my_cls.__name__}.
            """
        xlink_loader.__name__ = f'load_{other_cls._pep8_method_friendly_name()}'
        return xlink_loader

    @classmethod
    def _generate_my_xlink_get_method(my_cls, xlink, other_cls):
        """Generate the `get_xlink()` method to be attached to cls. 

        E.g. will generate get_site() when xlink_dataclass is netdot.Site.
        """
        xlink_getter = my_cls._generate_my_xlink_load_method(xlink, other_cls)
        xlink_getter.__doc__ = f"""Get the {other_cls.__name__}s associated to this {my_cls.__name__}.

            > If the object is not cached, it will be downloaded. Equivilent to load_{other_cls._pep8_method_friendly_name()}.

            Returns:
                netdot.{other_cls.__name__}: The full {other_cls.__name__} object that is related to this {my_cls.__name__}.
            """
        xlink_getter.__name__ = f'get_{other_cls._pep8_method_friendly_name()}'
        return xlink_getter

    @classmethod
    def _generate_your_xlink_load_method(my_cls, xlink, other_cls):
        """Generate the `load_xlinks()` method to be attached to other_cls. 

        E.g. will generate load_devices() when my_cls is netdot.Device.
        """
        def xlink_loader(self) -> List['netdot.T']:
            # TODO Should this field be generated outside of this method? Otherwise, "site.devices" will literally not exist until 'site.load_devices()' is called. 
            # For now, we accept that AttributeErrors may occur!
            xlink_object_field = f'{xlink}s'
            if not hasattr(self, xlink_object_field):
                download_function_name = f'get_{my_cls._pep8_method_friendly_name()}s_by_{other_cls._pep8_method_friendly_name()}'
                download_function = getattr(self.repository, download_function_name)
                downloaded_data = download_function(self)
                setattr(self, xlink_object_field, downloaded_data)                
            return getattr(self, xlink_object_field)

        xlink_loader.__doc__ = f"""Load the {other_cls.__name__}s associated to this {my_cls.__name__}.

        Returns:
            List[netdot.{other_cls.__name__}]: The full {other_cls.__name__} object that is related to this {my_cls.__name__}.
        """
        xlink_loader.__name__ = f'load_{my_cls._pep8_method_friendly_name()}s'
        return xlink_loader

    @classmethod
    def _generate_your_xlink_get_method(my_cls, xlink, other_cls):
        """Generate the `get_xlinks()` method to be attached to dataclass. 

        E.g. will generate get_devices() when cls is netdot.Device.
        """
        xlink_getter = my_cls._generate_your_xlink_load_method(xlink, other_cls)
        xlink_getter.__doc__ = f"""Get the {other_cls.__name__}s associated to this {my_cls.__name__}.

        Returns:
            List[netdot.{other_cls.__name__}]: The full {other_cls.__name__} object that is related to this {my_cls.__name__}.
        """
        xlink_getter.__name__ = f'load_{my_cls._pep8_method_friendly_name()}s'
        return xlink_getter

    @classmethod
    def _generate_xlink_setter(my_cls, xlink, other_cls):
        """Generate the `with_xlinks()` method to be attached to dataclass. 

        E.g. will generate with_device() when dataclass is netdot.Device.
        """
        def xlink_setter(self: 'netdot.T', entity: other_cls) -> 'netdot.T':
            setattr(self, my_cls._xlink_object_fieldname(xlink), entity)
            return self
        xlink_setter.__doc__ = f"""Set the {other_cls.__name__}s associated to this {my_cls.__name__}.

                Args:
                    entity ({other_cls.__name__}): The entity that is related to this {my_cls.__name__}.

                Returns:
                    netdot.{my_cls.__name__}: This object, to enable method chaining, e.g. to build objects.
                """
        xlink_setter.__name__ = f'with_{other_cls._pep8_method_friendly_name()}'
        return xlink_setter
