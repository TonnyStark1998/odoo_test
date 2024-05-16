# -*- coding: utf-8 -*-

import logging
import datetime

from odoo\
    import models, fields, api

class FreezeMeCustomizationStockProductExpirationAlert(models.Model):
    _name = 'freeze.me.customization.stock.product.expiration.alert'
    _description = """
        Agrega la funcionalidad de alerta de caducidad de productos según requerimiento de la empresa Freeze Me.
    """

    def send_product_expiration_alerts(self):
        self._send_thirty_days_alert()
        self._send_twenty_days_alert()
        self._send_fifteen_days_alert()

    def _send_thirty_days_alert(self):
        pass

    def _send_twenty_days_alert(self):
        pass

    def _send_fifteen_days_alert(self):
        today = datetime.datetime.now()
        stock_move_lines = self.env['stock.picking']\
            .search([('picking_type_code', 'in', ['incoming']),
                     ('state', 'in', ['done'])])\
            .mapped('move_ids')\
            .mapped('move_line_ids')\
            .filtered(lambda sml: sml.expiration_date
                        and sml.expiration_date > today
                        and (sml.expiration_date - today).days == 15)
        
        products_owner = {}
        for stock_move_line in stock_move_lines:
            owner_id = stock_move_line.owner_id.id if stock_move_line.owner_id else None
            if not owner_id:
                owner_id = stock_move_line.move_id.partner_id.id
            
            if not products_owner.get(owner_id, -1):
                products_owner.update({owner_id: stock_move_line.product_id.name})
                continue
            
            products_owner.update({owner_id: 
                '{}\n{}'.format(products_owner.get(owner_id), stock_move_line.product_id.name)})
    
        for owner, products in products_owner.items():
            mail_template = self.env.ref('freeze_me_customization.email_template_thirty_days_alert')
            mail_template.send_mail(self.id, 
                force_send=True, 
                email_values={'products': products,
                              'owner': self.env['res.partner'].browse(owner).name})

        logging.info('[KCS] Move Lines with Expiration Date: {}'.format(stock_move_lines))
        logging.info('[KCS] Products Expiration List: {}'.format(products_owner))