# -*- coding: utf-8 -*-

import logging as log,\
        datetime as datetime

from odoo import models,\
                    exceptions,\
                    _

from . import billing_do_exceptions as bexceptions

class BillingDoCurrencyRateHttpServiceHelper(models.AbstractModel):
    _name = 'billing.do.currency.rate.http.service.helper'
    _inherit  = 'billing.do.authentication.http.service.helper'
    _description = 'Billing DO - Currency Rate HTTP Service Helper'

    def get_currency_rates_for_today(self):
        config = self.env['ir.config_parameter'].sudo()
        _currency_rates_switch = config.get_param('billing_do.api_services_currency_rates_switch')

        log.info("[KCS] Service Rates Switch: {0}"
                    .format(_currency_rates_switch))
        
        if _currency_rates_switch:
            log.info("[KCS] Common Api Base URL: {0}".format(config.get_param('billing_do.api_services_base_url')))
            log.info("[KCS] Service Currency Rates Endpoint: {0}".format(config.get_param('billing_do.api_services_currency_rates_endpoint')))
            
            currency_rates = []

            response = self.send_request("{0}/{1}/today".format(config\
                                                                    .get_param('billing_do.api_services_base_url'),
                                                                config\
                                                                    .get_param('billing_do.api_services_currency_rates_endpoint')),
                                            http_method=self.HTTP_METHODS['get'],
                                            headers=self.get_request_headers())

            log.info("[KCS] Request: {0}"
                        .format(response))
            log.info("[KCS] Request (Status Code): {0}"
                        .format(response.status_code))

            if response.status_code == 200:
                currency_rates = list(response.json())
            elif response.status_code == 404:
                raise bexceptions.UrlNotFoundError(_('URL for querying the Currencies Rates is misconfigured or not exist. Check with your administrator.'))
            elif response.status_code == 400:
                raise bexceptions.BadRequestException(_('Something went wrong while querying the Currencies Rates service. Check with your administrator.'))
            else:
                raise bexceptions.ConnectionError(_('There was a Connection problem while querying the Currencies Rates service. Check with your administrator.'))

            return currency_rates
        
        else:
            log.warning(_('{} Automatically loading of Currencies is disabled.').format('[KCS]'))