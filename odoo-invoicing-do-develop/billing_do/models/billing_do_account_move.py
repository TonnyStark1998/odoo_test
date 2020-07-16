# -*- coding: utf-8 -*-
import re
import requests
from odoo import models, fields, api, exceptions

class BillingDoAccountMove(models.Model):
    _inherit = "account.move"

    # Account Move - SQL Constraints
    _sql_constraints = [
        ('ncf_sequence_next_number',
         'UNIQUE(ncf_sequence_next_number)',
         "El NCF de las facturas no puede repetirse."),
    ]

    # Account Move - New Fields
    income_type = fields.Selection(selection=[
            ('01', '01 - Ingresos por Operaciones (No Financieros)'),
            ('02', '02 - Ingresos Financieros'),
            ('03', '03 - Ingresos Extraordinarios'),
            ('04', '04 - Ingresos por Arrendamientos'),
            ('05', '05 - Ingresos por Venta de Activo Depreciable'),
            ('06', '06 - Otros Ingresos')
        ], required=True, store=True, readonly=False, copy=False, tracking=True, default='01')

    expense_type = fields.Selection(selection=[
            ('01', '01 - Gastos de personal'),
            ('02', '02 - Gastos por trabajos, suministros y servicios'),
            ('03', '03 - Arrendamientos'),
            ('04', '04 - Gastos de activo fijo'),
            ('05', '05 - Gastos de representación'),
            ('06', '06 - Otras deducciones admitidas'),
            ('07', '07 - Gastos financieros'),
            ('08', '08 - Gastos extraordinarios'),
            ('09', '09 - Compras y gastos que formarán parte del costo de venta'),
            ('10', '10 - Adquisiciones de activos'),
            ('11', '11 - Gastos de seguro'),
        ], required=True, store=True, readonly=False, copy=True, tracking=True, default='02')

    ncf = fields.Char(string="NCF", readonly=False, copy=False, store=True, tracking=True, states={'posted': [('readonly', True)]})
    ncf_sequence_next_number = fields.Char(readonly=True, copy=False, store=False, tracking=False, compute='_compute_set_name_next_sequence')

    # Account Move - OnChange Fields Functions
    @api.onchange('journal_id')
    def _onchange_journal_id_billing_do(self):
        if self.journal_id:
            sequence_date = self.date or self.invoice_date
            if self.type in ('out_refund', 'in_refund'):
                sequence = self.journal_id.refund_sequence_id
            else:
                sequence = self.journal_id.sequence_id
            prefix, suffix = sequence._get_prefix_suffix(date=sequence_date, date_range=sequence_date)
            number_next = sequence._get_current_sequence(sequence_date=sequence_date).number_next_actual
            self.ncf_sequence_next_number = str(prefix) + str('%%0%sd' % sequence.padding % number_next)

    @api.onchange('ncf')
    def _onchange_ncf(self):
        if self.type == 'in_invoice':
            try:
                self._validate_ncf(self.ncf)
            except exceptions.ValidationError as ve:
                return {
                    'warning': {
                        'title': "Campo invalido",
                        'message': "{0}".format(ve.name),
                    }
                }


    # Account Move - Compute Field's Functions
    @api.depends('ncf_sequence_next_number', 'journal_id')
    def _compute_set_name_next_sequence(self):
        for move in self:
            if move.journal_id:
                sequence_date = move.date or move.invoice_date
                if move.type in ('out_refund', 'in_refund'):
                    sequence = move.journal_id.refund_sequence_id
                else:
                    sequence = move.journal_id.sequence_id
                prefix, suffix = sequence._get_prefix_suffix(date=sequence_date, date_range=sequence_date)
                number_next = sequence._get_current_sequence(sequence_date=sequence_date).number_next_actual
                move.ncf_sequence_next_number = str(prefix) + str('%%0%sd' % sequence.padding % number_next)

    # Account Move - Contraints Field's Functions
    @api.constrains('ncf', 'type')
    def _check_ncf(self):
        for move in self:
            if move.type == 'in_invoice':
                try:
                    self._validate_ncf(move.ncf)
                except exceptions.ValidationError:
                    raise

    # Account Move - Helper Functions
    def _validate_ncf(self, ncf):
        if ncf:
            regex = r"(^(E)?(?=)(31|32|33|34|41|43|44|45)[0-9]{10}|^(B)(?:(01|02|03|04|11|12|13|14|15|16|17)[0-9]{8}))"
            match_ncf = re.match(regex, ncf.upper())
            if not match_ncf:
                raise exceptions.ValidationError("El NCF (%s) es inválido." % ncf.upper())
            else:
                if int(len(ncf)) != int(match_ncf.end()):
                    raise exceptions.ValidationError("El NCF (%s) posee dígitos extras. Verifique." % ncf.upper())
                # response = requests.get("https://localhost:44359/webapi/Contribuyentes/00117045369")