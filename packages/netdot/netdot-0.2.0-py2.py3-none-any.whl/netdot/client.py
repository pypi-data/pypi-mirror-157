from __future__ import absolute_import

import logging
import re
import textwrap
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
        response = self.http.post(self.login_url, data=params, timeout=self.timeout)
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
        response = self.http.post(self.base_url + url, data=data, timeout=self.timeout)
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
                logger.warning(f"Request failed due to {type(e)}. Will retry {times_to_retry} more times. (endpoint: {url_path}).")
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
