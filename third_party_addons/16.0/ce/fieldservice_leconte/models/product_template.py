from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.template'

    type_equipment_id = fields.Many2one(
        'fsm.equipment.leconte',
        string='Type Equipment',
    )
