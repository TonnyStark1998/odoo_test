from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    age = fields.Integer()
    weight_loss = fields.Selection(selection=[
        ('less_than_20', 'Less than 20 pounds'), ('20-40', '40 - 80 pounds'),
        ('40-80', '40 - 80 pounds'), ('more_than_80', 'More than 80 pounds')
    ])
    country_id = fields.Many2one(comodel_name='res.country')
    bariatric = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')])
    bariatric_description = fields.Text()
    procedure = fields.Text()
    budget = fields.Selection(selection=[
        ('1000-4000', '1, 000 - 4, 000 USD'), ('4000-8000', '4, 000 - 8, 000 USD'),
        ('8000-12000', '8, 000 - 12, 000 USD'), ('other', 'Other')
    ])

    def create_lead_from_json(self, json_values):
        self.create({
            'name': f"{json_values.get('name')} {json_values.get('surname')} / {json_values.get('procedure')}",
            'phone': json_values.get('phone'),
            'type': 'opportunity',
            'age': json_values.get('age'),
            'weight_loss': json_values.get('weight_loss'),
            'country_id': json_values.get('country_id'),
            'email_from': json_values.get('email'),
            'bariatric': json_values.get('bariatric_surgery'),
            'bariatric_description': json_values.get('surgery_type'),
            'procedure': json_values.get('procedure'),
            'medium_id': json_values.get('medium_id'),
        })
