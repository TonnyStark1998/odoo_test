import logging
from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    token_url = fields.Char(string='Token URL')
    token_client_id = fields.Char(string='Client ID')
    token_client_secret = fields.Char(string='Client Secret')
    api_services_base_url = fields.Char(string='API Base URL')
    api_services_tax_contributors_endpoint = fields.Char(string='Tax Contributors Endpoint')
    api_services_tax_receipts_endpoint = fields.Char(string='Tax Receipts Endpoint')
    api_services_tax_contributors_switch = fields.Boolean(string='Tax Contributors Switch')
    api_services_tax_receipts_switch = fields.Boolean(string='Tax Receipts Switch')
    api_services_citizens_endpoint = fields.Char(string='Citizens Endpoint')

    # Rates Configuration Settings
    rate_service_url = fields.Char(string='Rate Service URL')
    rate_regex_usd = fields.Char(string='Regular Expression USD Rate')
    rate_regex_eur = fields.Char(string='Regular Expression EUR Rate')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('billing_do.token_url', self.token_url)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.api_services_base_url', self.api_services_base_url)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.token_client_id', self.token_client_id)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.token_client_secret', self.token_client_secret)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.api_services_tax_contributors_endpoint', self.api_services_tax_contributors_endpoint)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.api_services_tax_receipts_endpoint', self.api_services_tax_receipts_endpoint)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.api_services_tax_contributors_switch', self.api_services_tax_contributors_switch)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.api_services_tax_receipts_switch', self.api_services_tax_receipts_switch)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.rate_service_url', self.rate_service_url)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.rate_regex_usd', self.rate_regex_usd)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.rate_regex_eur', self.rate_regex_eur)
        self.env['ir.config_parameter'].sudo().set_param('billing_do.api_services_citizens_endpoint', self.api_services_citizens_endpoint)

    @api.model
    def get_values(self):
        config = super(ResConfigSettings, self).get_values()
        token_url = self.env['ir.config_parameter'].sudo().get_param('billing_do.token_url')
        token_client_id = self.env['ir.config_parameter'].sudo().get_param('billing_do.token_client_id')
        token_client_secret = self.env['ir.config_parameter'].sudo().get_param('billing_do.token_client_secret')
        api_services_base_url = self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_base_url')
        api_services_tax_contributors_endpoint = self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_tax_contributors_endpoint')
        api_services_tax_receipts_endpoint = self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_tax_receipts_endpoint')
        api_services_tax_contributors_switch = self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_tax_contributors_switch')
        api_services_tax_receipts_switch = self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_tax_receipts_switch')
        rate_service_url = self.env['ir.config_parameter'].sudo().get_param('billing_do.rate_service_url')
        rate_regex_usd = self.env['ir.config_parameter'].sudo().get_param('billing_do.rate_regex_usd')
        rate_regex_eur = self.env['ir.config_parameter'].sudo().get_param('billing_do.rate_regex_eur')
        api_services_citizens_endpoint = self.env['ir.config_parameter'].sudo().get_param('billing_do.api_services_citizens_endpoint')
        config.update({'token_url': token_url})
        config.update({'api_services_base_url': api_services_base_url})
        config.update({'token_client_id': token_client_id})
        config.update({'token_client_secret': token_client_secret})
        config.update({'api_services_tax_contributors_endpoint': api_services_tax_contributors_endpoint})
        config.update({'api_services_tax_receipts_endpoint': api_services_tax_receipts_endpoint})
        config.update({'api_services_tax_contributors_switch': api_services_tax_contributors_switch})
        config.update({'api_services_tax_receipts_switch': api_services_tax_receipts_switch})
        config.update({'rate_service_url': rate_service_url})
        config.update({'rate_regex_usd': rate_regex_usd})
        config.update({'rate_regex_eur': rate_regex_eur})
        config.update({'api_services_citizens_endpoint': api_services_citizens_endpoint})
        return config