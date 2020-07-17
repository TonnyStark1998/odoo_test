from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils

class BillingDoResCompany(models.Model):
    _inherit = "res.company"

    # Res Partner - Modified Fields
    vat = fields.Char(required=True, store=True, tracking=True)

    # Res Partner - OnChange Fields Functions
    @api.onchange('vat')
    def _onchange_vat_billing_do(self):
        self.name = ''
        if self.vat:
            _validate_vat_result = doutils.BillingDoUtils.validate_vat(self.vat)
            if _validate_vat_result == 3:
                return { 
                    'warning':{
                            'title': "Valor digitado inválido",
                            'message': "El RNC (%s) es inválido. Verifique el valor digitado." % self.vat
                        }
                }
            elif _validate_vat_result == 2:
                return { 
                    'warning':{
                            'title': "Dígito verificador erróneo",
                            'message': "El RNC (%s) digitado es inválido." % self.vat
                        }
                }
            try:
                vat_response = doutils.BillingDoUtils.dgii_get_vat_info(self.vat)
                if(vat_response.status_code == 200):
                    self.name = vat_response.json()['razonSocial']
                elif(vat_response.status_code == 404):
                    return{
                        'warning':{
                            'title': "Consulta fallida",
                            'message': "El RNC '%s' no se encuentra en la base de datos de la DGII." % self.vat
                        }
                    }
                else:
                    return{
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