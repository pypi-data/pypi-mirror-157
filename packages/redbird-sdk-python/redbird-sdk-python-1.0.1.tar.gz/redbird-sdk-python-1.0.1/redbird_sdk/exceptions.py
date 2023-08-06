#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2020 wesley wu


class RedBirdAPIException(Exception):

    def __init__(self, response):
        self.code = 0
        try:
            json_res = response.json()
        except ValueError:
            self.message = 'Invalid JSON error message from RedBird: {}'.format(response.text)
        else:
            self.code = json_res['code']
            self.message = json_res['msg']
        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s' % (self.code, self.message)


class RedBirdResultErrorException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'RedBirdResultErrorException: %s' % self.message


class RedBirdRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'RedBirdRequestException: %s' % self.message