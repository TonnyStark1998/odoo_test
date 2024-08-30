# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
import logging as log

class ArsDoAccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Model representing a Account Move.'

    healthcare_invoice = fields.Selection(string='Healthcare Invoice',
                                            selection=[
                                                ('healthcare_invoice', 'Insurance'),
                                                ('not_healthcare_invoice', 'Private')
                                            ])

    healthcare_card = fields.Many2one(string='Healthcare Card',
                                        comodel_name='ars.do.healthcare.card')
    healthcare_provider = fields.Many2one(related='healthcare_card.healthcare_plan.healthcare_provider',
                                            store=True)
    healthcare_plan = fields.Char(related='healthcare_card.healthcare_plan.name',
                                    store=True)
    healthcare_authorization_number = fields.Char(string='Healthcare Authorization Number',
                                                    size=20,
                                                    tracking=True)

    created_from_sale = fields.Boolean(string='Created from sale',
                                        store=False,
                                        default=False)

    amount_coverage = \
        fields.Monetary(
            string='Amount Coverage',
            compute='_compute_amount_coverage', store=True, readonly=True,
            currency_field='company_currency_id',
            default=0.0)

    # Changes methods
    @api.onchange('healthcare_invoice')
    def _onchange_healthcare_invoice(self):
        self.ensure_one()
        if not self.created_from_sale:
            self.partner_id = None
            self.healthcare_card = None

        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                line.coverage = 0.0
                if not line.move_id.is_invoice(include_receipts=True):
                    continue

                line.update(line._get_price_total_and_subtotal())
                line.update(line._get_fields_onchange_subtotal())

        if self.healthcare_invoice == 'healthcare_invoice':
            return {
                'domain': {
                        'partner_id': [('is_patient', '=', True)]
                }
            }

        return {
            'domain': {
                'partner_id': []
            }
        }

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.type in ['out_invoice', 'out_refund']:
            if not self.healthcare_invoice and self.partner_id:
                self.partner_id = False
                return { 
                        'warning': {
                            'title': _('User error!'),
                            'message': _('You must indicate if this is a Healthcare or Regular invoice before selecting the Customer.')
                        }
                }

            if self.healthcare_invoice == 'healthcare_invoice':
                if self.partner_id:
                    if not self.partner_id.is_patient:
                        self.partner_id = False
                    else:
                        self.healthcare_card = self.partner_id.healthcare_cards\
                                                                .filtered(lambda self: self.default_card == True)
                    return {
                            'domain': {
                                'partner_id': [('is_patient', '=', True)]
                            }
                        }

    # Compute methods
    @api.depends('invoice_line_ids')
    def _compute_amount_coverage(self):
        for move in self:
            if move.healthcare_invoice == 'healthcare_invoice':
                move.amount_coverage = \
                    self._calculate_amount_coverage(move.invoice_line_ids)

    # Contraints methods
    @api.constrains('healthcare_invoice')
    def _constrain_healthcare_invoice(self):
        for move in self:
            if move.type in ['out_invoice', 'out_refund'] and not move.healthcare_invoice:
                raise exceptions.ValidationError(_('You must indicate if this is a Healthcare or Regular invoice.'))

    # Override methods
    def action_post(self):
        posted = super().action_post()
        if self.type in ['out_invoice', 'out_refund'] \
            and self.healthcare_invoice == 'healthcare_invoice'\
            and posted:
            invoice_id = self.id
            invoice_date = self.invoice_date
            healthcare_patient = self.partner_id.name
            identity_number = self.partner_id.vat or ''
            healthcare_provider = self.healthcare_provider.id
            healthcare_plan = self.healthcare_plan
            healthcare_card = self.healthcare_card.number
            healthcare_authorization_number = self.healthcare_authorization_number
            currency_id = self.currency_id
            report = self._create_report()
            
            log.info('[KCS] Report State: {}'.format(report.state))
            if report.state in ['sent', 'reconciling', 'reconciled']:
                posted = False
                raise UserError(_('Report of {} for period {}-{} has been already sent. Can\'t add more invoice to it.')
                                    .format(report.healthcare_provider.name, report.report_month, report.report_year))

            for invoice_line in self.invoice_line_ids:
                self.env['ars.do.healthcare.report.ars.item']\
                        .create({
                            'report_id': report.id,
                            'invoice_id': invoice_id,
                            'invoice_line_id': invoice_line.id,
                            'invoice_date': invoice_date,
                            'healthcare_patient': healthcare_patient,
                            'identity_number': identity_number,
                            'healthcare_provider': healthcare_provider,
                            'healthcare_plan': healthcare_plan,
                            'healthcare_card': healthcare_card,
                            'healthcare_authorization_number': healthcare_authorization_number,
                            'healthcare_procedure': invoice_line.product_id.name,
                            'currency_id': currency_id.id,
                            'amount': ((invoice_line.quantity * invoice_line.price_unit)
                                        * (1 - (invoice_line.discount / 100))
                                        * (invoice_line.coverage / 100))
                        })
        return posted

    def button_draft(self):
        super(ArsDoAccountMove, self).button_draft()
        report = self._get_report_or_default()
        if not report is None \
            and report.state in ['sent', 'reconciling', 'reconciled']:
            raise UserError(_('Report of {} for period {}-{} has been already sent. This invoice will not reflect the changes in the report.')
                                    .format(report.healthcare_provider.name, report.report_month, report.report_year))

        if self.type in ['out_invoice', 'out_refund']\
            and self.healthcare_invoice == 'healthcare_invoice':
            move_id = self.id
            self.env['ars.do.healthcare.report.ars.item']\
                    .search([('invoice_id', '=', move_id)])\
                    .unlink()

    def write(self, values):
        original_healthcare_authorization_number = \
            self.healthcare_authorization_number
        move = super().write(values)
        if 'healthcare_authorization_number' in values\
            and self.invoice_date:
            report = self._get_report_or_default()
            if not report is None:
                invoice_id = self.id
                self.env['ars.do.healthcare.report.ars.item']\
                    .search([('invoice_id', '=', invoice_id), ('report_id', '=', report.id)])\
                    .write({
                        'healthcare_authorization_number': values.get('healthcare_authorization_number')
                    })
                log.info('[ARS] Healthcare Authorization Number changed: from {} to {}'
                         .format(original_healthcare_authorization_number, values.get('healthcare_authorization_number')))
        return move

    # Private Methods
    def _create_report(self):
        if self.invoice_date:
            invoice_month = str(self.invoice_date.month).rjust(2,'0')
            invoice_year = str(self.invoice_date.year)
            healthcare_provider = self.healthcare_provider.id
            report = self._get_report_or_default()
            if report is None:
                return self.env['ars.do.healthcare.report.ars']\
                            .create({
                                'healthcare_provider': healthcare_provider,
                                'report_year': invoice_year,
                                'report_month': invoice_month,
                                'state': 'draft'
                            })
            return report
        
    def _get_report_or_default(self):
        if self.invoice_date:
            invoice_month = str(self.invoice_date.month).rjust(2,'0')
            invoice_year = str(self.invoice_date.year)
            healthcare_provider = self.healthcare_provider.id
            report = self.env['ars.do.healthcare.report.ars']\
                            .search([('healthcare_provider', '=', healthcare_provider),
                                        ('report_year', '=', invoice_year),
                                        ('report_month', '=', invoice_month)])
            if not report:
                return None
            return report
    
    def _calculate_amount_coverage(self, invoice_line_ids):
        amount_coverage = 0.0
        if invoice_line_ids:
            for line in invoice_line_ids:
                if not line.exclude_from_invoice_tab:
                    amount_coverage += \
                        ((line.quantity \
                            * (line.price_unit * (1 - (line.discount / 100)))) \
                            * (line.coverage / 100))

        return amount_coverage
