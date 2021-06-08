import logging as log

from odoo\
    import models, exceptions

class BillingDoVatHttpServiceHelper(models.AbstractModel):
    _name = "billing.do.vat.http.service.helper"
    _inherit = "billing.do.authentication.http.service.helper"
    _description = """
    
    """

    def dgii_get_vat_info(self, vat):
        config = self.env['ir.config_parameter'].sudo()
        
        log.info("[KCS] Service Tax Contributors Switch: {0}".format(config.get_param('billing_do.api_services_tax_contributors_switch')))
        
        if config.get_param('billing_do.api_services_tax_contributors_switch'):
            log.info("[KCS] DGII Api Base URL: {0}".format(config.get_param('billing_do.api_services_base_url')))
            log.info("[KCS] Service Tax Contributors Endpoint: {0}".format(config.get_param('billing_do.api_services_tax_contributors_endpoint')))
            log.info("[KCS] Payload: ['vat': '{0}']".format(vat))
            log.info("[KCS] Token used: {0}".format(self.get_access_token_for_webapi()))
            
            response = self.send_request("{0}/{1}/{2}".format(config.get_param('billing_do.api_services_base_url'),
                                                            config.get_param('billing_do.api_services_tax_contributors_endpoint'),
                                                            vat),
                                            http_method=self.HTTP_METHODS['get'],
                                            headers=self.get_request_headers())
            
            log.info("[KCS] Request: {0}".format(response))
            log.info("[KCS] Request (Status Code): {0}".format(response.status_code))

            return response
        return None