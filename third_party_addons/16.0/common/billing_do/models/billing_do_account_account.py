# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class BillingDoAccountAccount(models.Model):
    _inherit = "account.account"

    withholding_tax_type = fields.Selection(selection=[
        ('RET-ITBIS-606', 'Retencion ITBIS 606'),
        ('RET-ITBIS-607', 'Retencion ITBIS 607'),
        ('RET-ISR-606', 'Retencion ISR 606'),
        ('RET-ISR-607', 'Retencion ISR 607'),
    ], string='Withholding Tax Type', required=False, store=True, copy=True)
    account_type = fields.Selection(
        selection_add=[
            ('equity_capital_social', 'Capital Social'),
            ('equity_accion_tesoreria', 'Acciones en Tesoreria'),
            ('equity_reserva_legal', 'Reserva Legal'),
            ('equity_superavit_revaluacion', 'Superávit por revaluación'),
        ],
        ondelete={
            'equity_capital_social': 'set equity', 
            'equity_accion_tesoreria': 'set equity', 
            'equity_reserva_legal': 'set equity', 
            'equity_superavit_revaluacion': 'set equity'
        },
    )