from odoo import models, fields, api, exceptions, _

import datetime
import logging as log

TAX_REPORT_TYPES = {
                        '606': 'Tax Report 606',
                        '607': 'Tax Report 607'
                    }

class BillingDoTaxReport(models.AbstractModel):
    _name = 'billing.do.tax.report'
    _description = ''''
            This is the model which represents a Tax Report for creating them. This is an abstract model since it would serve as a base class for the specific reports.
    '''

    type = fields.Selection(selection=TAX_REPORT_TYPES,
                                        string='Tax Report Type')
    tax_term = fields.Char(string='Tax Term')