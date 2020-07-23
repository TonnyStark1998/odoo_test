# -*- coding: utf-8 -*-
import re
import requests
from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils

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
    ncf_date_to = fields.Date(string="NCF valid to:", readonly=True, copy=False, store=True, tracking=True)

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
            sequence_date_new = sequence._get_current_sequence(sequence_date=sequence_date)
            number_next = sequence_date_new.number_next_actual
            self.ncf_date_to = sequence_date_new.date_to
            self.ncf_sequence_next_number = str(prefix) + str('%%0%sd' % sequence.padding % number_next)

    @api.onchange('ncf', 'partner_id')
    def _onchange_ncf(self):
        if self.type == 'in_invoice':
            try:
                self._validate_ncf(self.ncf)
            except exceptions.ValidationError as ve:
                return {
                    'warning': {
                        'title': "Campo NCF inválido",
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
                sequence_date_new = sequence._get_current_sequence(sequence_date=sequence_date)
                number_next = sequence_date_new.number_next_actual
                move.ncf_date_to = sequence_date_new.date_to
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
            if not self.partner_id:
                raise exceptions.ValidationError("Seleccione primero el proveedor y luego digite el NCF.")
            regex = r"(^(E)?(?=)(31|32|33|34|41|43|44|45)[0-9]{10}|^(B)(?:(01|02|03|04|11|12|13|14|15|16|17)[0-9]{8}))"
            match_ncf = re.match(regex, ncf.upper())
            if not match_ncf:
                raise exceptions.ValidationError("El NCF (%s) es inválido." % ncf.upper())
            else:
                if int(len(ncf)) != int(match_ncf.end()):
                    raise exceptions.ValidationError("El NCF (%s) posee dígitos extras. Verifique." % ncf.upper())
            ncf_response = doutils.BillingDoUtils.dgii_validate_ncf(self.partner_id.vat, ncf, self.env.company.vat)
            if ncf_response.status_code == 400:
                raise exceptions.ValidationError("Los datos suministrados para la consulta no son válidos. NCF:{0}|RNC:{1}".format(ncf, self.partner_id.vat))
            elif ncf_response.status_code == 500:
                raise exceptions.ValidationError("Ocurrió un error desconocido al conectar con el servicio de consulta.")
            elif ncf_response.status_code == 404:
                raise exceptions.ValidationError("El NCF {0} y el RNC {1} no arrojaron ningún resultado. Favor verificar el NCF digitado.".format(ncf, self.partner_id.vat))
            elif ncf_response.status_code == 200:
                if not bool(ncf_response.json()['isValid']):
                    raise exceptions.ValidationError("El NCF {0} digitado no es válido. Verifique el valor digitado y el proveedor (RNC: {1}) seleccionado.".format(ncf, self.partner_id.vat))