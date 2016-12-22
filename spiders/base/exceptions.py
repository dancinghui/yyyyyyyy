#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

class SpiderErrors:
    class FatalError(Exception):
        pass
    class RetryError(Exception):
        pass

class AccountErrors:
    class NoAccountError(Exception):
        pass

class LoginErrors:
    class RetryError(Exception):
        pass
    class NeedLoginError(Exception):
        pass
    class AccountHoldError(Exception):
        pass