# -*- coding: utf-8 -*-

"""

sadism - Simplified Active Directory Information Search Mechanism

Provide an Active Directory connector
for simplified information search

"""


import logging
import re

from typing import Dict, List, Optional, Tuple

import ldap
import ldap.dn


__version__ = "0.3.0"


#
# Exceptions
#


class NoResultsError(Exception):

    """Raised when a search returned zero results"""


class TooManyResultsError(Exception):

    """Raised when a search returned more results than expected"""


#
# Base class
#


class Connector:

    """Class for Active Directory access"""

    ldap_url: str = "ldaps://ldap.example.com:3269"
    user_search_base_dn: str = "dc=example,dc=com"
    user_search_attribute: str = "uid"
    prx_user_id = re.compile("^([a-z0-9]+)", re.IGNORECASE)
    search_timeout: int = 2
    attributes_timeout: int = 1

    def __init__(
        self,
        bind_dn: Optional[str] = None,
        bind_password: Optional[str] = None,
        cacerts_file: Optional[str] = None,
    ) -> None:
        """Set credentionals of the bind user internally,
        and tell the LDAP client to use <cacerts_file>
        for server certificate validation if provided.

        :param bind_dn: the distinguished name of the bind user
        :param bind_password: the password of the bind user
        :param cacerts_file: path of a file with CA certificates
            in PEM format, for use of ldaps:// URLs using
            certificates issued by a private CA.
            This file must contain the private CA's root certificate
            as well as all intermediate CA certificates.
        :raises: ldap.DECODING_ERROR if bind_dn was provided,
            but is not a valid distinguished name
        """
        self.__bind_user_dn: Optional[str] = None
        self.__bind_user_password: Optional[str] = None
        self.__next_bind_dn: Optional[str] = None
        self.__next_bind_password: Optional[str] = None
        try:
            dn_probe = ldap.dn.str2dn(bind_dn)
        except ldap.DECODING_ERROR as error:
            logging.error("%r is not a valid LDAP DN!", bind_dn)
            raise error
        #
        if dn_probe:
            self.__bind_user_dn = bind_dn
            self.__bind_user_password = bind_password
        #
        self.set_bind_user()
        if cacerts_file:
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, cacerts_file)
        #

    def set_bind_user(
        self, user_dn: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """Set DN and password for all following LDAP bind(s).
        If no bind_dn was provided, use the internally stored
        DN and password of the bind user

        :param user_dn: the distinguished name of the bind user
        :param password: the password of the bind user
        """
        if user_dn is None:
            self.__next_bind_dn = self.__bind_user_dn
            self.__next_bind_password = self.__bind_user_password
        else:
            self.__next_bind_dn = user_dn
            self.__next_bind_password = password
        #

    def bind_and_search(
        self,
        *attrs: str,
        base: Optional[str] = None,
        scope: int = ldap.SCOPE_SUBTREE,
        filterstr: str = "(objectClass=*)",
        timeout: Optional[int] = None,
    ) -> list[Tuple[str, Dict[str, List[str]]]]:
        """Connect to the LDAP server, bind using the DN and password
        previously set using self.__set_bind_user(),
        search, unbind and return the results

        The parameters are the same as the likewise named paramters
        of ldap.LDAPObject.search_st() as documented in
        <https://www.python-ldap.org/en/python-ldap-3.4.0
         /reference/ldap.html#ldap.LDAPObject.search_st>

        :param attrs: (* star-arguments) names of the requested attributes
        :param base: the base DN to search,
            defaults to the class or instance attribute user_search_base_dn
        :param scope: the scope of the search,
            defaults to ldap.SCOPE_SUBTREE
        :param filterstr: the filter string to use,
            defaults to "(objectClass=*)"
        :param timeout: timeout in seconds (-1 = no timeout),
            defaults to the class or instance attribute search_timeout
        :returns: the results in a list
        :raises: ldap.LDAPError
        """
        ldap_client = ldap.initialize(self.ldap_url)
        ldap_client.set_option(ldap.OPT_REFERRALS, 0)
        bind_dn: Optional[str] = self.__next_bind_dn
        password: Optional[str] = self.__next_bind_password
        if bind_dn != self.__bind_user_dn:
            scope = ldap.SCOPE_BASE
        #
        try:
            ldap_client.simple_bind_s(bind_dn, password)
        except ldap.INVALID_CREDENTIALS as error:
            ldap_client.unbind()
            logging.error("%s: Wrong bind DN or password", bind_dn)
            raise error
        #
        results: List = ldap_client.search_st(
            base or self.user_search_base_dn,
            scope,
            filterstr=filterstr,
            attrlist=list(attrs),
            attrsonly=0,
            timeout=timeout or self.search_timeout,
        )
        ldap_client.unbind_s()
        return results

    def sanitized(self, user_id: str) -> str:
        """Connect to the LDAP server, bind using the bind user DN
        and password, search <user_id> with timeout (default: 1 second),
        unbind and return the results

        :param user_id: the user ID to be sanitized
        :returns: the sanitized user ID
        :raises: ValueError on invalid user IDs
        """
        user_id_match = self.prx_user_id.match(user_id)
        if not user_id_match:
            raise ValueError(f"{user_id} does not contain a valid user ID!")
        #
        return user_id_match.group(1)

    def get_own_attributes(
        self,
        user_dn: str,
        password: str,
        *attrs: str,
        timeout: Optional[int] = None,
    ) -> Dict[str, List[str]]:
        """Connect to the LDAP server,
        bind with user_dn, and return the requested attributes of user_dn

        :param user_dn: the user DN
        :param password: the password of the user
        :param attrs: (* star-arguments) names of the requested attributes
        :param timeout: timeout in seconds (-1 = no timeout)
            for the attribute(s) retrieval,
            defaults to the class or instance attribute attributes_timeout
        :returns: the resulting attributes as a dict
        :raises: ldap.LDAPError, especially ldap.INVALID_CREDENTIALS
        """
        self.set_bind_user(user_dn, password)
        attributes_results: List = self.bind_and_search(
            *attrs,
            base=user_dn,
            scope=ldap.SCOPE_BASE,
            timeout=timeout or self.attributes_timeout,
        )
        return attributes_results[0][1]

    def get_user_attributes(
        self,
        user_id: str,
        password: str,
        *attrs: str,
        search_timeout: Optional[int] = None,
        attributes_timeout: Optional[int] = None,
    ) -> Dict[str, List[str]]:
        """Connect to the LDAP server,
        find the user's DN using self.bind_and_search(),
        bind with the user's DN, and return the requested attributes

        :param user_id: the user ID determining the user DN
        :param password: the password of the user
        :param attrs: (* star-arguments) names of the requested attributes
        :param search_timeout: timeout in seconds (-1 = no timeout)
            for the user DN search,
            defaults to the class or instance attribute search_timeout
        :param attributes_timeout: timeout in seconds (-1 = no timeout)
            for the attribute(s) retrieval,
            defaults to the class or instance attribute attributes_timeout
        :returns: the resulting attributes as a dict
        :raises: ldap.LDAPError, especially ldap.INVALID_CREDENTIALS,
            NoResultsError if no user was found,
            of TooMnyResultsError if mote than one user was found.
        """
        sanitized_user_id: str = self.sanitized(user_id)
        self.set_bind_user()
        search_results: List = self.bind_and_search(
            self.user_search_attribute,
            base=self.user_search_base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=f"({self.user_search_attribute}={sanitized_user_id})",
            timeout=search_timeout,
        )
        if not search_results:
            raise NoResultsError
        #
        if len(search_results) > 1:
            raise TooManyResultsError
        #
        user_dn: str = search_results[0][0]
        return self.get_own_attributes(
            user_dn, password, *attrs, timeout=attributes_timeout
        )


# vim:fileencoding=utf-8 autoindent ts=4 sw=4 sts=4 expandtab:
