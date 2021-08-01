# -*- coding: utf-8 -*-

import logging as log

from odoo\
    import models, exceptions, _

class BillingDoTrnHttpServiceHelper(models.AbstractModel):
    _name = "billing.do.trn.http.service.helper"
    _inherit = "billing.do.authentication.http.service.helper"
    _description = ""

    def dgii_validate_ncf(self, vat, ncf, vat_buyer, security_code):
        config = self.env['ir.config_parameter'].sudo()
        
        log.info("[KCS] Service Tax Receipts Switch: {0}"
                    .format(config.get_param('billing_do.api_services_tax_receipts_switch')))

        if config.get_param('billing_do.api_services_tax_receipts_switch'):
            log.info("[KCS] DGII Api Base URL: {0}"
                        .format(config.get_param('billing_do.api_services_base_url')))            
            log.info("[KCS] Service Tax Receipts Endpoint: {0}"
                        .format(config.get_param('billing_do.api_services_tax_receipts_endpoint')))
            log.info("[KCS] Payload: ['vat': '{0}', 'ncf': '{1}', 'vat_buyer': '{2}', 'security_code': '{3}']"
                        .format(vat, 
                                ncf, 
                                vat_buyer, 
                                security_code))
            log.info("[KCS] Token used: {0}"
                        .format(self.get_access_token_for_webapi()))

            request_uri = "{0}/{3}/{1}/{2}".format(config.get_param('billing_do.api_services_base_url'),\
                                                                vat,\
                                                                ncf,\
                                                                config.get_param('billing_do.api_services_tax_receipts_endpoint'))

            if ncf[0] in ['E']:
                request_uri = "{0}/{1}/{2}".format(request_uri, vat_buyer, security_code)

            response = self.send_request(request_uri, 
                                            http_method=self.HTTP_METHODS['get'],
                                            headers=self.get_request_headers(),
                                            data={})

            log.info("[KCS] Request (Status Code): {0}".format(response.status_code))

            if not response is None:
                log.info("[KCS] TRN Response (Status Code): {0}".format(response.status_code))

                if response.status_code == 500:
                    raise exceptions.ValidationError(_("An unknown error ocurred during the connection to the webservice."))
                
                elif response.status_code == 404:
                    raise exceptions.ValidationError(_("The tax receipt number {0} entered is not valid or does not belongs to the VAT {1}.")
                                                        .format(ncf,
                                                                vat))
                
                elif response.status_code == 400:
                    raise exceptions.UserError(_("The values entered for TRN ({0}) and VAT ({1}) are invalid.")
                                                    .format(ncf, 
                                                            vat))
                
                elif response.status_code == 200:
                    if not bool(response.json()['isValid']):
                        raise exceptions.ValidationError(_("The tax receipt number {0} entered is not valid or does not belongs to the VAT {1}.")
                                                            .format(ncf,
                                                                    vat))
                    else:
                        return True

            return False
        return None