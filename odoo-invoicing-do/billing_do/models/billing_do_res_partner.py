from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils
import requests, re
import logging as log

class BillingDoResPartner(models.Model):
    _inherit = "res.partner"

    # Res Partner - Modified Fields
    vat = fields.Char(required=True, store=True, tracking=True)

    # Res Partner - OnChange Fields Functions
    @api.onchange('vat')
    def _onchange_vat_billing_do(self):
        self.name = ''
        if self.vat:
            _validate_vat_result = doutils.BillingDoUtils.validate_vat(self.vat)
            log.info("[KCS] Validate VAT Result: {0}".format(_validate_vat_result))
            if _validate_vat_result == 3:
                return { 
                    'warning':{
                            'title': "Valor digitado inválido",
                            'message': "El RNC (%s) digitado es inválido. Posee un formato incorrecto. Verifique el valor digitado." % self.vat
                        }
                }
            elif _validate_vat_result == 2:
                return { 
                    'warning':{
                            'title': "Dígito verificador erróneo",
                            'message': "El RNC (%s) digitado es inválido. El dígito verificador no coincide. Verifique el valor digitado." % self.vat
                        }
                }
            try:
                vat_response = doutils.BillingDoUtils.dgii_get_vat_info(self, self.vat)
                log.info("[KCS] VAT Response: {0}".format(vat_response))
                log.info("[KCS] VAT Response (Status Code): {0}".format(vat_response.status_code))
                if not vat_response is None:
                    if(vat_response.status_code == 200):
                        self.name = vat_response.json()['razonSocial']
                    elif(vat_response.status_code == 404):
                        return {
                            'warning':{
                                'title': "Consulta fallida",
                                'message': "El RNC '{0}' no se encuentra en la base de datos de la DGII.".format(self.vat)
                            }
                        }
                    else:
                        return {
                            'warning':{
                                'title': "Error de conexión con servicio",
                                'message': "Ocurrió un error inesperado al consulta el servicio."
                            }
                        }
                else:
                    return {
                        'warning': {
                            'title': 'Hola',
                            'message': 'Pasaba por aquí..'
                        }
                    }
            except exceptions.ValidationError as ve:
                return {
                    'warning': {
                        'title': "Error de conexión en servicio",
                        'message': "No se pudo consultar con la DGII la información requerida.",
                    }
                }