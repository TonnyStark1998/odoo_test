from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    token_url = fields.Char(string='Token URL', default='https://login.microsoftonline.com/4e9b7883-1526-4764-abf5-619326b5f34a/oauth2/v2.0/token')
    api_services_base_url = fields.Char(string='', default='https://api-dev.koalacreativesoftware.com/webapi/')
    api_services_tax_contributors_endpoint = fields.Char(string='Tax Contributors Endpoint')
    api_services_tax_receipts_endpoint = fields.Char(string='Tax Contributors Endpoint')
