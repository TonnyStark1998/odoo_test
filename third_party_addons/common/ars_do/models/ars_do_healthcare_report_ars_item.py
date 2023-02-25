from odoo import models, fields, api, _, exceptions
import logging as log

class ArsDoHealthcareReportArsItem(models.Model):
    _name = 'ars.do.healthcare.report.ars.item'
    _description = 'Model representing a Healthcare Report for ARS.'
    _order = 'invoice_date desc'

    invoice_id = fields.Integer(string='Move Id',
                                required=True)
    invoice_line_id = fields.Integer(string='Move Line Id',
                                    required=True)
    invoice_date = fields.Date(string='Date',
                        required=True,
                        index=True)
    healthcare_patient = fields.Char(string='Patient',
                                        required=True)
    identity_number = fields.Char(string='Identity Number')
    healthcare_provider = fields.Char(string='Provider',
                                        required=True,
                                        index=True)
    healthcare_plan = fields.Char(string='Plan',
                                    required=True)
    healthcare_card = fields.Char(string='Card',
                                    required=True)
    healthcare_authorization_number = fields.Char(string='Authorization Number',
                                                    required=True)
    healthcare_procedure = fields.Char(string='Procedure',
                                        required=True)
    currency_id = fields.Many2one('res.currency',
                                    string='Currency')
    amount = fields.Monetary(string='Amount',
                                currency_field='currency_id',
                                required=True)