# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from werkzeug.exceptions import NotFound
import logging

class FreezeMeCustomizationMainController(http.Controller):

    @http.route(['/stock/products/availability'], type='http', auth='user', website=True)
    def stock_products_availability(self, **kwargs):
        current_company = 13 # env.user.partner_id
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        company_products = set(env['stock.picking'].search([('partner_id', '=', current_company)])\
            .move_ids.mapped('product_id'))
        
        # Render page
        return request.render('freeze_me_customization.stock_products_availability', 
            {'products': company_products})