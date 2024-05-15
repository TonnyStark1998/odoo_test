# -*- coding: utf-8 -*-
{
    'name': "Freeze Me Customizations",
    'summary': """
        Ajustes realizados para la empresa Freeze Me.
    """,
    'description': """
        Integra reportes y portales para la empresa Freeze Me.
    """,
    'author': "Accounterprise SRL",
    'website': "http://www.accounterprise.com",
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
        'security/ir.model.access.csv',
        'data/fm_website_data.xml',
        'data/default_fm_customization_stock_picking_bulk.xml',
        'views/fm_customization_stock_picking_views.xml',
        'views/fm_customization_stock_views.xml',
        'views/fm_customization_stock_templates.xml',
        'views/fm_customization_stock_picking_bulk_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
    'post_init_hook': '_freeze_me_post_init',
    'auto_install': False,
}
