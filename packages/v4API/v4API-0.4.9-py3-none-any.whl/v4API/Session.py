#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python API / v4yve.corp
# v4yve-api.py
# VK: https://vk.com/v4yve

# /IMPORTS/
from uuid import uuid4
from v4API import v4APIError, ArgumentError, InvalidTokenError, OverridingEx, SCodeEx
import requests
import threading
import time
import json


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
        
        self.login = login
        self.url = "http://b926723z.beget.tech/api/api"
        self.token = token
        self.delay = delay
        self.thread = False
    
    def _async_loop(self, target):
      lock = threading.Lock()
      
      while self.thread:
        try:
          lock.acquire()
          
          target()
          time.sleep(self.delay)
        finally:
          lock.release()
    
    @property
    def _id(self):
      return str(int(time.time() * 1000))
      
      
    def _account(self):
      
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
      
    def help(self):
      info = """
      token > Проверить валидность токена
      acc/account > Показать информацию об аккаунте
      discord > Модуль API дискорд-бота
      telegram > Модуль API телеграм-бота
      vk > Модуль API вк-бота
      """
      print(info)
      
    def check_logon(self):
      headers = {
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
      }
      
      args = [
        ('id', str(self._id)),
        ('method', "v4-api-oauth"),
        ('login', str(self.login)),
        ('token', str(self.token)),
        ("returns", "code")
      ]
      
      response = requests.post(url=self.url, headers=headers, data=args)
      
      print(response.status_code)
      if response.status_code != 200:
        result = SCodeEx(code=response.status_code)
        return result.__raise__()
      else:
        data = response.text
        print(data)
      
    def start(self):
      """
      Start thread
      """
      
      if not self.thread:
        self.thread = True
        th = threading.Thread(target=self._async_loop, args=(self.check_logon,))
        th.start()
        
    def stop(self):
      """
      Stop thread
      """
      self.thread = False
      
class DiscordV4(object):
    """
    Class v4API.DiscordV4 for project 'v4yve.corp'
    """
  
    def __init__(self, token, login):
      """
      Class __init__
      
      :type token: str
      :type login: str
      
      :param token: v4API token
      :param login: Your nick
      """
      
      self._s = requests.Session()
      self._s.headers['Accept'] = 'application/json'
      self._s.headers['Content-Type'] = 'application/json'
      self._s.headers['Authorization'] = 'Bearer ' + token
      self.token = token
      self.login = login
    
    def oauth(self):
      token = self.token
      login = self.login
      print("DiscordV4 is in beta-testing")
  
# END v4API