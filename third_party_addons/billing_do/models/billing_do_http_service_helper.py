# -*- coding: utf-8 -*-

import re, requests

from odoo import models, exceptions

class BillingDoHttpServiceHelper(models.AbstractModel):
    _name = "billing.do.http.service.helper"
    _description = """
    
    """

    HTTP_METHODS = dict({
        "get": "GET",
        "post": "POST",
    })

    def send_request(self, request_uri, http_method = HTTP_METHODS['get'], headers = {}, data = {}):
        if http_method == self.HTTP_METHODS['get']:
            response = requests.get(request_uri,
                                        headers=headers)
        elif http_method == self.HTTP_METHODS['post']:
            response = requests.post(request_uri,
                                        headers=headers,
                                        data=data)

        return response
