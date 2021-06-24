from odoo import models, fields, api, exceptions, _

import datetime
import logging as log

TAX_REPORT_TYPES = [
                    ('606', 'Tax Report 606'),
                    ('607', 'Tax Report 607'),
                    ]

class BillingDoTaxReport(models.Model):
    _name = 'billing.do.tax.report'
    _description = ''''
            This is the model which represents a Tax Report for creating them. This is an abstract model since it would serve as a base class for the specific reports.
    '''

    # Model fields
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
                                            default=lambda self: self.env.user and self.env.user.id or False)

    # Compute methods
    @api.depends('type', 'tax_term_year', 'tax_term_month')
    def _compute_name(self):
        for tax_report in self:
            if tax_report.type and tax_report.tax_term_year and tax_report.tax_term_month:
                tax_report.name = '{} ({}-{})'.format(_('Report') if not tax_report.type 
                                                                    else _('{}'.format(dict(self._fields['type'].selection).get(tax_report.type))), 
                                                                                tax_report.tax_term_year,
                                                                                tax_report.tax_term_month)
            else:
                tax_report.name = _('Report')

    # Selection fields functions
    def _get_years(self):
        years = []
        for year in range(datetime.datetime.now().year - 4, datetime.datetime.now().year + 4):
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
        values['state'] = 'created'
        return super(BillingDoTaxReport, self).create(values)

    @api.model
    def write(self, values):
        if self.state in ['generated']:
            raise exceptions.ValidationError(_('A report which was generated can be modified. You can create another report if you want.'))
        return super(BillingDoTaxReport, self).write(values)

    # Button actions
    def generate_report(self):
        self.write({
            'state':'generated',
            'date_generated': datetime.datetime.now()
        })
        if self.type in ['606']:
            return
        elif self.type in ['607']:
            return
