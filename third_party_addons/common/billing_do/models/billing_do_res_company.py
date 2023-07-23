# -*- coding: utf-8 -*-

import logging as log

from odoo\
    import models, fields, api, exceptions

class BillingDoResCompany(models.Model):
    _name = 'res.company'
    _inherit = ['res.company', 'mail.thread']

    # Res Company - New Fields
    tax_contributor_type = fields.Selection(selection=[
                                                ('1', 'Persona jurídica'),
                                                ('2', 'Persona física'),
                                                ('3', 'Otro')
                                            ],
                                            string='Tax Contributor Type',
                                            required=True,
                                            store=True,
                                            readonly=False,
                                            copy=False,
                                            tracking=True)

    googleplus = fields.Char(string='Google Plus ID', 
                                copy=True, 
                                store=True, 
                                default='')

    load_currency_rates = fields.Boolean(string='Load Currency Rates?',
                                            default=True,
                                            copy=True)

    # Res Company - Modified Fields
    vat = fields.Char(store=True, tracking=True)

    # Res Company - Related Fields
    economic_activity = fields.Char(related='partner_id.economic_activity')

    # Res Company - OnChange Fields Functions
    @api.onchange('vat', 'tax_contributor_type')
    def _onchange_vat_billing_do(self):
        self.name = ''
        self.economic_activity = ''

        if self.vat and self.tax_contributor_type and not self.tax_contributor_type in ['3']:
            _vat_helper = self.env['billing.do.vat.helper'].sudo()
            _validate_vat_result = _vat_helper.validate_vat(self.vat)
            
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
                            'message': "No posee la estructura de una cedula y tampoco de un RNC ({0}).".format(self.vat)
                        }
                }

            try:
                _vat_helper = self.env['billing.do.vat.http.service.helper'].sudo()
                vat_response = _vat_helper.dgii_get_vat_info(self.vat)

                log.info("[KCS] VAT Response: {0}".format(vat_response))
                log.info("[KCS] VAT Response (Status Code): {0}".format(vat_response.status_code))

                if vat_response and vat_response.status_code == 200:
                    self.name = vat_response.json()['razonSocial']
                    self.economic_activity = vat_response.json()['actividadEconomica']
                    return {
                        'warning': {
                            'title': "RNC '{0}' encontrado.".format(self.vat),
                            "message": "Pertenece a '{0}' según los registros de la DGII.".format(self.name)
                        }
                    }

                _citizen_helper = self.env['billing.do.citizen.http.service.helper'].sudo()
                citizen_response = _citizen_helper.dgii_get_citizen_info(self, self.vat)

                log.info("[KCS] Citizen Response: {0}".format(citizen_response))
                log.info("[KCS] Citizen Response (Status Code): {0}".format(citizen_response.status_code))

                if citizen_response and citizen_response.status_code == 200:
                    self.name = citizen_response.json()['nombre']
                    return {
                        'warning': {
                            'title': "Ciudadano '{0}' encontrado.".format(self.vat),
                            "message": "Pertenece a '{0}' según los registros de la DGII.".format(self.name)
                        }
                    }

                if((citizen_response is not None and citizen_response.status_code == 404) 
                        or (vat_response is not None and vat_response.status_code == 404)):
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
            self.economic_activity = ''

    @api.model
    def create(self, vals):
        _new_partner = self.env['res.partner'].create({
            'name': vals['name'],
            'is_company': True,
            'image_1920': vals.get('logo'),
            'email': vals.get('email'),
            'phone': vals.get('phone'),
            'website': vals.get('website'),
            'vat': vals.get('vat'),
            'country_id': vals.get('country_id'),
            'tax_contributor_type': vals.get('tax_contributor_type'),
            'economic_activity': vals.get('economic_activity'),
        })
        # compute stored fields, for example address dependent fields
        _new_partner.flush()
        vals['partner_id'] = _new_partner.id

        _new_company = super(BillingDoResCompany, self)\
                        .create(vals)
        _new_company.flush()

        _base_sale_order_sequence = self.env['ir.sequence']\
                                            .search([('code', '=', 'sale.order'),
                                                            ('company_id', '=', False)],
                                                        limit = 1)
        _base_purchase_order_sequence = self.env['ir.sequence']\
                                            .search([('code', '=', 'purchase.order'),
                                                            ('company_id', '=', False)],
                                                        limit = 1)

        if _base_sale_order_sequence:
            _base_sale_order_sequence.copy({
                                            'company_id' : _new_company.id
                                        })

        if _base_purchase_order_sequence:
            _base_purchase_order_sequence.copy({
                                                'company_id' : _new_company.id
                                            })

        return _new_company

    def write(self, values):
        self.clear_caches()

        partner = self.env['res.partner'].browse(self.partner_id.id)

        if values.get('tax_contributor_type'):
            partner.write({'tax_contributor_type': values.get('tax_contributor_type')})

        if values.get('economic_activity'):
            partner.write({'economic_activity': values.get('economic_activity')})
    
        return super(BillingDoResCompany, self).write(values)
