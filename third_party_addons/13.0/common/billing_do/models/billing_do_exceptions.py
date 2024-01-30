# -*- coding: utf-8 -*-

class ConnectionError(Exception):

    def __init__(self, message):
        super(ConnectionError, self).__init__(message)

class UrlNotFoundError(Exception):

    def __init__(self, message):
        super(UrlNotFoundError, self).__init__(message)

class BadRequestException(Exception):

    def __init__(self, message):
        super(BadRequestException, self).__init__(message)

class NotFound(Exception):

    def __init__(self, message, model):
        super(NotFound, self).__init__(message)
        self.model = model