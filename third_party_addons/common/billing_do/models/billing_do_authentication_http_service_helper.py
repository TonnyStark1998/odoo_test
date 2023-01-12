# -*- coding: utf-8 -*-

import logging as log

from odoo\
    import models, exceptions

class BillingDoAuthenticationHttpServiceHelper(models.AbstractModel):
    _name = "billing.do.authentication.http.service.helper"
    _inherit = "billing.do.http.service.helper"
    _description = "Billing DO - Authentication HTTP Service Helper"

    def get_request_headers(self):
        return {
            "Cache-Control":"max-age=3600"
        }