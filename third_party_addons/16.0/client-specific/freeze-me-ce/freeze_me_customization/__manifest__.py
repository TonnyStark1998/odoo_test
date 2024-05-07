# -*- coding: utf-8 -*-
{
    'name': "Freeze Me Customizations",
    'summary': """
        Ajustes realizados para la empresa Freeze Me.
    """,
    'description': """
        Integra reportes y portales para la empresa Freeze Me.
    """,
    'author': "Koala Creative Software SRL",
    'website': "http://www.koalacreativesoftware.com",
    'category': 'Accounting/Accounting',
    'version': '1.0',
    'depends': ['base', 
                'account', 
                'delivery', 
                'sale_management', 
                'purchase', 
                'crm', 
                'stock', 
                'l10n_do',
                'mrp',
                'billing_do',
                'website'],
    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'data/fm_website_data.xml',
        'views/fm_customization_stock_views.xml',
        'views/fm_customization_stock_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
