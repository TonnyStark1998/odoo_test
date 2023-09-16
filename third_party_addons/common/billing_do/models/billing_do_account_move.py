# -*- coding: utf-8 -*-

import re
import datetime as date
import logging as log

from odoo\
    import models, fields, api, exceptions, _
from odoo.tools\
    import index_exists, drop_index

class BillingDoAccountMove(models.Model):
    _inherit = "account.move"

    # Account Move - Modified Fields
    invoice_date = fields.Date(default=lambda self: self._default_invoice_date())

    # Account Move - New Fields
    income_type = fields.Selection(selection=[
            ('01', '01 - Ingresos por Operaciones (No Financieros)'),
            ('02', '02 - Ingresos Financieros'),
            ('03', '03 - Ingresos Extraordinarios'),
            ('04', '04 - Ingresos por Arrendamientos'),
            ('05', '05 - Ingresos por Venta de Activo Depreciable'),
            ('06', '06 - Otros Ingresos')], 
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
            ('11', '11- GASTOS DE SEGUROS')], 
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

    ncf_serie = fields.Char(string='NCF Serie', default='')

    ncf_date_to = fields.Date(string="NCF valid to:", 
        readonly=True, 
        copy=False, 
        store=True, 
        tracking=True)

    security_code = fields.Char(string='Security Code', copy=False)

    ncf_type = fields.Many2one(comodel_name='billing.do.ncf.type',
        string='NCF Type',
        domain=lambda self: self._get_ncf_type_domain())
    
    ncf_type_sequence = fields.Many2one(comodel_name='ir.sequence.date_range', string='NCF Type Sequence Used')
    
    ncf_type_code = fields.Char(related='ncf_type.type')

    is_tax_valuable = fields.Boolean(string='Is tax valuable?', default=True)

    is_third_party_ncf = fields.Boolean(string='Is third-party NCF?', default=False)

    _sql_constraints = [(
        'unique_name', "", "Another entry with the same name already exists.",
    )]

    def _auto_init(self):
        if index_exists(self.env.cr, 'account_move_unique_name'):
            drop_index(self.env.cr, "account_move_unique_name", self._table)

        # Make all values of `name` different (naming them `name (1)`, `name (2)`...) so that we can add the following UNIQUE INDEX
        self.env.cr.execute("""
            WITH duplicated_sequence AS (
                SELECT name, journal_id, state
                    FROM account_move
                    WHERE state = 'posted'
                    AND name != '/'
                GROUP BY journal_id, name, state
                HAVING COUNT(*) > 1
            ),
            to_update AS (
                SELECT move.id,
                        move.name,
                        move.journal_id,
                        move.state,
                        move.date,
                        row_number() OVER(PARTITION BY move.name, move.journal_id ORDER BY move.name, move.journal_id, move.date) AS row_seq
                    FROM duplicated_sequence
                    JOIN account_move move ON move.name = duplicated_sequence.name
                                        AND move.journal_id = duplicated_sequence.journal_id
                                        AND move.state = duplicated_sequence.state
            ),
            new_vals AS (
                SELECT id,
                        name || ' (' || (row_seq-1)::text || ')' AS name
                    FROM to_update
                    WHERE row_seq > 1
            )
            UPDATE account_move
                SET name = new_vals.name
                FROM new_vals
                WHERE account_move.id = new_vals.id;
        """)
        self.env.cr.execute("""
            CREATE UNIQUE INDEX account_move_unique_name
            ON account_move(name, journal_id, partner_id) WHERE (state = 'posted' AND name != '/');
        """)

    # Account Move - OnChange Field's Functions
    @api.onchange('ncf', 'partner_id', 'security_code', 'invoice_date')
    def _onchange_ncf(self):
        try:
            if self.ncf and len(self.ncf) > 1:
                self.ncf_serie = self.ncf[0]

            if self.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
                if self.is_tax_valuable:
                    if self.ncf_serie in ['E']\
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

                elif self.is_third_party_ncf:
                    if self.ncf_type:
                        if self.ncf_type.type.upper() in ['B11']\
                            and self.partner_id:
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
                    'message': '{0}'.format(ue.args[0]),
                }
            }

        except exceptions.ValidationError as ve:
            return {
                'warning': {
                    'title': _('¡Validation error!'),
                    'message': '{0}'.format(ve.name),
                }
            }

    @api.onchange('is_tax_valuable')
    def _onchange_is_tax_valuable(self):
        if not self.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
            self.name = ''
            if self.is_tax_valuable:
                self.is_third_party_ncf = False
    
    @api.onchange('is_third_party_ncf')
    def _onchange_is_third_party_ncf(self):
        if not self.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
            self.name = ''
            if self.is_third_party_ncf:
                self.is_tax_valuable = False

    @api.onchange('is_tax_valuable', 'ncf_type', 'invoice_date', 'is_third_party_ncf')
    def _onchange_tax_valuable_fields(self):
        if self.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
            if not self.is_tax_valuable:
                self.ncf_type = ''
                return

            result = \
                self._validate_ncf_type(self.ncf_type, self.invoice_date)
            
            if result != True:
                self.ncf_type = ''
                return result
            
            return self._compute_name_tax_valuable_invoice()
        else:
            if self.is_third_party_ncf:
                result = \
                    self._validate_ncf_type(self.ncf_type, self.invoice_date)
                
                if result != True:
                    self.ncf_type = ''
                    return result

                return self._compute_name_tax_valuable_invoice()

    # Account Move - Compute Field's Functions
    @api.depends('invoice_date')
    def _compute_move_date(self):
        for move in self:
            if move.invoice_date and move.move_type not in ['entry']:
                move.date = move.invoice_date
            else:
                move.date = fields.Date.today()

    # Account Move - Contraints Field's Functions
    @api.constrains('ncf', 'move_type')
    def _check_ncf(self):
        for move in self:
            try:
                if move.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
                    if move.is_tax_valuable:
                        if move.ncf_type.serie in ['E']\
                            and not move.security_code:

                            raise exceptions.UserError(_("For E NCF ('{0}') type you have to provide the security code.").format(self.ncf))

                        self._validate_ncf(move.ncf)
                elif self.is_third_party_ncf:
                    if move.ncf_type:
                        if move.ncf_type.type.upper() in ['B11']\
                            and move.partner_id:
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

    @api.constrains('name', 'state', 'journal_id')
    def _check_unique_sequence_number(self):
        moves = self.filtered(lambda move: move.state == 'posted')

        if not moves:
            return
        
        self.flush_model(['name', 'journal_id', 'move_type', 'state'])

        # /!\ Computed stored fields are not yet inside the database.
        self._cr.execute('''
            SELECT move2.id
            FROM account_move move
            INNER JOIN account_move move2 ON
                move2.name = move.name
                AND move2.journal_id = move.journal_id
                AND move2.move_type = move.move_type
                AND move2.id != move.id
                AND move2.company_id = move.company_id
                AND move2.partner_id = move.partner_id
            WHERE move.id IN %s AND move2.state = 'posted'
        ''', [tuple(moves.ids)])
        res = self._cr.fetchone()
        if res:
            raise exceptions.ValidationError(_('Posted journal entry must have an unique sequence number per company.'))

    # Account Move - Overriden Functions
    def _post(self, soft=True):
        try:
            for move in self:
                self._set_name_for_out_move(move)
                self._set_ncf_date_to(move)
                
                if not move.posted_before:
                    move._move_to_next_sequence_number(move.ncf_type_sequence)

            return super()._post(soft)
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
            raise exceptions.UserError(
                    _('There is(are) a(some) line(s) which does not have any product associated. Please correct this error before duplicating.')
                )

        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['context'] = dict(self.env.context)
        action['context']['form_view_initial_mode'] = 'edit'
        action['context']['view_no_maturity'] = False
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = self.copy().id
        return action

    def js_assign_outstanding_line(self, line_id):
        super().js_assign_outstanding_line(line_id)

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

    @api.depends('ncf_type', 'is_tax_valuable', 'invoice_date', 'is_third_party_ncf', 'move_type')
    def _compute_name(self):
        for move in self:
            if not move.id:
                return

            if (move.move_type in ['out_invoice', 'out_receipt', 'out_refund']\
                    and not move.is_tax_valuable)\
                or (move.move_type in ['in_invoice', 'in_receipt', 'in_refund']\
                    and not move.is_tax_valuable\
                    and not move.is_third_party_ncf):
                
                if not move.journal_id:
                    return {
                        'warning': {
                            'title': _('¡Validation error!'),
                            'message': _('You must select a journal for this entry.')
                        }
                    }

                self = \
                    self.sorted(lambda m: (m.date, m.ref or '', m.id))
                sequence_prefix = '{}/{}/{}'.format(move.journal_id.code,
                                                        date.datetime.now().year, 
                                                        str(date.datetime.now().month)
                                                            .rjust(2, '0'))
                highest_name = \
                    self[0]._get_last_sequence(lock=False, 
                                               with_prefix=sequence_prefix) if self else False

                move.sequence_prefix = sequence_prefix
                if highest_name:
                    move.sequence_number = \
                        int(re.match('.*/([0-9]*)', highest_name).group(1)) + 1
                else:
                    move.sequence_number = 1
                
                move.name = '{}/{}'.format(move.sequence_prefix, 
                                            str(move.sequence_number)
                                                .rjust(6, '0'))
            else:
                super(BillingDoAccountMove, move)._compute_name()
                move._onchange_tax_valuable_fields()

    def _onchange_name_warning(self):
        if not self.is_tax_valuable:
            super()._onchange_name_warning()

    # Account Move - Default Value Functions
    def _default_invoice_date(self):
        move_type = self._context.get('default_move_type')
        # If move_type is out_invoice or in_invoice, set invoice_date to today
        if move_type in ['out_invoice', 'in_invoice']:
            return date.datetime.today()

    # Account Move - Helper Functions
    def _validate_ncf(self, ncf):
        if ncf:
            if not self.partner_id:
                raise exceptions.UserError(
                        _('Please, first select the vendor and then enter the value for NCF field.')
                    )

            if not self.invoice_date:
                raise exceptions.UserError(
                        _('Please, first select the invoice date and then enter the value for NCF field.')
                    )

            if self.partner_id.vat:
                ncf_exists = self.env['account.move']\
                    .search_count([
                        ('id', '!=', self.id if self.id else 0), 
                        ('move_type', 'in', ['in_invoice', 'in_refund', 'in_receipt']), 
                        ('partner_id.vat', '=', self.partner_id.vat), 
                        '|', ('ncf', '=', ncf), ('name', '=', ncf)
                    ])

                if ncf_exists > 0:
                    raise exceptions.ValidationError(
                        "El comprobante {0} ya fue utilizado en otra factura con el proveedor {1} - {2}."
                            .format(ncf, 
                                self.partner_id.vat, 
                                self.partner_id.name)
                    )
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

    def _compute_name_tax_valuable_invoice(self):
        if self.posted_before:
            return

        current_sequence = self.ncf_type\
            .sequence\
            .date_range_ids\
            .filtered(lambda range:
                range.date_from <= self.invoice_date and
                range.date_to >= self.invoice_date and
                range.number_next <= range.number_last
            )

        if not current_sequence:
            self.ncf_type = None
            return {
                'warning': {
                    'title': _('¡Validation error!'),
                    'message': 
                        _('The sequence associated with this NCF type does not have a valid range according to the Invoice Date.')
                }
            }

        if len(current_sequence) > 1:
            current_sequence = current_sequence[0]

        self.ncf_type_sequence = current_sequence
        self.show_name_warning = False
        self.sequence_prefix = self.ncf_type.type
        self.sequence_number = current_sequence.number_next
        self.name = '%s%s' % \
            (self.ncf_type.type, 
                str(self.sequence_number)
                .rjust(self.ncf_type.sequence.padding, '0'))
            
    def _get_ncf_type_domain(self):
        move_type = self._context.get('default_move_type')
        if move_type in ['out_invoice', 'out_receipt', 'out_refund']:
            return [('is_sale_usable', '=', True)]
        else:
            return [('is_purchase_usable', '=', True)]
    
    def _validate_ncf_type(self, ncf_type, invoice_date):
        is_valid = True
        warning_message = ''
        if ncf_type:
            if not invoice_date:
                is_valid = False
                warning_message = \
                    _('Please select the invoice date first.')

            if not ncf_type.sequence:
                is_valid = False
                warning_message = \
                    _('This type of NCF does not have any sequence associated.')

            if len(ncf_type.sequence.date_range_ids) < 1:
                is_valid = False
                warning_message = \
                    _('The sequence associated with this NCF type does not contain any range.')
        else:
            return None

        if is_valid:
            return is_valid
        else:
            return {
                    'warning': {
                        'title': _('¡Validation error!'),
                        'message': warning_message
                    }
                }
        
    def _set_name_for_out_move(self, move):
        if move.is_tax_valuable \
            and move.move_type in ['in_invoice', 'in_refund', 'in_receipt']\
            and move.is_tax_valuable:

            move.name = move.ncf

    def _set_ncf_date_to(self, move):
        if move.is_tax_valuable and \
            (move.move_type in ['out_invoice', 'out_refund', 'out_receipt'] \
            or (move.move_type in ['in_invoice', 'in_refund', 'in_receipt'] \
                and move.is_third_party_ncf)):
            
            if not move.ncf_type_sequence:
                move.ncf_date_to = '31/12/{}'.format(date.datetime.now().strftime('%Y'))
            else:
                move.ncf_date_to = move.ncf_type_sequence.date_to
    
    def _move_to_next_sequence_number(self, sequence):
        sequence.number_next_actual = \
                sequence.number_next + 1
        sequence._set_number_next_actual()

    def _must_check_constrains_date_sequence(self):
        return False