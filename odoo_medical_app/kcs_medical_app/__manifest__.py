# -*- coding: utf-8 -*-
{
    'name': "KCS Medical App",
    'summary': """
        Módulo que permite el registro y manejo del historial médico de los pacientes.""",
    'description': """
        Permite el registro de la información médica de un paciente tomando en consideración cada uno de los aspectos relevantes que son requeridos para evaluaciones quirúrgicas y recetarias.
    """,
    'author': "Koala Creative Software SRL",
    'website': "http://www.koalacreativesoftware.com",
    'category': 'Medical/History',
    'version': '0.1',
    'css': ['static/src/css/*.css'],
    'depends': ['base', 'contacts', 'billing_do'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/kcs_medical_app_patient_views.xml',
        'views/kcs_medical_app_blood_type_views.xml',
        'views/kcs_medical_app_diseases_views.xml',
        'views/kcs_medical_app_virus_views.xml',
        'views/kcs_medical_app_allergies_views.xml',
        'views/kcs_medical_app_stetic_contraindications_views.xml',
        'views/kcs_medical_app_stetic_skin_type_views.xml',
        'views/kcs_medical_app_body_part_views.xml',
        'views/kcs_medical_app_patient_evolution_views.xml',
        'views/kcs_medical_app_product_template.xml',
        'views/kcs_medical_app_patient_functional_medicine_nutrition_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
