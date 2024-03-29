# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_services_base_url = fields.Char(string='API Base URL', default='https://odoo-host/webapi')
    api_services_tax_contributors_endpoint = fields.Char(string='Tax Contributors Endpoint', default='taxcontributors')
    api_services_tax_receipts_endpoint = fields.Char(string='Tax Receipts Endpoint', default='taxreceiptsnumbers')
    api_services_citizens_endpoint = fields.Char(string='Citizens Endpoint', default='citizens')
    api_services_tax_contributors_switch = fields.Boolean(string='Tax Contributors Switch')
    api_services_tax_receipts_switch = fields.Boolean(string='Tax Receipts Switch')

    # Rates Configuration Settings
    api_services_currency_rates_switch = fields.Boolean(string='Currency Rates Switch')
    api_services_currency_rates_endpoint = fields.Char(string='Currency Rates Endpoint', default='currencyrates')

    def set_values(self):
        super(ResConfigSettings, self)\
            .set_values()

        self.env['ir.config_parameter'].sudo()\
            .set_param('billing_do.api_services_base_url', self.api_services_base_url)
        self.env['ir.config_parameter'].sudo()\
            .set_param('billing_do.api_services_tax_contributors_endpoint', self.api_services_tax_contributors_endpoint)
        self.env['ir.config_parameter'].sudo()\
            .set_param('billing_do.api_services_tax_receipts_endpoint', self.api_services_tax_receipts_endpoint)
        self.env['ir.config_parameter'].sudo()\
            .set_param('billing_do.api_services_tax_contributors_switch', self.api_services_tax_contributors_switch)
        self.env['ir.config_parameter'].sudo()\
            .set_param('billing_do.api_services_tax_receipts_switch', self.api_services_tax_receipts_switch)
        self.env['ir.config_parameter'].sudo()\
            .set_param('billing_do.api_services_currency_rates_endpoint', self.api_services_currency_rates_endpoint)
        self.env['ir.config_parameter'].sudo()\
            .set_param('billing_do.api_services_citizens_endpoint', self.api_services_citizens_endpoint)
        self.env['ir.config_parameter'].sudo()\
            .set_param('billing_do.api_services_currency_rates_switch', self.api_services_currency_rates_switch)

    @api.model
    def get_values(self):
        config = super(ResConfigSettings, self)\
                    .get_values()

        api_services_base_url = \
            self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_base_url')
        api_services_tax_contributors_endpoint = \
            self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_tax_contributors_endpoint')
        api_services_tax_receipts_endpoint = \
            self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_tax_receipts_endpoint')
        api_services_tax_contributors_switch = \
            self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_tax_contributors_switch')
        api_services_tax_receipts_switch = \
            self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_tax_receipts_switch')
        api_services_currency_rates_endpoint = \
            self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_currency_rates_endpoint')
        api_services_citizens_endpoint = \
            self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_citizens_endpoint')
        api_services_currency_rates_switch = \
            self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_currency_rates_switch')
        
        config.update({'api_services_base_url':
                        api_services_base_url})
        config.update({'api_services_tax_contributors_endpoint':
                        api_services_tax_contributors_endpoint})
        config.update({'api_services_tax_receipts_endpoint':
                        api_services_tax_receipts_endpoint})
        config.update({'api_services_tax_contributors_switch':
                        api_services_tax_contributors_switch})
        config.update({'api_services_tax_receipts_switch':
                        api_services_tax_receipts_switch})
        config.update({'api_services_currency_rates_endpoint':
                        api_services_currency_rates_endpoint})
        config.update({'api_services_citizens_endpoint':
                        api_services_citizens_endpoint})
        config.update({'api_services_currency_rates_switch':
                        api_services_currency_rates_switch})
        
        return config