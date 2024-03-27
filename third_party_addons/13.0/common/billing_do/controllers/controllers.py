# -*- coding: utf-8 -*-
# from odoo import http


# class BillingDo(http.Controller):
#     @http.route('/billing_do/billing_do/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/billing_do/billing_do/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('billing_do.listing', {
#             'root': '/billing_do/billing_do',
#             'objects': http.request.env['billing_do.billing_do'].search([]),
#         })

#     @http.route('/billing_do/billing_do/objects/<model("billing_do.billing_do"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('billing_do.object', {
#             'object': obj
#         })
