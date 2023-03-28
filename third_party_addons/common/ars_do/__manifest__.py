# -*- coding: utf-8 -*-
{
    'name': "Ars Do App",
    'summary': """
        Administración de seguros médicos en la República Dominicana.""",
    'description': """
        Módulo que la captura de información y reportería para la administración de facturas que posee una cobertura de seguro médico en la República Dominicana
    """,
    'author': "Koala Creative Software SRL",
    'website': "http://www.koalacreativesoftware.com",
    'category': 'Accounting/Accounting',
    'version': '0.1',
    'css': ['static/src/css/*.css'],
    'depends': ['base', 
                'contacts', 
                'sale', 
                'sale_management', 
                'billing_do', 
                'professional_templates'],
    'data': [
        'security/ir.model.access.csv',
        'data/ars_do_res_partner_category.xml',
        'data/ars_do_default_healthcare_providers.xml',
        'data/ars_do_healthcare_medicines.xml',
        'data/ars_do_ir_attachment_patient_form.xml',
        'views/ars_do_account_move_views.xml',
        'views/ars_do_healthcare_card.xml',
        'views/ars_do_healthcare_plans.xml',
        'views/ars_do_res_partner_healthcare_common.xml',
        'views/ars_do_res_partner_healthcare_provider.xml',
        'views/ars_do_res_partner_healthcare_patient.xml',
        'views/ars_do_healthcare_medical_record.xml',
        'views/ars_do_healthcare_medicines.xml',
        'views/ars_do_healthcare_report_ars.xml',
        'views/ars_do_healthcare_report_ars_item.xml',
        'views/ars_do_healthcare_report_actions.xml',
        'views/ars_do_sale_views.xml',
        'views/ars_do_template_invoice_lines.xml',
    ],
    'qweb':[
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
