from odoo import models, api


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_buy(self, procurements):
        return super(StockRule, self.with_context(l10n_do_send_purchase_mail=True))._run_buy(procurements)
