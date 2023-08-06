#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2020 wesley wu

import re


def to_camel_case(snake_str):
    words = snake_str.split('_')
    return words[0] + ''.join(w.capitalize() for w in words[1:])


def to_snake_case(camel_str):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def str_to_int(s):
    if isinstance(s, int):
        return s
    s = s.strip()
    return int(s) if s else 0


def str_to_float(s):
    if isinstance(s, float):
        return s
    s = s.strip()
    return float(s) if s else 0.0
