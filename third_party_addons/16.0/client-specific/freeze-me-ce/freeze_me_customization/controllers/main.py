# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request

class FreezeMeCustomizationMainController(http.Controller):

    @http.route(['/stock/products/availability'], type='http', auth='user', website=True)
    def stock_products_availability(self, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        current_partner = env.user.partner_id.parent_id

        company_products = set(env['stock.picking']\
            .sudo()\
            .with_company(env.company)\
            .search([('state', 'in', ['done']),
                     '|', ('partner_id', '=', current_partner.id if current_partner else -1),
                        ('owner_id', '=',  current_partner.id if current_partner else -1)])\
            .move_ids.mapped('product_id'))

        # Render page
        return request.render('freeze_me_customization.stock_products_availability', 
            {'products': company_products, 'partner_name': current_partner.name if current_partner else ''})