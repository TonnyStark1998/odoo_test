from odoo import fields, models

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    fsm_stage_id = fields.Many2one('fsm.stage', 'Stages in Orders')
