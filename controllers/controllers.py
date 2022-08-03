# -*- coding: utf-8 -*-
from openerp import http

# class FinancieraRekognition(http.Controller):
#     @http.route('/financiera_rekognition/financiera_rekognition/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financiera_rekognition/financiera_rekognition/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financiera_rekognition.listing', {
#             'root': '/financiera_rekognition/financiera_rekognition',
#             'objects': http.request.env['financiera_rekognition.financiera_rekognition'].search([]),
#         })

#     @http.route('/financiera_rekognition/financiera_rekognition/objects/<model("financiera_rekognition.financiera_rekognition"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financiera_rekognition.object', {
#             'object': obj
#         })