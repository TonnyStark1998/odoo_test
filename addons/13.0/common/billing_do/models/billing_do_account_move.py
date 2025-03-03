# -*- coding: utf-8 -*-

import re
import datetime as date
import logging as log

from odoo\
    import models, fields, api, exceptions, _

class BillingDoAccountMove(models.Model):
    _inherit = "account.move"

    # Account Move - New Fields
    income_type = fields.Selection(selection=[
                                                ('01', '01 - Ingresos por Operaciones (No Financieros)'),
                                                ('02', '02 - Ingresos Financieros'),
                                                ('03', '03 - Ingresos Extraordinarios'),
                                                ('04', '04 - Ingresos por Arrendamientos'),
                                                ('05', '05 - Ingresos por Venta de Activo Depreciable'),
                                                ('06', '06 - Otros Ingresos')
                                            ], 
                                    required=True, 
                                    store=True, 
                                    readonly=False, 
                                    copy=False, 
                                    tracking=True, 
                                    default='01',
                                    string='Income Type')

    expense_type = fields.Selection(selection=[
                                                ('01', '01 -GASTOS DE PERSONAL'),
                                                ('02', '02-GASTOS POR TRABAJOS, SUMINISTROS Y SERVICIOS'),
                                                ('03', '03-ARRENDAMIENTOS'),
                                                ('04', '04-GASTOS DE ACTIVOS FIJO'),
                                                ('05', '05 -GASTOS DE REPRESENTACIÓN'),
                                                ('06', '06 -OTRAS DEDUCCIONES ADMITIDAS'),
                                                ('07', '07 -GASTOS FINANCIEROS'),
                                                ('08', '08 -GASTOS EXTRAORDINARIOS'),
                                                ('09', '09 -COMPRAS Y GASTOS QUE FORMARAN PARTE DEL COSTO DE VENTA'),
                                                ('10', '10 -ADQUISICIONES DE ACTIVOS'),
                                                ('11', '11- GASTOS DE SEGUROS'),
                                            ], 
                                    required=True, 
                                    store=True, 
                                    readonly=False, 
                                    copy=True, 
                                    tracking=True, 
                                    default='02',
                                    string='Expense Type')

    ncf = fields.Char(string="NCF",
                        readonly=False,
                        copy=False, 
                        store=True, 
                        tracking=True, 
                        states={'posted': [('readonly', True)]})

    ncf_date_to = fields.Date(string="NCF valid to:", 
                                readonly=True, 
                                copy=False, 
                                store=True, 
                                tracking=True)

    security_code = fields.Char(string='Security Code',
                                    copy=False)

    ncf_type = fields.Char(string='NCF Type',
                            store=False,
                            default='/')

    # Account Move - Related Fields
    is_tax_valuable = fields.Boolean(related='journal_id.is_tax_valuable', 
                                        store=False, 
                                        Tracking=False)
    use_sequence = fields.Boolean(related='journal_id.use_sequence', 
                                    store=False, 
                                    Tracking=False)

    sequence_count_left = fields.Integer(compute='_compute_sequence_count_left',
                                         store=False)

    @api.onchange('ncf', 'partner_id', 'journal_id', 'security_code', 'invoice_date')
    def _onchange_ncf(self):
        try:
            self._ensure_journal_code_is_set()

            if self.ncf and len(self.ncf) > 1:
                self.ncf_type = self.ncf[0]

            if self.type in ['in_invoice', 'in_refund', 'in_receipt']\
                and self.is_tax_valuable\
                and self.journal_id.sequence_id.code.upper() not in ['B11', 'B13']:

                if self.ncf_type in ['E']\
                    and not self.security_code:
                    return

                if self._validate_ncf(self.ncf):
                    return {
                            'warning': {
                                'title': _('TRN is valid.'),
                                'message': _('The TRN "{0}" y el RNC "{1}" are valid.')
                                                .format(self.ncf, 
                                                        self.partner_id.vat)
                            }
                        }

            elif self.journal_id.sequence_id.code.upper() in ['B11']:
                if self.partner_id:
                    if self.partner_id.vat:
                        _vat_helper = self.env['billing.do.vat.helper'].sudo()
                        _vat_helper.validate_vat(self.partner_id.vat)

                        return self.__validate_vat_journal_b11(self)
                    else:
                        raise exceptions.UserError(_('You are trying to use a partner who does not have a VAT value. Please verify.'))

        except exceptions.UserError as ue:
            return {
                'warning': {
                    'title': _('¡User error!'),
                    'message': '{0}'.format(ue.name),
                }
            }

        except exceptions.ValidationError as ve:
            return {
                'warning': {
                    'title': _('¡Validation error!'),
                    'message': '{0}'.format(ve.name),
                }
            }

    # Account Move - Compute Field's Functions
    @api.onchange('invoice_date')
    def _compute_move_date(self):
        if self.invoice_date and self.type not in ['entry']:
            self.date = self.invoice_date
        else:
            self.date = fields.Date.today()

    @api.depends('journal_id', 'invoice_date')
    def _compute_sequence_count_left(self):
        count_left = False
        if self.journal_id and self.invoice_date:
            if (self.journal_id.is_tax_valuable and self.type in ['out_invoice', 'out_refund']) \
                or (self.journal_id.use_sequence and self.type in ['in_invoice', 'in_refund']):
                sequence = \
                    False if not self.journal_id\
                        .sequence_id\
                        .use_date_range\
                    else self.journal_id\
                        .sequence_id\
                        .date_range_ids\
                        .filtered(lambda seq: \
                                   seq.date_from <= self.invoice_date
                                   and seq.date_to >= self.invoice_date
                                   and seq.number_next <= seq.number_last)
                if sequence:
                    count_left = sequence.sequence_count_left
        
        if count_left:
            self.sequence_count_left = count_left
        else:
            self.sequence_count_left = 999

    # Account Move - Contrains Field's Functions
    @api.constrains('ncf', 'type', 'journal_id')
    def _check_ncf(self):
        for move in self:
            try:
                self._ensure_journal_code_is_set()

                if move.type in ['in_invoice', 'in_refund', 'in_receipt']\
                    and move.is_tax_valuable\
                    and move.journal_id.sequence_id.code.upper() not in ['B11', 'B13']:

                    if move.ncf_type in ['E']\
                        and not move.security_code:

                        raise exceptions.UserError(_("For E NCF ('{0}') type you have to provide the security code.").format(self.ncf))

                    self._validate_ncf(move.ncf)

                elif move.journal_id.sequence_id.code.upper() in ['B11']:
                    if move.partner_id:
                        if move.partner_id.vat:
                            _vat_helper = self.env['billing.do.vat.helper'].sudo()
                            _vat_helper.validate_vat(move.partner_id.vat)

                            return self.__validate_vat_journal_b11(move)
                        else:
                            raise exceptions.UserError(_('You are trying to use a partner who does not have a VAT value. Please verify.'))
                    
                    else:
                        raise exceptions.UserError(_('Please, first select the vendor and then enter the value for NCF field.'))

            except:
                raise

    @api.constrains('name', 'journal_id', 'state')
    def _check_unique_sequence_number(self):
        moves = self.filtered(lambda move: move.state == 'posted')

        if not moves:
            return

        self.flush()

        # /!\ Computed stored fields are not yet inside the database.
        self._cr.execute('''
            SELECT move2.id
            FROM account_move move
            INNER JOIN account_move move2 ON
                move2.name = move.name
                AND move2.journal_id = move.journal_id
                AND move2.type = move.type
                AND move2.id != move.id
                AND move2.company_id = move.company_id
                AND move2.partner_id = move.partner_id
            WHERE move.id IN %s AND move2.state = 'posted'
        ''', [tuple(moves.ids)])
        res = self._cr.fetchone()
        if res:
            raise exceptions.ValidationError(_('Posted journal entry must have an unique sequence number per company.'))

    @api.model
    def post(self):
        try:
            for move in self:
                move._ensure_journal_code_is_set()

                sequence = move.__get_journal_sequence()
                if not sequence:
                    return

                sequence = sequence._get_current_sequence(sequence_date=move.date or move.invoice_date)
                if move.type in ['in_invoice', 'in_refund', 'in_receipt']\
                        and move.journal_id.sequence_id.code.upper() not in ['B11', 'B13']\
                            and move.journal_id.is_tax_valuable:
                    
                    move.name = move.ncf

                if isinstance(sequence, type(move.env['ir.sequence.date_range'])):
                    if 'date_to' in sequence:
                        move.ncf_date_to = sequence.date_to

                    sequence._compute_sequence_count_left()

            return super().post()
        except exceptions.UserError:
            raise

    def action_duplicate(self):
        self.ensure_one()

        lines_wo_product = 0
        for line in self.line_ids:
            if not line.product_id:
                lines_wo_product += 1
        log.info('Lines w/o products: {}'.format(lines_wo_product))
        if lines_wo_product > 0:
            raise exceptions.UserError(_('There is(are) a(some) line(s) which does not have any product associated. Please correct this error before duplicating.'))

        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['context'] = dict(self.env.context)
        action['context']['form_view_initial_mode'] = 'edit'
        action['context']['view_no_maturity'] = False
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = self.copy().id
        return action

    def js_assign_outstanding_line(self, line_id):
        super(BillingDoAccountMove, self).js_assign_outstanding_line(line_id)

        line = self.env['account.move.line'].browse(line_id)
        self.env['mail.message'].create({
            'subject': _('Payment reconciled.'),
            'body': _("<p style='margin:0px; font-size:13px; font-family:'Lucida Grande', Helvetica, Verdana, Arial, sans-serif'><strong>Payment reconciled with line id:</strong> {} - {}.</p>")
                        .format(line.id, line.name),
            'email_from': self.env.user.login,
            'author_id': self.env.user.partner_id.id,
            'model': 'account.move',
            'res_id': self.id,
            'record_name': self.name,
            'message_type': 'comment',
            'subtype_id': 2
        })

        log.info("[KCS] AccountMove.JsAssignOutstandingLine: User {} added a payment {} to move id {}."
                    .format(self.env.user.login, line_id, self.id))

    # Account Move - Helper Functions
    def _validate_ncf(self, ncf):
        if ncf:
            if not self.partner_id:
                raise exceptions.UserError(_('Please, first select the vendor and then enter the value for NCF field.'))

            if not self.invoice_date:
                raise exceptions.UserError(
                        _('Please, first select the invoice date and then enter the value for NCF field.')
                    )

            if self.partner_id.vat:
                ncf_exists = self.env['account.move'].search_count(args=[
                                                                        ('id', '!=', self.id if self.id else 0), 
                                                                        ('type', 'in', ['in_invoice', 'in_refund', 'in_receipt']), 
                                                                        ('partner_id.vat', '=', self.partner_id.vat), 
                                                                        '|', ('ncf', '=', ncf), ('name', '=', ncf)
                                                                    ])

                if ncf_exists > 0:
                    raise exceptions.ValidationError("El comprobante {0} ya fue utilizado en otra factura con el proveedor {1} - {2}."
                                                        .format(ncf, 
                                                                self.partner_id.vat, 
                                                                self.partner_id.name))
            else:
                raise exceptions.UserError(_('You are trying to use a partner who does not have a VAT value. Please verify.'))
            
            _trn_helper = self.env['billing.do.trn.helper'].sudo()

            _trn_helper.is_trn_from_journal_which_use_sequence(ncf)

            if _trn_helper.is_valid_trn_do(ncf):
                _trn_service_helper = self.env['billing.do.trn.http.service.helper'].sudo()
                result = _trn_service_helper.dgii_validate_ncf(self.partner_id.vat, 
                                                                ncf,
                                                                self.env.company.vat,
                                                                self.security_code)

                if not result[0]:
                    if self.invoice_date > result[1]:
                        raise exceptions.ValidationError(_("The tax receipt number {0} entered is not valid or does not belongs to the VAT {1}.")
                                                            .format(ncf, self.partner_id.vat))

                return True

    def __validate_vat_journal_b11(self, model):
        vat_helper = self.env['billing.do.vat.http.service.helper'].sudo()
        vat_response = vat_helper.dgii_get_vat_info(model.partner_id.vat)

        log.info("[KCS] VAT Response: {0}".format(vat_response))
        log.info("[KCS] VAT Response (Status Code): {0}".format(vat_response.status_code))

        es_contribuyente = False
        if vat_response is not None:
            if vat_response.status_code == 200:
                es_contribuyente = bool(vat_response.json()['esContribuyente'])
                if es_contribuyente:
                    partner_id = model.partner_id
                    model.partner_id = None
                    raise exceptions.ValidationError("El proveedor con RNC '{0}' perteneciente a '{1}' esta registrado como contribuyente en la DGII y se le debe solicitar una factura con Valor Fiscal.".format(partner_id.vat, partner_id.name))
                else:
                    return {
                        'warning': {
                            'title': "RNC '{0}' no es contribuyente.".format(model.partner_id.vat),
                            "message": "Se validó que el proveedor con RNC '{0}' perteneciente a '{1}' no está registrado como contribuyente en la DGII.".format(model.partner_id.vat, model.partner_id.name)
                        }
                    }
            elif vat_response.status_code == 404:
                return {
                    'warning': {
                        'title': "RNC '{0}' no es contribuyente.".format(model.partner_id.vat),
                        "message": "Se validó que el proveedor con RNC '{0}' perteneciente a '{1}' no está registrado como contribuyente en la DGII.".format(model.partner_id.vat, model.partner_id.name)
                    }
                }
            else:
                return {
                    'warning': {
                        'title': "Error de conexión con el servicio.".format(model.partner_id.vat),
                        "message": "La comunicación con el servicio de  DGII falló. Valide este RNC '{0}' directamente con la consulta DGII. Si el problema persiste consulte a su administrador.".format(model.partner_id.vat)
                    }
                }

    def __get_journal_sequence(self):
        if self.journal_id:
            if self.type in ('out_refund', 'in_refund'):
                sequence = self.journal_id.refund_sequence_id
                sequence_type = _('refund sequence')
            else:
                sequence = self.journal_id.sequence_id
                sequence_type = _('sequence')

            if not sequence:
                raise exceptions.UserError(_("The journal '{0}' doesn\'t have a {1} associated with it.")
                                            .format(self.journal_id.name, sequence_type))
            return sequence
        
        if self.id:
            raise exceptions.UserError(_("There isn\'t a journal associated with this move: {0} ({1}).")
                                        .format(self.name, self.id))
        return None
    
    def _ensure_journal_code_is_set(self):
        if self.journal_id:
            if not self.journal_id.sequence_id.code:
                raise exceptions.UserError(_('The code is missing for the sequence associated with this journal {0}.')
                                                .format(self.journal_id.name))