# -*- coding: utf-8 -*-
{
    'name': "Billing DO - Community Edition",
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
    'depends': ['billing_do'],
    # always loaded
    'data': [
        'views/billing_do_tax_report.xml',
        'views/billing_do_ncf_types.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
