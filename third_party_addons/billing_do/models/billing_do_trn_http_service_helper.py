# -*- coding: utf-8 -*-

import logging as log
import json

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

            request_uri = "{0}/{1}".format(config.get_param('billing_do.api_services_base_url'),\
                                                                config.get_param('billing_do.api_services_tax_receipts_endpoint'))

            headers = self.get_request_headers()
            headers.update({
                'Content-Type': 'application/x-www-form-urlencoded'
            })

            data = {
                'rncIssuer': vat,
                'trn': ncf
            }

            if ncf[0] in ['E']:
                data.update({
                    'rncConsumer': vat_buyer,
                    'securityCode': security_code
                })

            response = self.send_request(request_uri, 
                                            http_method=self.HTTP_METHODS['post'],
                                            headers=headers,
                                            data=data)

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