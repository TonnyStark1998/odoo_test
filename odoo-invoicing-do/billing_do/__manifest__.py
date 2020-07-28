# -*- coding: utf-8 -*-
{
    'name': "Billing DO",
    'summary': """
        Ajustes del proceso de facturación para la República Dominicana.
    """,
    'description': """
        Integra los campos y funcionalidades requeridas para la facturación en la República Dominicana.
    """,
    'author': "Koala Creative Software SRL",
    'website': "http://www.koalacreativesoftware.com",
    'category': 'Accounting/Accounting',
    'version': '0.1',
    'depends': ['base', 'account', 'account_accountant'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/billing_do_account_journal.xml',
        'views/billing_do_account_move.xml',
        'views/billing_do_ir_sequence.xml',
        'views/billing_do_res_partner.xml',
        'views/billing_do_res_company.xml',
        'report/report_invoice.xml',
        'report/external_layout_standard.xml',
        'views/billing_do_res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
