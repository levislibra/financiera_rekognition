# -*- coding: utf-8 -*-
{
    'name': "Financiera Reconocimiento de imagenes",

    'summary': """
        Utilizacion de Amazon Rekognition para validar dni, selfie, servicio, etc.""",

    'description': """
        Utilizacion de Amazon Rekognition para validar dni, selfie, servicio, etc.
    """,

    'author': "Librasoft",
    'website': "https://libra-soft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'financiera_prestamos', 'financiera_app'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
				'views/extends_res_company.xml',
				'views/extends_res_partner.xml',
				'views/rekognition_config.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}