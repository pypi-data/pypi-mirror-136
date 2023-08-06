#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python API / v4yve.corp
# v4yve-api.py
# VK: https://vk.com/v4yve

# /IMPORTS/
from uuid import uuid4
from v4API import v4APIError, ArgumentError, InvalidTokenError, OverridingEx
import requests
import threading
import time


class v4API(object):
    """
    Class v4API for project 'v4yve.corp'
    """

    def __init__(self, token, login, delay=1):
        """
        Class __init__
        
        :type token: str
        :type login: str
        :type delay: int
        
        :param token: v4API token
        :param login: Your nick
        :param delay: Loop sleep time
        """
        
        self._s = requests.Session()
        self._s.headers['Accept'] = 'application/json'
        self._s.headers['Content-Type'] = 'application/json'
        self._s.headers['Authorization'] = 'Bearer ' + token
        self.login = login
        self._inv = {}
        self._echo = None
        self.delay = delay
        self.thread = False
    
    def _async_loop(self, target):
      lock = threading.Lock()
      
      while self.thread:
        try:
          lock.acquire()
          
          target()
        finally:
          lock.release()
    
    def _parse_account_info(self):
      accounts = self.accounts
      
      if "errorCode" in accounts:
        time.sleep(10)
        return
      # Получение всех данных от аккаунта 
      
      time.sleep(self.delay)
      
    def info(self):
      info = """
      v4API - api для проекта [v4yve.corp]
      Подробнее о функциях -> help
      Документация -> http://b926723z.beget.tech/api/doc
      """
      print(info)
      
    def start(self):
      """
      Start thread
      """
      
      if not self.thread:
        self.thread = True
        th = threading.Thread(target=self._async_loop, args=(self.info,))
        th.start()
        
    def stop(self):
      """
      Stop thread
      """
      self.thread = False
      
    
# END v4API