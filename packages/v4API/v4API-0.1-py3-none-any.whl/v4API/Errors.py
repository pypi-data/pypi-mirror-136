#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python API / v4yve.corp
# v4yve-api.py
# VK: https://vk.com/v4yve

class v4APIError(Exception):
  pass


class ArgumentError(Exception):
  pass


class InvalidTokenError(Exception):
  pass


class OverridingEx(Exception):
  pass