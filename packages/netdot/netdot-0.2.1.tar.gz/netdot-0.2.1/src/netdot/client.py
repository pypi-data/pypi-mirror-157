import logging
import textwrap
import xml.etree.ElementTree as ET
from contextlib import AbstractContextManager
from typing import Any, Dict, List

import requests

from . import exceptions, parse, trace, validate

logger = logging.getLogger(__name__)


# TODO Eventually collapse v1 into the "Client" class below -- or make this into a different layer entirely
class Client_v1(AbstractContextManager):
    """NetDot Client_v1 (to be deprecated) -- provides access to NetDot data directly as dicts.
    """

    def __init__(self, server, username, password, verify_ssl=True, timeout=None):
        """Connect to a Netdot Server to begin making API requests.
        """
        self.user = username
        self.timeout = timeout
        self.http = requests.session()
        self.http.verify = verify_ssl
        self.http.headers.update({
            'User_Agent': 'Netdot::Client::REST/self.version',
            'Accept': 'text/xml; version=1.0'
        })

        # Setup URLs
        self.server = server
        self.base_url = f'{server}/rest'
        self.login_url = f'{server}/NetdotLogin'
        self.logout_url = f'{server}/logout.html'

        # Actually login (and load a test page)
        self._login(username, password)

    def __exit__(self):
        self.logout()
        self.http.close()

    def _login(self, username, password):
        """Log into the NetDot API with provided credentials.
        Stores the generated cookies to be reused in future API calls.
        """
        params = {
            'destination': 'index.html',
            'credential_0': username,
            'credential_1': password,
            'permanent_session': 1
        }
        response = self.http.post(
            self.login_url, data=params, timeout=self.timeout)
        if response.status_code != 200:
            raise exceptions.NetdotLoginError(
                f'Invalid credentials for user: {username}')

    def logout(self):
        """
        Logout of the NetDot API
        """
        self.http.post(self.logout_url, timeout=self.timeout)

    def get_xml(self, url):
        """
        This function provides a simple interface
        into the "GET" function by handling the authentication
        cookies as well as the required headers and base_url for
        each request.

        Arguments:
          url -- Url to append to the base url

        Usage:
          response = netdot.Client.get_xml("/url")

        Returns:
          XML string output from Netdot
        """
        response = self.http.get(self.base_url + url, timeout=self.timeout)
        logger.debug(f'HTTP Response: {response}')
        response.raise_for_status()
        return response.content

    def get(self, url):
        """
        This function delegates to get_xml() and parses the
        response xml to return a dict

        Arguments:
          url -- Url to append to the base url

        Usage:
          dict = netdot.Client.get("/url")

        Returns:
          Result as a multi-level dictionary on success.
        """
        return parse.RESTful_XML(self.get_xml(url))

    def get_object_by_filter(self, object, field, value):
        """
        Returns a multi-level dict of an objects (device, interface, rr, person)
        filtered by an object field/attribute
        Arguments:
          object -- NetDot object ID
          field -- NetDot field/attribute of object
          value -- The value to select from the field.

        Usage:
          response = netdot.Client.get_object_by_filter(device, name, some-switch)

        Returns:
          Multi-level dictionary on success
        """
        url = "/{}?{}={}".format(object, field, value)
        return self.get(url)

    def post(self, url, data):
        """
        This function provides a simple interface
        into the "POST" function by handling the authentication
        cookies as well as the required headers and base_url for
        each request.

        Arguments:
          url -- Url to append to the base url
          data -- dict of key/value pairs that the form requires

        Usage:
          response = netdot.Client.post("/url", {form-data})

        Returns:
          Result as a multi-level dictionary on success
        """
        response = self.http.post(
            self.base_url + url, data=data, timeout=self.timeout)
        logger.debug(f'HTTP Response: {response}')
        response.raise_for_status()
        validate.XML(response.content)
        # TODO: Don't we want to parse this similar to in get()?
        return response.content

    def delete(self, url):
        """
        This function provides a simple interface
        into the "HTTP/1.0 DELETE" function by handling the authentication
        cookies as well as the required headers and base_url for
        each request.

        Arguments:
          url -- Url to append to the base url

        Usage:
          response = netdot.Client.delete("/url")

        Returns:
          Result as an empty multi-level dictionary
        """
        response = self.http.delete(self.base_url + url, timeout=self.timeout)
        logger.debug(f'HTTP Response: {response}')
        response.raise_for_status()
        # TODO: Don't we want to parse this similar to in get()?
        return response.content

    def create_object(self, object, data):
        """
        Create object record when it's parameters are known.
        Parameters are passed as key:value pairs in a dictionary

        Arguments:
          data -- key:value pairs applicable for an object:
                  (e.g. a device below)
                name:                 'devicename'
                snmp_managed:         '0 or 1'
                snmp_version:         '1 or 2 or 3'
                community:            'SNMP community'
                snmp_polling:         '0 or 1'
                canautoupdate:        '0 or 1'
                collect_arp:          '0 or 1'
                collect_fwt:          '0 or 1'
                collect_stp:          '0 or 1'
                info:                 'Description string'

        Usage:
          response = netdot.Client.create_device("device",
                                                 {'name':'my-device',
                                                  'snmp_managed':'1',
                                                  'snmp_version':'2',
                                                  'community':'public',
                                                  'snmp_polling':'1',
                                                  'canautoupdate':'1',
                                                  'collect_arp':'1',
                                                  'collect_fwt':'1',
                                                  'collect_stp':'1',
                                                  'info':'My Server'}

        Returns:
          Created record as a multi-level dictionary.
        """
        return self.post("/" + object, data, timeout=self.timeout)


class Client(Client_v1):
    """NetDot Client (v2) -- provides access to NetDot data directly as dicts.
    """

    def __init__(self, *args, times_to_retry=3, **kwargs):
        self._retries = times_to_retry
        super().__init__(*args, **kwargs)

    @property
    def netdot_api_url(self) -> str:
        return self.base_url

    @property
    def netdot_url(self) -> str:
        return self.server

    def get_xml(self, url_path: str) -> bytes:
        #
        # Override get_xml to decorate it with a 'download tracker'.
        #
        ENCODING = 'UTF-8'
        response = super().get_xml(url_path)
        trace.netdot_downloads(len(response))
        try:
            return response.decode(ENCODING)
        except UnicodeDecodeError:
            logger.warning(f'Unable to decode {ENCODING} data: {response}')
            return response

    def get(self, url_path: str) -> Dict:
        """Get some data from Netdot REST API.

        Arguments:
            url_path: Path to append to the base url.

        Returns:
            Dict: Result as a multi-level dictionary on success.
        """
        return self._get_with_retries(url_path, times_to_retry=self._retries)

    def _get_with_retries(self, url_path: str, times_to_retry: int):
        """Wrapper around super().get. Retry the get request if it fails.
        """
        try:
            return self._get_convert_404_to_empty(url_path)
        except requests.exceptions.RequestException as e:
            if times_to_retry > 0:
                logger.warning(
                    f"Request failed due to {type(e)}. Will retry {times_to_retry} more times. (endpoint: {url_path}).")
                logger.debug(str(e))
                return self._get_with_retries(url_path, times_to_retry - 1)
            else:
                raise e

    def _get_convert_404_to_empty(self, url_path: str):
        """Wrapper around super().get. Ensures that 'empty' is returned instead of 404.
        """
        try:
            return super().get(url_path)
        except requests.exceptions.HTTPError as http_error:  # 404 response means 'no entries found'
            if http_error.response.status_code == 404:
                logger.debug(
                    f"Got 404 response GETing: {self.base_url}{url_path} \n"
                    + "⇒ Implies 'no entries found'. Returning empty."
                )
                return dict()
            else:
                raise http_error

    def get_object_by_filter(self, table: str, column: str, search_term: Any) -> List[Dict]:
        """Filter records from a table. Retrieve all the records from the "table" that match the 
        provided "search_term", for "column".

        NOTE: HTTP 404 erros are logged and 'empty dict' is returned.

        Args:
            table (str): The table name of the table to be searched (in CamelCase).
            column (str): The column name of the column to be searched.
            search_term (Any): The particular id/str/value you are looking for in the table.

        Raises:
            http_error (requests.exceptions.HTTPError): For any (non 404) HTTP errors.

        Returns:
            List: A list of any objects that match "search_term" for "column" in "table".
        """
        data = super().get_object_by_filter(table, column, search_term)
        if len(data) > 1:
            logger.warning(textwrap.dedent(
                f'''Netdot API returned more data items than expected when attempting to 
                    SELECT {table} WHERE {column} == {search_term}.'''))

        if data:
            data = next(iter(data.values()))
            return list(data.values())
        return list()

    def get_object_by_id(self, table: str, id: int) -> Dict:
        """Retrieve the object from 'table' with the given 'id'.

        NOTE: HTTP 404 erros are logged and 'empty dict' is returned.

        Args:
            table (str): The table name of the table to be searched (in CamelCase).
            id (int): The particular id you are looking for in the table.

        Raises:
            http_error (requests.exceptions.HTTPError): For any (non 404) HTTP errors.

        returns
        """
        objects = self.get_object_by_filter(table, 'id', id)

        if len(objects) > 1:
            logger.error(f'Found multiple {table} with id={id}: {objects}')

        if objects:
            return objects[0]
        else:
            raise ValueError(f'Unable to find {table} with id: {id}')

    def get_all(self, table: str) -> List:
        all_data = self.get(f'/{table}')
        all_data = all_data[table]
        all_objects = list(all_data.values())
        return all_objects


#
# TODO Deprecate, and then eventually delete ze Connect class below.
#
class Connect:
    def __init__(self, username, password, server, debug=0):
        """
        Class constructor, instantiates a number of
        variables for use in the class.  Mainly the required
        NetDot HTTP headers and login form parameters.

        Usage:
          import netdot
          dot = netdot.Client.connect(username,
                                      password,
                                      "https://netdot.localdomain/netdot",
                                      debug)

        Returns: NetDot.client object.
        """

        self.debug = bool(debug)
        if self.debug:
            print("DEBUG MODE: ON")
        self.http = requests.session()
        self.http.verify = True

        self.server = server
        self.base_url = server + '/rest'
        self.login_url = server + '/NetdotLogin'
        self.timeout = 10
        self.retries = 3
        self.version = '0.1.0'
        self.http.headers.update({'User_Agent': 'Netdot::Client::REST/self.version',
                                  'Accept': 'text/xml; version=1.0'})
        # Call the _login() function
        self._login(username, password)

    def _login(self, username, password):
        """
        Internal Function. Logs into the NetDot API with provided credentials,
        stores the Apache generated cookies into the self object to be
        reused.

        Arguments:
          dict -- 'destination':'index.html',
                  'credential_0':username,
                  'credential_1':password,
                  'permanent_session':1
        """
        params = {'destination': 'index.html',
                  'credential_0': username,
                  'credential_1': password,
                  'permanent_session': 1}
        response = self.http.post(self.login_url, data=params)
        if response.status_code != 200:
            raise AttributeError('Invalid Credentials')

    def logout(self):
        """
        Logout of the NetDot API
        """
        response = self.http.post(self.server + '/logout.html')
        logger.debug(f'HTTP Response: {response}')

    def get_xml(self, url):
        """
        This function provides a simple interface
        into the "GET" function by handling the authentication
        cookies as well as the required headers and base_url for
        each request.

        Arguments:
          url -- Url to append to the base url

        Usage:
          response = netdot.Client.get_xml("/url")

        Returns:
          XML string output from Netdot
        """
        response = self.http.get(self.base_url + url)
        logger.debug(f'HTTP Response: {response}')
        response.raise_for_status()
        return response.content

    def get(self, url):
        """
        This function delegates to get_xml() and parses the
        response xml to return a dict

        Arguments:
          url -- Url to append to the base url

        Usage:
          dict = netdot.Client.get("/url")

        Returns:
          Result as a multi-level dictionary on success.
        """
        return parse.RESTful_XML(self.get_xml(url))

    def post(self, url, data):
        """
        This function provides a simple interface
        into the "POST" function by handling the authentication
        cookies as well as the required headers and base_url for
        each request.

        Arguments:
          url -- Url to append to the base url
          data -- dict of key/value pairs that the form requires

        Usage:
          response = netdot.Client.post("/url", {form-data})

        Returns:
          Result as a multi-level dictionary on success
        """
        response = self.http.post(self.base_url + url, data=data)
        logger.debug(f'HTTP Response: {response}')
        response.raise_for_status()
        validate.RESTful_XML(response.content)
        return response.content

    def delete(self, url):
        """
        This function provides a simple interface
        into the "HTTP/1.0 DELETE" function by handling the authentication
        cookies as well as the required headers and base_url for
        each request.

        Arguments:
          url -- Url to append to the base url

        Usage:
          response = netdot.Client.delete("/url")

        Returns:
          Result as an empty multi-level dictionary
        """
        response = self.http.delete(self.base_url + url)
        logger.debug(f'HTTP Response: {response}')
        response.raise_for_status()
        return response.content

    def get_host_by_ipid(self, id):
        """
        Given an Ipblock ID, returns the Ipblock and associated
        resource records' data

        Arguments:
          id -- NetDot Ipblock ID

        Usage:
          response = netdot.Client.get_host_by_ipid("1111")

        Returns:
          Multi-level dictionary on success.
        """
        return self.get("/host?ipid=" + id)

    def get_host_by_rrid(self, id):
        """
        Given a resource record ID, returns the
        RR's data

        Arguments:
          id -- NetDot RR ID

        Usage:
          response = netdot.Client.get_host_by_rrid("1111")

        Returns:
          Multi-level dictionary on success.
        """
        return self.get("/host?rrid=" + id)

    def get_host_by_name(self, name):
        """
        Given a RR name, returns the RR's data

        Arguments:
          name -- RR label (DNS name)

        Usage:
          response = netdot.Client.get_host_by_name("foo")

        Returns:
          Multi-level dictionary on success.
        """
        return self.get("/host?name=" + name)

    def get_ipblock(self, ipblock):
        """
        This function returns all of the host
        records from the provided IP block

        Arguments:
          ipblock - Subnet address in CIDR notation

        Usage:
          response = netdot.Client.get_ipblock('192.168.1.0/24')

        Returns:
          Array of NetDot-XML objects on success
        """
        return self.get("/host?subnet=" + ipblock)

    def get_host_address(self, address):
        """
        Given an IP address, returns the associated
        records' data

        Arguments:
          address -- IP Address in "dotted-quad" syntax

        Usage:
          response = netdot.Client.get_host_address("192.168.0.1")

        Returns:
          Multi-level dictionary on success.
        """
        return self.get("/host?address=" + address)

    def get_person_by_username(self, user):
        """
        Returns a single-level dict of the requested Username

        Arguments:
          user -- Desired username

        Usage:
          response = netdot.Client.get_person_by_username("user")

        Returns:
          Multi-level dictionary on success.
        """
        return self.get("/person?username=" + user)

    def get_person_by_id(self, id):
        """
        Returns a single-level dict of the requested user id

        Arguments:
          id -- Desired User ID

        Usage:
          response = netdot.Client.get_person_by_id("id")

        Returns:
          Multi-level dictionary on success.
        """
        xml = self.get_xml("/person?id=" + id)
        xml_root = ET.fromstring(xml)
        person = dict()

        for child in xml_root:
            person[id] = child.attrib
        return person

    def create_object(self, object, data):
        """
        Create object record when it's parameters are known.
        Parameters are passed as key:value pairs in a dictionary

        Arguments:
          data -- key:value pairs applicable for an object:
                  (e.g. a device below)
                name:                 'devicename'
                snmp_managed:         '0 or 1'
                snmp_version:         '1 or 2 or 3'
                community:            'SNMP community'
                snmp_polling:         '0 or 1'
                canautoupdate:        '0 or 1'
                collect_arp:          '0 or 1'
                collect_fwt:          '0 or 1'
                collect_stp:          '0 or 1'
                info:                 'Description string'

        Usage:
          response = netdot.Client.create_device("device",
                                                 {'name':'my-device',
                                                  'snmp_managed':'1',
                                                  'snmp_version':'2',
                                                  'community':'public',
                                                  'snmp_polling':'1',
                                                  'canautoupdate':'1',
                                                  'collect_arp':'1',
                                                  'collect_fwt':'1',
                                                  'collect_stp':'1',
                                                  'info':'My Server'}

        Returns:
          Created record as a multi-level dictionary.
        """
        return self.post("/" + object, data)

    def get_object_by_id(self, object, id):
        """
        Returns a single-level dict of the requested object and id

        Arguments:
          object -- 'device', 'person',  etc...
          id  --  Object ID

        Usage:
          response = netdot.Client.get_object_by_id("object", "id")

        Returns:
          Multi-level dictionary on success
        """
        return self.get("/" + object + "?id=" + id)

    def get_object_by_name(self, object, name):
        """
        Returns a multi-level dict of the requested object by name

        Arguments:
          object -- 'device', 'person',  etc...
          name  --  name

        Usage:
          response = netdot.Client.get_object_by_id("object", "name")

        Returns:
          Multi-level dictionary on success
        """
        return self.get("/" + object + "?name=" + name)

    def get_object_by_desc(self, object, desc):
        """
        Returns a multi-level dict of the requested object by
        description

        Arguments:
          object -- 'device', 'person',  etc...
          desc  --  Object description

        Usage:
          response = netdot.Client.get_object_by_desc("object", "desc")

        Returns:
          Multi-level dictionary on success
        """
        return self.get("/" + object + "?description=" + desc)

    def get_object_by_info(self, object, info):
        """
        Returns a multi-level dict of the requested object by
        description

        Arguments:
          object -- 'device', 'person',  etc...
          info  -- Comment Field

        Usage:
          response = netdot.Client.get_object_by_info("object", "info")

        Returns:
          Multi-level dictionary on success
        """
        return self.get("/" + object + "?info=" + info)

    def delete_object_by_id(self, object, id):
        """
        This function deletes an object record by it's id

        Arguments:
          object -- 'device', 'vlan', etc...
          id  -- Object ID

        Usage:
          response = netdot.Client.delete_object_by_id("device", "id")

        Returns:
        """
        return self.delete("/" + object + "/" + id)

    def get_contact_by_person_id(self, id):
        """
        Returns contact information for given person ID

        Arguments:
          id  --  person id

        Usage:
          response = netdot.Client.get_contact_by_person_id('id')

        Returns:
          Single-level dictionary on success
        """
        # xml = self.get_xml("/contact?person=" + id)
        # xml_root = ET.fromstring(xml)
        # person = dict()
        # for child in xml_root:
        #  person[id] = child.attrib
        return self.get('/contact?person=' + id)

    def get_contact_by_username(self, user):
        """
        Returns contact information for given person username

        Arguments:
          user  --  NetDot Username

        Usage:
          response = netdot.Client.get_contact_by_username("mary")

        Returns:
          Multi-level dictionary on success
        """
        person = self.get_person_by_username(user)['Person'].values()[0]
        return self.get_contact_by_person_id(person['id'])

    def get_grouprights_by_username(self, user):
        """
        Returns grouprights for a given username

        Arguments:
         user -- Netdot Username

        Usage:
         response = netdot.Client.get_accesrights_by_username("mary")
        """
        contacts = self.get_contact_by_username(user)
        groupright = {}

        for values in contacts['Contact'].values():
            try:
                gr = self.get_grouprights_by_conlist_id(
                    values['contactlist_xlink'].split('/')[1]).values()[0]
                groupright.update(gr)
            except requests.HTTPError:
                # there weren't any grouprights associated with that conlist. No big deal.
                pass

        return {'GroupRight': groupright}

    def get_accessright_by_id(self, id):
        """
        Returns accessrights for a given id

        Arguments:
         user -- Netdot Username

        Usage:
         response = netdot.Client.get_accessrights_by_id("id")
        """
        return self.get('/accessright/'+id)

    def get_accessrights_by_username(self, user):
        """
        Returns accessrights for a given user

        Arguments:
         user -- Netdot Username

        Usage:
         response = netdot.Client.get_accessrights_by_username("user")
        """
        accessrights = {}
        grouprights = self.get_grouprights_by_username(user)
        for vals in grouprights['GroupRight'].values():
            # some values return in the grouprights don't have an accessright_xlink
            if 'accessright_xlink' in vals:
                # split the accessright_xlink value to get the ID
                ar = self.get_accessright_by_id(
                    vals['accessright_xlink'].split('/')[1])
                accessrights.update({ar['id']: ar})
            else:
                pass
        return {'AccessRight': accessrights}

    def get_device_accessrights_by_username(self, user):
        """
        Returns devices rights for a given user

        Arguments:
         user -- Netdot Username

        Usage:
         response = netdot.Client.get_device_accessrights_by_username("user")
        """
        devices = {}
        accessrights = self.get_accessrights_by_username(user)
        for ars in accessrights['AccessRight'].values():
            if ars['object_class'] == 'Device':
                devices.update(self.get_object_by_id(
                    'Device', ars['object_id'])['Device'])
        return {'Device': devices}

    def get_grouprights_by_conlist_id(self, id):
        """
        Returns a single-level dict of the requested group's
        access rights

        Arguments:
          id  --  NetDot Contact List ID

        Usage:
          response = netdot.Client.get_grouprights_by_conlist_id("id")

        Returns:
          Multi-level dictionary on success
        """
        return self.get("/groupright?contactlist=" + id)

    def get_site(self, site=None):
        """
        Returns a single-level dict of sites

        Arguments:
          None

        Usage:
          response = netdot.Client.get_site()

        Returns:
          Multi-level dictionary on success

        """
        if site:
            return self.get("/site?name=" + site)
        else:
            return self.get("/site")

    def get_floors_by_site(self, site):
        """
        Returns a single-level dict of floors

        Arguments:
          Site ID

        Usage:
          response = netdot.Client.get_floors_by_site()

        Returns:
          Multi-level dictionary on success

        """
        return self.get_object_by_filter('floor', 'site', site)

    def get_rooms_by_floor(self, floor):
        """
        Returns a single-level dict of rooms

        Arguments:
          Site ID

        Usage:
          response = netdot.Client.get_rooms_by_floor()

        Returns:
          Multi-level dictionary on success

        """
        return self.get_object_by_filter('room', 'floor', floor)

    def get_closet_by_room(self, room):
        """
        Returns a single-level dict of closets

        Arguments:
          Site ID

        Usage:
          response = netdot.Client.get_closet_by_room()

        Returns:
          Multi-level dictionary on success

        """
        return self.get_object_by_filter('closet', 'room', room)

    def get_horizontalcable_by_room(self, room):
        """
        Returns a single-level dict of horizontalcables (jacks)

        Arguments:
          Site ID

        Usage:
          response = netdot.Client.get_closet_by_room()

        Returns:
          Multi-level dictionary on success

        """
        return self.get_object_by_filter('horizontalcable', 'room', room)

    def get_horizontalcable_by_closet(self, closet):
        """
        Returns a single-level dict of horizontalcables (jacks)

        Arguments:
          Site ID

        Usage:
          response = netdot.Client.get_closet_by_closet()

        Returns:
          Multi-level dictionary on success

        """
        return self.get_object_by_filter('horizontalcable', 'closet', closet)

    def add_cname_to_record(self, name, cname):
        """
        This fucntion will add a CNAME to an
        existing resource record or "A" record

        Arguments:
          name -- A record
          cname -- Desired CNAME

        Usage:
          response = dot.add_cname_to_record('foo.example.com', 'bar.example.com')
        """
        data = {'cname': cname}
        host = self.get_host_by_name(name)
        for key in host[name]['RR'].iterkeys():
            for attr, attr_val in host[name]['RR'][key].iteritems():
                if attr == 'name' and attr_val == name:
                    return self.post("/host?rrid=" + host['RR'][key]['id'], data)

    def rename_host(self, old, new):
        """
        This function will rename a host record.  Previously,
        the user had to query know the RRID of the record, then
        post the updated name to the RRID record.  This function
        automates the RRID search and constructs the post request
        for you.

        Arguments:
          old -- Old DNS shortname
          new -- New DNS shortname

        Usage:
          netdot.Client.rename_host('old-name','new-name')
        """
        host = self.get_host_by_name(old)
        rrid = host['RR']['id']
        data = {}
        data['name'] = new
        return self.post("/host?rrid=" + rrid, data)

    def create_host(self, data):
        """
        Create DNS records (and optionally) DHCP entries
        for a given IP address, using the given
        name and description.
        Passing a subnet address instead of an IP address,
        the function will create records for the next
        available IP address in the subnet.

        Arguments:
          data -- dict with the following key:value pairs:
                name:     'servername'
                address:  'IP'
                subnet:   'CIDR'
                ethernet: 'MAC'
                info:     'Description string'

        Usage:
          response = netdot.Client.create_host({'name':'my-server',
                                                'subnet':'192.168.1.0/24',
                                                'ethernet':'XX:XX:XX:XX:XX:XX',
                                                'info':'My Server'})

        Returns:
          Created record as a multi-level dictionary.
        """
        return self.post("/host", data)

    def delete_host_by_rrid(self, id):
        """
        This function deletes a hostname record
        for the requested RR ID. This also frees the IP.

        Arguments:
          rrid -- NetDot Resource Record ID

        Usage:
          response = netdot.Client.delete_host_by_rrid("1111")

        Returns:
        """
        return self.delete("/host?rrid=" + id)

    def delete_host_by_ipid(self, id):
        """
        This function deletes all hostname records
        for the requested Ipblock ID.

        Arguments:
          ipid -- NetDot Ipblock ID

        Usage:
          response = netdot.Client.delete_host_by_ipid("1111")

        Returns:
        """
        return self.delete("/host?ipid=" + id)

    def get_vlan(self, id=None):
        """Returns a multi-level dict of vlans

           Arguments:
             id -- vlan id

           Usage:
             response = netdot.Client.get_vlan(id)
        """
        if id:
            return self.get('/vlan/'+id)
        return self.get('/vlan')

    def get_vlans_by_groupid(self, id):
        """
        Returns a multi-level dict of vlans in a vlan group

        Arguments:
          id  --  vlan group id

        Usage:
          response = netdot.Client.get_object_by_id("id")

        Returns:
          Multi-level dictionary on success
        """
        return self.get("/vlan?VlanGroup=" + id)

    def get_object_by_filter(self, object, field, value):
        """
        Returns a multi-level dict of an objects (device, interface, rr, person)
        filtered by an object field/attribute
        Arguments:
          object -- NetDot object ID
          field -- NetDot field/attribute of object
          value -- The value to select from the field.

        Usage:
          response = netdot.Client.get_object_by_filter(device, name, some-switch)

        Returns:
          Multi-level dictionary on success
        """
        url = "/{}?{}={}".format(object, field, value)
        return self.get(url)

    def get_device_vlans(self, device):
        """
        Returns a multi-level dict of vlans that exist on the supplied device.

        Arguments:
          device == NetDot Device ID

        Usage:
          response = netdot.Client.get_device_vlans(device)

        Returns:
          Multi-level dictionary on success
        """
        # empty list to hold our results
        dev_vlans = []

        # get the interfaces associated with a device
        dev_ifaces = self.get_object_by_filter('interface', 'device', device)

        # interate through each interface and cross reference against the interfacevlan table
        for iface in dev_ifaces['Interface'].keys():
            try:
                iface_vlans = self.get_object_by_filter(
                    'interfacevlan', 'interface', iface)
                for iv in iface_vlans['InterfaceVlan'].keys():
                    if iface_vlans['InterfaceVlan'][iv]['vlan'] not in dev_vlans:
                        dev_vlans.append(
                            iface_vlans['InterfaceVlan'][iv]['vlan'])
            except requests.exceptions.HTTPError as e:
                # This is caused by SVI interfaces.  They don't have a Vlan
                # because they are Vlans...
                logger.debug(f'Ignoring HTTPError: {str(e)}')
                pass

        return {
            "Device": { 
                device: dev_vlans 
            }
        }

    def get_device_by_person(self, user):
        """
        Returns a multi-level dict for the device associated with a username.
        This association is done through the Entity table
        Person <-> Entity <-> Device

        Arguments:
          username - Desired username

        Usage:
          response = netdot.Client.get_device_by_person("user")

        Returns:
          Multi-level dictionary on success.
        """
        user_obj = self.get_person_by_username(user)
        # this oneliner grabs the entity_xlink reutrn in the "Person" dict and splits the values to get entity id
        user_ent_id = user_obj['Person'].values(
        )[0]['entity_xlink'].split('/')[1]

        return self.get_object_by_filter('device', 'owner', user_ent_id)
