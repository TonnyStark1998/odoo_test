# -*- coding: utf-8 -*-

import logging
import datetime

from odoo\
    import models, fields, api

class FreezeMeCustomizationStockProductExpirationAlert(models.Model):
    _name = 'freeze.me.customization.stock.product.expiration.alert'
    _description = 'Stock Products Expiration Alerts'

    prueba = fields.Boolean(string='Prueba')

    def send_product_expiration_alerts(self):
        for days_left in [15, 20, 30]:
            stock_move_lines = self._get_stock_move_lines_by_expiration_days_left(days_left)
            products_owner = self._group_stock_move_lines_by_owner(stock_move_lines)
        
            logging.info('[KCS] Move Lines with Expiration Date: {}'.format(stock_move_lines))
            logging.info('[KCS] Products Expiration List: {}'.format(products_owner))

            self._send_email_to_owner(products_owner, days_left)

    def _get_stock_move_lines_by_expiration_days_left(self, expiration_days_left):
        today = datetime.datetime.now()
        stock_move_lines = self.env['stock.picking']\
            .search([('picking_type_code', 'in', ['incoming']),
                     ('state', 'in', ['done'])])\
            .mapped('move_ids')\
            .mapped('move_line_ids')\
            .filtered(lambda sml: sml.expiration_date
                        and sml.expiration_date > today
                        and (sml.expiration_date - today).days == expiration_days_left)
        return stock_move_lines
    
    def _group_stock_move_lines_by_owner(self, stock_move_lines):
        products_owner = {}
        for stock_move_line in stock_move_lines:
            owner_id = stock_move_line.owner_id.id if stock_move_line.owner_id else None
            if not owner_id:
                owner_id = stock_move_line.move_id.partner_id.id
            
            product = '''<tr>
                            <td style="text-align:left;width:40%;">{}</td>
                            <td style="width:15%;">{}</td>
                            <td style="width:20%;">{}</td>
                            <td style="text-align:right;width:15%;">{}</td>
                        </tr>'''\
                    .format(stock_move_line.product_id.name,
                            stock_move_line.lot_id.name,
                            stock_move_line.expiration_date.strftime('%Y-%m-%d'),
                            stock_move_line.lot_id.product_qty) 
            
            if products_owner.get(owner_id, -1) == -1:
                products_owner.update({owner_id: product})
                continue
            
            products_owner.update({owner_id: '{}{}'.format(products_owner.get(owner_id, ''), product) })
        return products_owner
    
    def _send_email_to_owner(self, products_owner, days_left):
        for owner, products in products_owner.items():
            partner = self.env['res.partner'].browse(owner)
            context = {'products': products, 
                       'owner_name': partner.name,
                       'email_to': partner.email,
                       'email_from': self.env.company.email,
                       'days_left': days_left }
            mail_template = self.env.ref('freeze_me_customization.email_template_products_expiration_days_left_alert')
            mail_template.with_context(context)\
                .send_mail(self.id, force_send=True)