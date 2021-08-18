# -*- coding: utf-8 -*-

import logging as log
import datetime as datetime

from odoo import models,\
                    fields,\
                    exceptions,\
                    _

from . import billing_do_exceptions as bexceptions

class BillingDoResCurrency(models.AbstractModel):
    _name = 'billing.do.res.currency'
    _description = 'Billing DO - Res Currency'

    def load_today_currency_rates(self):
        try:
            currency_rates = self.env['billing.do.currency.rate.http.service.helper']\
                                    .get_currency_rates_for_today()

            if currency_rates:
                for currency_rate in currency_rates:
                    _currency_id = self.env['res.currency']\
                                        .search([('name', '=', currency_rate['currency'])])

                    if not _currency_id:
                        raise bexceptions.NotFound(_('Resource with name {} not found in model.')\
                                                        .format(currency_rate['currency']),\
                                                    'res.currency')

                    companys = self.env['res.company'].search([])
                    for company in companys:
                        self.env['res.currency.rate'].create({
                            'name': currency_rate['date'],
                            'rate': currency_rate['rate'],
                            'currency_id': _currency_id.id,
                            'company_id': company.id,
                            'source': currency_rate['source']
                        })

                        log.info(_('{} Company {} Currency Rate Inserted: {} - {} (Rate: {})')\
                                        .format('[KCS] ',
                                                    company.name,
                                                    currency_rate['date'],
                                                    currency_rate['rate'],
                                                    currency_rate['currency']))

        except Exception as ex:
            log.warning(_('{} Exception thrown while loading Currencies Rates: {}').format('[KCS] ', ex))

class BillingDoResCurrencyModel(models.Model):
    _inherit = 'res.currency.rate'

    source = fields.Char(string="Source", 
                            readonly=True,
                            default="Odoo")