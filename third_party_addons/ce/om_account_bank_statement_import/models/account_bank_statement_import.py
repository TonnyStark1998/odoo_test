# -*- coding: utf-8 -*-
import base64
import io
import os
import logging
import tempfile
import binascii

from odoo \
    import fields, models, _
from odoo.exceptions \
    import ValidationError
from datetime \
    import datetime

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot ''import csv''.')

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot ''import xlrd''.')

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    # Ensure transactions can be imported only once (if the import format provides unique transaction ids)
    unique_import_id = fields.Char(string='Import ID', readonly=True, copy=False)

    _sql_constraints = [
        ('unique_import_id', 
         'unique (unique_import_id)', 
         _('A bank account transactions can be imported only once!'))
    ]


class AccountBankStatementImport(models.TransientModel):
    _name = 'account.bank.statement.import'
    _description = 'Import Bank Statement'

    ACCEPTED_FILE_TYPES = ('csv', 'xlsx')

    attachment_ids = \
        fields.Many2many('ir.attachment',
                        string='Files',
                        required=True,
                        help='Get you bank statements in electronic format from your bank and select them here.')

    statement_formats = fields.Char(string='Statement Formats',
                                    store=False,
                                    default=lambda self:', '.join(self.ACCEPTED_FILE_TYPES))

    def _get_partner(self, value):
        partner = \
            self.env['res.partner'].search([('name', '=', value)], limit=1)
        return partner.id if partner else False

    def _get_currency(self, value):
        currency = \
            self.env['res.currency'].search([('name', '=', value)], limit=1)
        return currency.id if currency else False

    def _create_statement(self, values):
        statement = \
            self.env['account.bank.statement'].create(values)
        return statement

    def import_file(self):
        for data_file in self.attachment_ids:
            _file_name = data_file.name.lower()
            _file_type = self._get_file_type(_file_name)
            _logger.info('[KCS] File types: {}'.format(', '.join(self.ACCEPTED_FILE_TYPES)))
            if _file_type in self.ACCEPTED_FILE_TYPES:
                statement = False
                statement_name = _('Statement of ') + datetime.now().strftime('%Y-%M-%d %H:%I')
                journal_id = self.env.context.get('active_id')
                if _file_type == 'csv':
                    keys = ['date', 'payment_ref', 'partner_id', 'amount', 'currency_id']
                    csv_data = base64.b64decode(data_file.datas)
                    data_file = io.StringIO(csv_data.decode("utf-8"))
                    data_file.seek(0)
                    file_reader = []
                    values = {}
                    csv_reader = csv.reader(data_file, delimiter=',')
                    file_reader.extend(csv_reader)
                    vals_list = []
                    date = False
                    for i in range(len(file_reader)):
                        field = list(map(str, file_reader[i]))
                        values = dict(zip(keys, field))
                        if values:
                            if i == 0:
                                continue
                            else:
                                if not date:
                                    date = field[0]
                                values.update({
                                    'date': field[0],
                                    'payment_ref': field[1],
                                    'ref': field[2],
                                    'partner_id': self._get_partner(field[3]),
                                    'amount': field[4],
                                    'currency_id':  self._get_currency(field[5]),
                                    'journal_id': journal_id
                                })
                                vals_list.append((0, 0, values))
                    statement_vals = {
                        'name': statement_name,
                        'journal_id': journal_id,
                        'line_ids': vals_list
                    }
                    if len(vals_list) != 0:
                        statement = self._create_statement(statement_vals)
                elif  _file_type == 'xlsx':
                    fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                    fp.write(binascii.a2b_base64(data_file.datas))
                    fp.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(fp.name)
                    sheet = workbook.sheet_by_index(0)
                    vals_list = []
                    for row_no in range(sheet.nrows):
                        values = {}
                        if row_no <= 0:
                            map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                        else:
                            line = list(map(lambda row: 
                                            isinstance(row.value, bytes) 
                                            and row.value.encode('utf-8') 
                                            or str(row.value), 
                                        sheet.row(row_no)))
                            values.update({
                                'date': line[0],
                                'payment_ref': line[1],
                                'ref': line[2],
                                'partner_id': self._get_partner(line[3]),
                                'amount': line[4],
                                'currency_id': self._get_currency(line[5]),
                                'journal_id': journal_id
                            })
                            vals_list.append((0, 0, values))
                    statement_vals = {
                        'name': statement_name,
                        'journal_id': journal_id,
                        'line_ids': vals_list
                    }
                    if len(vals_list) != 0:
                        statement = self._create_statement(statement_vals)
                if statement:
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'account.bank.statement',
                        'view_mode': 'form',
                        'res_id': statement.id,
                        'views': [(False, 'form')],
                    }
            else:
                raise ValidationError(_("Unsupported File Type!"))

    def _journal_creation_wizard(self, currency, account_number):
        """ Calls a wizard that allows the user to carry on with journal creation """

        return {
            'name': _('Journal Creation'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement.import.journal.creation',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'statement_import_transient_id': self.env.context['active_id'],
                'default_bank_acc_number': account_number,
                'default_name': _('Bank') + ' ' + account_number,
                'default_currency_id': currency and currency.id or False,
                'default_type': 'bank',
            }
        }

    def _check_journal_bank_account(self, journal, account_number):
        # Needed for CH to accommodate for non-unique account numbers
        sanitized_acc_number = journal.bank_account_id.sanitized_acc_number
        if " " in sanitized_acc_number:
            sanitized_acc_number = sanitized_acc_number.split(" ")[0]
        return sanitized_acc_number == account_number

    def _get_file_type(self, file):
        if file:
            file_name_splitted = os.path.splitext(file)
            if file_name_splitted[1]:
                return file_name_splitted[1].replace('.', '')
        return ''

    def get_sample_file_csv(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=ir.attachment'
                '&download=true'\
                '&id={}'.format(str(self.env.ref('om_account_bank_statement_import.om_account_bank_statement_import_sample_file_csv').id)),
            'target': 'self',
        }

    def get_sample_file_xlsx(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=ir.attachment'
                '&download=true'\
                '&id={}'.format(str(self.env.ref('om_account_bank_statement_import.om_account_bank_statement_import_sample_file_xlsx').id)),
            'target': 'self',
        }