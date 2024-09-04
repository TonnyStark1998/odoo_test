{
    'name': "Form web view to customers",
    'summary': """Customers form in web view""",
    'author': "Tonny Velazquez",

    'category': 'crm',
    'version': '16.0.0.0.1',

    'depends': ['mail', 'web', 'website', 'base', 'survey', 'crm'],

    'assets': {
        'web.assets_frontend': [
            'crm_customer_web_form/static/src/js/crm_customer_form.js',
        ],
    },

    'data': [
        'views/crm_customer_form_template.xml',
    ],
}
