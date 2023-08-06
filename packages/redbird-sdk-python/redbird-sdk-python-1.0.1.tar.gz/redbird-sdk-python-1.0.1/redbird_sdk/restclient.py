#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2020 wesley wu

try: import simplejson as json
except ImportError: import json
import requests
import requests.exceptions
from .exceptions import RedBirdAPIException, RedBirdRequestException,RedBirdResultErrorException


class RestClient(object):
    """Client interface for the RedBird REST API."""
    def __init__(self, api_Url, username=None, password=None, timeout=20, session=None, verify=True):
        """Create a RedBirdClient instance.
        :param str api_Url: url address, "http://x.x.x.x"
        :param str username: Basic auth username
        :param str password: Basic auth password
        :param requests.session session: requests.session for reusing the connections
        :param int timeout: Timeout (in seconds) for requests to RedBird
        """
        if session is None:
            self.session = requests.Session()
        else:
            self.session = session

        self.api_Url = api_Url
        self.auth = (username, password) if username and password else None
        self.verify = verify
        self.timeout = timeout

    def __repr__(self):
        return 'Connection:%s' % self.api_Url

    def _handle_response(self, response):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        # check http error
        if not str(response.status_code).startswith('2'):
            raise RedBirdAPIException(response)
        # check json error
        try:
            json = response.json()
        except ValueError:
            raise RedBirdRequestException('Invalid Response: %s' % response.text)
        # check result error
        if json['error'].strip():
            raise RedBirdResultErrorException(json['error'])
        #
        return json['data']

    def _request(self, method, path, params=None, data=None):
        """Query RedBird server."""
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = None
        url = ''.join([self.api_Url.rstrip('/'), path])
        response = self.session.request(
            method, url, params=params, data=data, headers=headers,
            auth=self.auth, timeout=self.timeout, verify=self.verify)
        return self._handle_response(response)

    def get(self, path, params=None, data=None):
        return self._request('get', path, params, data)

    def post(self, path, params=None, data=None):
        return self._request('post', path, params, data)

    def put(self, path, params=None, data=None):
        return self._request('put', path, params, data)

    def delete(self, path, params=None, data=None):
        return self._request('delete', path, params, data)
