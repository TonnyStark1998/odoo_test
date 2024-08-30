from odoo import models, fields, api, _, exceptions
import datetime,\
        logging as log

class ArsDoHealthcareReportArs(models.Model):
    _name = 'ars.do.healthcare.report.ars'
    _description = 'Model representing a Healthcare Report for ARS.'

    name = fields.Char(string='Name',
                        compute='_compute_name')
    state = fields.Selection(selection=[('draft','Draft'),
                                        ('sent', 'Sent'),
                                        ('reconciling', 'Reconciling'),
                                        ('reconciled', 'Reconciled')],
                                string='State',
                                default='draft',
                                required=True,
                                readonly=True)
    report_month = fields.Selection(selection=[('01', '01 - January'),
                                                ('02', '02 - February'),
                                                ('03', '03 - March'),
                                                ('04', '04 - April'),
                                                ('05', '05 - May'),
                                                ('06', '06 - June'),
                                                ('07', '07 - July'),
                                                ('08', '08 - August'),
                                                ('09', '09 - September'),
                                                ('10', '10 - October'),
                                                ('11', '11 - November'),
                                                ('12', '12 - December')],
                                        string='Month',
                                        required=True)
    report_year = fields.Char(string='Year',
                                required=True)
    report_items_count = fields.Integer(string='Report Items Count',
                                        compute='_compute_report_items_count')

    # Relational Fields
    healthcare_provider = fields.Many2one(string='Healthcare Provider',
                                            comodel_name='res.partner',
                                            domain=[('is_ars', '=', True)],
                                            required=True)
    report_items = fields.One2many(string='Report Items',
                                    comodel_name='ars.do.healthcare.report.ars.item',
                                    inverse_name='report_id')

    # Computer Methods
    def _compute_report_items_count(self):
        for report in self:
            report.report_items_count = len(report.report_items)

    @api.depends('healthcare_provider', 'report_year', 'report_month')
    def _compute_name(self):
        for report in self:
            report.name = '{} ({}-{})'.format(report.healthcare_provider.name, report.report_month, report.report_year)

    # Actions Methods
    def action_reconcile(self):
        self._set_report_state('reconciling')
        return self._get_report_view_action('ars_do.ars_do_healthcare_report_ars_item_reconcile_view_tree')

    def action_mark_as_sent(self):
        self._set_report_state('sent')

    def action_mark_as_reconciled(self):
        self._check_amount_paid()
        self._set_report_state('reconciled')

    def action_view(self):
        return self._get_report_view_action('ars_do.ars_do_healthcare_report_ars_item_reconcile_noneditable_view_tree')

    def action_view_printable_version(self):
        return self._get_report_view_action('ars_do.ars_do_healthcare_report_ars_item_printable_view_tree')

    # Constrains Methods
    @api.constrains('report_year')
    def _constrain_report_year(self):
        current_year = datetime.datetime.now().year
        if not ((current_year - 2) <= int(self.report_year) <= (current_year + 1)):
            raise exceptions.ValidationError(_('Year field must be either this year or the year before.'))

    # Private Methods
    def _set_report_state(self, state=''):
        if state == '':
            return
        
        if state == self.state:
            return

        self.write({
            'state': state
        })

    
    def _get_report_view_action(self, view_id):
        return {
            "type": "ir.actions.act_window",
            "res_model": "ars.do.healthcare.report.ars.item",
            "view_mode": "tree",
            "view_id": self.env.ref(view_id).id,
            "domain": [('report_id', '=', self.id)],
            "context": {},
            "name": "Reconcile"
        }

    def _check_amount_paid(self):
        amount_paid = 0.0
        amount_invoiced = 0.0
        for report_item in self.report_items:
            amount_paid += report_item.amount_paid
            amount_invoiced += report_item.amount

        if amount_paid > amount_invoiced:
            raise exceptions.ValidationError(_('This report can\'t be reconciled since the total of the Amount Paid is greater than the total of the Amount.'))