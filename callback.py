#!/usr/bin/env python
# -*- coding:utf8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json

import logging
import logging.handlers

import socket

import requests
import hashlib

from ansible.plugins.callback import CallbackBase


def log2callback(host, result_status, data, classify=''):
    accept_key = '<M(^BJB<*&RGKJKLSO'
    callback_url = 'http://127.0.0.1:8000/log/callback'
    result = json.loads(data)
    headers = {'content-type': 'application/json'}
    m1 = hashlib.md5()
    m1.update(accept_key + host)
    result['access_token'] = m1.hexdigest()
    result['result_status'] = result_status
    result['host'] = host
    result['classify '] = classify
    requests.post(callback_url, data=json.dumps(result), headers=headers)


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'file_or_callback'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):

        super(CallbackModule, self).__init__()

        self.logger = logging.getLogger('ansible logger')
        self.logger.setLevel(logging.DEBUG)
        log_file = '/data/logs/ansible.log'
        if not os.path.isdir(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))
        self.handler = logging.handlers.RotatingFileHandler(log_file,
                                                              mode='a+',
                                                              maxBytes=1073741824,#1G
                                                              backupCount=5)
        self.handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)-8s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s'))
        self.logger.addHandler(self.handler)
        self.hostname = socket.gethostname()

    def runner_on_failed(self, host, res, ignore_errors=False):
        self.logger.error(
            '%s ansible-command: task execution FAILED; host: %s; message: %s'
            % (self.hostname, host, self._dump_results(res)))
        log2callback(host,
                     0,
                     self._dump_results(res),
                     classify='runner_on_failed')

    def runner_on_ok(self, host, res):
        self.logger.info(
            '%s ansible-command: task execution OK; host: %s; message: %s' %
            (self.hostname, host, self._dump_results(res)))
        log2callback(host, 1, self._dump_results(res), classify='runner_on_ok')

    def runner_on_skipped(self, host, item=None):
        self.logger.info(
            '%s ansible-command: task execution SKIPPED; host: %s; message: %s'
            % (self.hostname, host, 'skipped'))
        log2callback(host,
                     0,
                     self._dump_results({'skipped': 'skipped'}),
                     classify='runner_on_skipped')

    def runner_on_unreachable(self, host, res):
        self.logger.error(
            '%s ansible-command: task execution UNREACHABLE; host: %s; message: %s'
            % (self.hostname, host, self._dump_results(res)))
        log2callback(host,
                     0,
                     self._dump_results(res),
                     classify='runner_on_unreachable')

    def runner_on_async_failed(self, host, res):
        self.logger.error(
            '%s ansible-command: task execution FAILED; host: %s; message: %s'
            % (self.hostname, host, self._dump_results(res)))
        log2callback(host,
                     0,
                     self._dump_results(res),
                     classify='runner_on_async_failed')

    def playbook_on_import_for_host(self, host, imported_file):
        self.logger.info(
            '%s ansible-command: playbook IMPORTED; host: %s; message: imported file %s'
            % (self.hostname, host, imported_file))

    def playbook_on_not_import_for_host(self, host, missing_file):
        self.logger.info(
            '%s ansible-command: playbook NOT IMPORTED; host: %s; message: missing file %s'
            % (self.hostname, host, missing_file))
