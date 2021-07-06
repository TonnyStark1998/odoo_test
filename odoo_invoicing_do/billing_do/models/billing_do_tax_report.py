from odoo import models, fields, api, exceptions, _

import datetime
import calendar
import logging as log

TAX_REPORT_TYPES = [
                    ('606', 'Tax Report 606'),
                    ('607', 'Tax Report 607'),
                    ]

class BillingDoTaxReport(models.Model):
    _name = 'billing.do.tax.report'
    _description = 'Billing DO Tax Report'

    # Model fields
    company_id = fields.Many2one(string='Company',
                                    comodel_name='res.company',
                                    default=lambda self: self.env.company.id)

    state = fields.Selection(selection=[
                                        ('draft', 'Draft'),
                                        ('created', 'Created'),
                                        ('generated', 'Generated'),
                                        ],
                                string='State',
                                default='draft')
    name = fields.Char(string='Name',
                        store=True,
                        readonly=True,
                        compute='_compute_name')
    type = fields.Selection(selection=TAX_REPORT_TYPES,
                                string='Tax Report Type',
                                required=True)
    tax_term_year = fields.Selection(selection=lambda self: self._get_years(),
                                        string='Tax Term Year',
                                        required=True,
                                        index=True)
    tax_term_month = fields.Selection(selection=lambda self: self._get_months(),
                                        string='Tax Term Month',
                                        required=True,
                                        index=True)
    date_generated = fields.Date(string='Generated Date',
                                    readonly=True)
    user_who_generated = fields.Many2one('res.users', 
                                            string='User Who Generated', 
                                            readonly=True, 
                                            required=True, 
                                            ondelete='restrict', 
                                            default=lambda self: self.env.user 
                                                                    and self.env.user.id 
                                                                    or False)

    tax_report_items = fields.One2many(string='Tax Report Items',
                                        comodel_name='billing.do.tax.report.item',
                                        inverse_name='tax_report',
                                        default=False)

    # Compute methods
    @api.depends('type', 'tax_term_year', 'tax_term_month')
    def _compute_name(self):
        for tax_report in self:
            if tax_report.type \
                and tax_report.tax_term_year \
                and tax_report.tax_term_month:
                tax_report.name = '{} ({}-{})'.format(_('Report') if not tax_report.type 
                                                                    else _('{}'.format(dict(self._fields['type'].selection)
                                                                                            .get(tax_report.type))), 
                                                                                tax_report.tax_term_year,
                                                                                tax_report.tax_term_month)
            else:
                tax_report.name = _('Report')

    # Selection fields functions
    def _get_years(self):
        years = []
        for year in range(datetime.datetime.now().year - 4, 
                            datetime.datetime.now().year + 1):
            years.append((str(year), str(year)))
        return years
    
    def _get_months(self):
        months = []
        for month in range(1,13):
            months.append((str(month).rjust(2,'0'), str(month).rjust(2,'0')))
        return months

    # Model functions
    @api.model
    def create(self, values):
        reports = self.search([('type', '=', values['type']), 
                                ('tax_term_year', '=', values['tax_term_year']),
                                ('tax_term_month', '=', values['tax_term_month'])])\
                        .sorted(lambda report: report.create_date, False)

        # TODO: This limit value can be parametrized
        if len(reports) >= 5:
            reports[0].unlink()
        values['state'] = 'created'
        return super(BillingDoTaxReport, self).create(values)

    @api.model
    def write(self, values):
        if self.state in ['generated']:
            raise exceptions.ValidationError(_('A report which was generated can be modified. You can create another report if you want.'))
        return super(BillingDoTaxReport, self).write(values)

    # Button actions
    def action_generate_report(self):
        search_domain = [('invoice_date', '>=', datetime
                                                    .datetime(int(self.tax_term_year), 
                                                                int(self.tax_term_month), 
                                                                1)),
                            ('invoice_date', '<=', datetime
                                                        .datetime(int(self.tax_term_year), 
                                                                int(self.tax_term_month), 
                                                                calendar
                                                                    .monthrange(int(self.tax_term_year),
                                                                                int(self.tax_term_month))[1])),
                            ('state', 'in', ['posted']),
                            ('journal_id.is_tax_valuable', '=', True)]
        
        if self.type in ['606']:
            count_moves = self.env['billing.do.tax.report.item.606']\
                                .generate_items(search_domain, self)
        elif self.type in ['607']:
            count_moves = self.env['billing.do.tax.report.item.607']\
                                .generate_items(search_domain, self)

        self.write({
            'state':'generated',
            'date_generated': datetime.datetime.now()
        })

        res_model, view_id = self._get_action_window_by_type(self.type)
        return {
            'name': _('Report Items'),
            'type': 'ir.actions.act_window',
            'res_model': res_model,
            'res_id': self.id,
            'view_mode': 'tree',
            'view_id': self.env.ref('billing_do.{}'.format(view_id)).id,
            'target': 'current',
            'domain': '[]',
            'limit': count_moves,
            'context': '{}'
        }

    def action_show_report_items(self):
        res_model, view_id = self._get_action_window_by_type(self.type)
        return {
            'name': _('Report Items'),
            'type': 'ir.actions.act_window',
            'res_model': res_model,
            'res_id': self.id,
            'view_mode': 'tree',
            'view_id': self.env.ref('billing_do.{}'.format(view_id)).id,
            'target': 'current',
            'domain': '[]',
            'limit': self.env[res_model]\
                            .search_count([('tax_report', '=', self.id)]),
            'context': '{}'
        }

    # Helpers methods
    def _get_action_window_by_type(self, type):
        res_model = 'billing.do.tax.report'
        view_id = 'billing_do_tax_report_view_form'

        if type in ['606']:
            res_model = 'billing.do.tax.report.item.606'
            view_id = 'billing_do_tax_report_item_606_view_tree'
        elif type in ['607']:
            res_model = 'billing.do.tax.report.item.607'
            view_id = 'billing_do_tax_report_item_607_view_tree'

        return res_model, view_id

class BillingDoTaxReportItem(models.Model):
    _name = 'billing.do.tax.report.item'
    _description = '''
        This model represents an item for Tax Report.
    '''
    _check_company_auto = True

    # Model fields
    company_id = fields.Many2one(string='Company',
                                    comodel_name='res.company',
                                    default=lambda self: self.env.company.id)

    vat = fields.Char(string='Tax Contributor ID')
    vat_type = fields.Char(string='Tax Contributor Type')
    move = fields.Char(string='Tax Receipt Number')
    move_reversed = fields.Char(string='Tax Receipt Reversed')

    tax_report = fields.Many2one(string='Tax Report',
                                    comodel_name='billing.do.tax.report',
                                    ondelete='cascade',
                                    check_company=True)
    
    def generate_item(self, move, tax_report):
        return {
            'vat': '' if not move.partner_id else move.partner_id.vat,
            'vat_type': 2 if move.partner_id 
                                and move.partner_id.tax_contributor_type != '1' 
                            else move.partner_id.tax_contributor_type,
            'move': move.ncf if move.ncf else move.name,
            'move_reversed': '' if move.type not in ['in_refund', 'out_refund'] 
                                    else move.reversed_entry_id.name,
            'tax_report': tax_report.id
        }