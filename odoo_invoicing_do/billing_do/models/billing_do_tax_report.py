from odoo import models, fields, api, exceptions, _

import datetime
import calendar
import logging as log

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
    type = fields.Many2one(string='Tax Report Type',
                                comodel_name='billing.do.tax.report.type',
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

    # Compute methods
    @api.depends('type', 'tax_term_year', 'tax_term_month')
    def _compute_name(self):
        for tax_report in self:
            if tax_report.type \
                and tax_report.tax_term_year \
                and tax_report.tax_term_month:
                tax_report.name = '{} ({}-{})'.format(_('Report') if not tax_report.type 
                                                                    else tax_report.type.name, 
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
            raise exceptions\
                    .ValidationError(_('A report which was generated can be modified. You can create another report if you want.'))
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
        
        self.env[self.type.model.model]\
                .generate_items(search_domain, self)

        self.write({
            'state':'generated',
            'date_generated': datetime.datetime.now()
        })

        return self._generate_action_window_json(self.type.view.name, 
                                                    self.type.model.model)

    def action_show_report_items(self):
        return self._generate_action_window_json(self.type.view.name, 
                                                    self.type.model.model)

    def _generate_action_window_json(self, view, model):
        return {
            'name': _('Report Items'),
            'type': 'ir.actions.act_window',
            'res_model': model,
            'view_mode': 'tree',
            'view_id': self.env['ir.ui.view']\
                            .search([('name', '=', view)]).id,
            'target': 'fullscreen',
            'domain': "[('tax_report', '=', active_id)]",
            'limit': self.env[model]\
                            .search_count([('tax_report', '=', self.id)])
        }

class BillingDoTaxReportItem(models.AbstractModel):
    _name = 'billing.do.tax.report.item'
    _description = 'Billing DO - Tax Report Item'
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
    
    def generate_items(self, search_domain_common, tax_report):
        moves = self.env['account.move'].search(search_domain_common)
        
        for move in moves:
            tax_report_item = self.generate_item(move, tax_report)
        
        self.create(tax_report_item)

class BillingDoTaxReportType(models.Model):
    _name = 'billing.do.tax.report.type'
    _description = 'Billing DO - Tax Report Type'

    # Model fields
    name = fields.Char(string='Tax Report Type Name',
                        required=True)
    code = fields.Char(string='Tax Report Type Code',
                        required=True)

    model = fields.Many2one(string='Model',
                                comodel_name='ir.model',
                                domain=lambda self: self._get_tax_report_item_extended_models_domain(['billing.do.tax.report.item'],\
                                                                                                        True),
                                required=True)
    view = fields.Many2one(string='View',
                                comodel_name='ir.ui.view',
                                domain=[],
                                required=True)

    # OnChange Methods
    @api.onchange('model')
    def _on_change_model(self):
        if self.model:
            return {'domain': 
                        {'view': [('model', '=', self.model.model), 
                                    ('type', '=', 'tree')]}}

    # Helper methods
    @api.model
    def _get_tax_report_item_extended_models_domain(self, tax_report_items_models, rescan):
        _ir_models = self.env['ir.model']\
                            .search([('transient', '=', False),\
                                        ('model', 'not in', tax_report_items_models)])

        if rescan:
            rescan = False

            for _ir_model in _ir_models:
                try:
                    _inherit = self.env[_ir_model.model]._inherit

                    if _ir_model.model not in tax_report_items_models \
                        and _inherit in tax_report_items_models:
                        tax_report_items_models.append(_ir_model.model)
                        rescan = True
                
                except KeyError:
                    continue
            
            self._get_tax_report_item_extended_models_domain(tax_report_items_models, rescan)
        
        return "[('model', 'in', %s)]" % tax_report_items_models