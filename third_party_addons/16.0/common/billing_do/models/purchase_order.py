
from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.model_create_multi
    def create(self, vals_list):
        new_records = super().create(vals_list)
        if self.env.context.get("l10n_do_send_purchase_mail"):
            mail_template = self.env.ref("billing_do.mail_template_purchase_order_from_replenishment")
            for purchase in new_records:
                mail_template.send_mail(purchase.id,
                    force_send=True,
                    email_layout_xmlid="mail.mail_notification_light",
                )
        return new_records

    @api.model
    def l10n_do_get_users_to_notify(self):
        purchase_group = self.env.ref('purchase.group_purchase_manager')
        partner_ids = purchase_group.users.mapped("partner_id").ids
        return ",".join(map(str, partner_ids))
