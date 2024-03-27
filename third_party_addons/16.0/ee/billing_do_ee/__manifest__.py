# -*- coding: utf-8 -*-
{
    'name': "Billing DO - Enterprise Edition",
    'summary': """
        Ajustes del proceso de facturación para la República Dominicana.
    """,
    'description': """
        Integra los campos y funcionalidades requeridas para la facturación en la República Dominicana.
    """,
    'author': "Koala Creative Software SRL",
    'website': "http://www.koalacreativesoftware.com",
    'category': 'Accounting/Accounting',
    'version': '1.0',
    'depends': ['account_accountant', 'billing_do'],
    # always loaded
    'data': [
        'views/billing_do_stock_report_views.xml',
        'views/billing_do_tax_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
