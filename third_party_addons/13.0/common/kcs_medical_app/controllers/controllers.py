# -*- coding: utf-8 -*-
# from odoo import http


# class KcsMedicalApp(http.Controller):
#     @http.route('/kcs_medical_app/kcs_medical_app/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kcs_medical_app/kcs_medical_app/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kcs_medical_app.listing', {
#             'root': '/kcs_medical_app/kcs_medical_app',
#             'objects': http.request.env['kcs_medical_app.kcs_medical_app'].search([]),
#         })

#     @http.route('/kcs_medical_app/kcs_medical_app/objects/<model("kcs_medical_app.kcs_medical_app"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kcs_medical_app.object', {
#             'object': obj
#         })
