from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils
import logging as log

class BillingDoResPartner(models.Model):
    _inherit = "res.partner"

    # Res Partner - New Fields
    tax_contributor_type = fields.Selection(selection=[
            ('1', 'Persona jurídica'),
            ('2', 'Persona física'),
            ('3', 'Otro')
        ], string='Tax Contributor Type', required=True, store=True, readonly=False, copy=False, tracking=True)
    economic_activity = fields.Char(string='Economic Activity')

    # Res Partner - Modified Fields
    vat = fields.Char(store=True, tracking=True)
    company_id = fields.Many2one(default=lambda self: self.env.company)

    # Res Partner - OnChange Fields Functions
    @api.onchange('vat', 'tax_contributor_type')
    def _onchange_vat_billing_do(self):
        self.name = ''
        if self.vat and self.tax_contributor_type and not self.tax_contributor_type in ['3']:
            _validate_vat_result = doutils.BillingDoUtils.validate_vat(self.vat)
            log.info("[KCS] Validate VAT Result: {0}".format(_validate_vat_result))
            if _validate_vat_result == 3:
                return { 
                    'warning':{
                            'title': "Valor digitado inválido",
                            'message': "El RNC ({0}) digitado es inválido. Posee un formato incorrecto. Verifique el valor digitado.".format(self.vat)
                        }
                }
            elif _validate_vat_result == 2:
                return { 
                    'warning':{
                            'title': "Dígito verificador erróneo",
                            'message': "El RNC ({0}) digitado es inválido. El dígito verificador no coincide. Verifique el valor digitado.".format(self.vat)
                        }
                }
            try:
                vat_response = doutils.BillingDoUtils.dgii_get_vat_info(self, self.vat)

                if not vat_response is None:
                    log.info("[KCS] VAT Response: {0}".format(vat_response))
                    log.info("[KCS] VAT Response (Status Code): {0}".format(vat_response.status_code))
                    
                    if(vat_response.status_code == 200):
                        self.name = vat_response.json()['razonSocial']
                        self.economic_activity = vat_response.json()['actividadEconomica']
                        return {
                            'warning': {
                                'title': "RNC '{0}' encontrado.".format(self.vat),
                                "message": "Pertenece a '{0}' según los registros de la DGII.".format(self.name)
                            }
                        }
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
            except exceptions.ValidationError as ve:
                return {
                    'warning': {
                        'title': "Error de conexión en servicio",
                        'message': "No se pudo consultar con la DGII la información requerida.",
                    }
                }

    @api.onchange('tax_contributor_type')
    def _onchange_tax_contributor_type(self):
        if self.tax_contributor_type and self.tax_contributor_type in ['3']:
            self.name = ''