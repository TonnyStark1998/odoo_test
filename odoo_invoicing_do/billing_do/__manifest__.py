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
    'version': '0.2',
    'depends': ['base', 'account', 'sale', 'purchase', 'l10n_do', 'account_accountant'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/billing_do_account_journal.xml',
        'views/billing_do_account_move.xml',
        'views/billing_do_ir_sequence.xml',
        'views/billing_do_res_partner.xml',
        'views/billing_do_res_company.xml',
        'views/billing_do_res_config_settings_views.xml',
        'views/billing_do_account_tax.xml',
        'views/billing_do_account_account.xml',
        'views/billing_do_sale_views.xml',
        'views/billing_do_purchase_views.xml',
        'views/billing_do_account_payment_views.xml',
        'views/billing_do_account_payment_reports.xml',
        'views/billing_do_tax_report.xml',
        'views/billing_do_tax_report_item_606.xml',
        'views/billing_do_tax_report_item_607.xml',
        'views/billing_do_res_currency.xml',
        'views/billing_do_trn_type_views.xml',
        'report/billing_do_account_payment_templates.xml',
        'data/default_tax_report_types.xml',
        'data/default_trn_types.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
