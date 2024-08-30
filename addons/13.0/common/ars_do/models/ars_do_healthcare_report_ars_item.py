from odoo import models, fields, api, _, exceptions
import logging as log

class ArsDoHealthcareReportArsItem(models.Model):
    _name = 'ars.do.healthcare.report.ars.item'
    _description = 'Model representing a Healthcare Report Item for ARS.'
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
    healthcare_plan = fields.Char(string='Plan',
                                    required=True)
    healthcare_card = fields.Char(string='Card',
                                    required=True)
    healthcare_authorization_number = fields.Char(string='Authorization Number',
                                                    required=True)
    healthcare_procedure = fields.Char(string='Procedure',
                                        required=True)
    amount = fields.Monetary(string='Amount',
                                currency_field='currency_id',
                                required=True)
    amount_paid = fields.Monetary(string='Amount Paid',
                                    currency_field='currency_id',
                                    compute='_compute_amount_paid',
                                    store=True)
    amount_due = fields.Monetary(string='Amount Due',
                                    compute='_compute_amount_due',
                                    currency_field='currency_id',
                                    store=True)

    # Relational Fields
    healthcare_provider = fields.Many2one(string='Healthcare Provider', 
                                            comodel_name='res.partner',
                                            ondelete='restrict',
                                            domain=[('is_ars', '=', True)],
                                            required=True,
                                            index=True)
    currency_id = fields.Many2one('res.currency',
                                    string='Currency')
    report_id = fields.Many2one(string='Report Id',
                                    comodel_name='ars.do.healthcare.report.ars',
                                    index=True)
    payment_ids = fields.Many2many(string='Payments Associated',
                                    comodel_name='account.payment',
                                    relation='ars_do_healthcare_report_ars_items_payments')

    # Related Fields
    report_state = fields.Selection(related='report_id.state',
                                        string='State')

    # Compute Methods
    @api.depends('amount', 'amount_paid')
    def _compute_amount_due(self):
        for item in self:
            item.amount_due = item.amount - item.amount_paid

    @api.depends('amount', 'payment_ids')
    def _compute_amount_paid(self):
        for item in self:
            if len(item.payment_ids) > 0:
                item.amount_paid = item.amount
            else:
                item.amount_paid = 0