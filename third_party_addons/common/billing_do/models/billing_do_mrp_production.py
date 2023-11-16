# -*- coding: utf-8 -*-

from odoo import models, exceptions, _

class BillingDoAccountTax(models.Model):
    _inherit = 'mrp.production'

    def _button_mark_done_sanity_checks(self):
        if self.env.user.has_group('billing_do.enforce_mrp_production_attachments'):
            attachments_count = \
                self.env['ir.attachment']\
                    .search_count([('res_id', '=', self.id),
                                   ('res_model', '=', 'mrp.production')])

            if attachments_count < 1:
                raise exceptions.ValidationError(_('In order to mark the Production Order as Done, you must attach at least one file.'))

        super()._button_mark_done_sanity_checks()