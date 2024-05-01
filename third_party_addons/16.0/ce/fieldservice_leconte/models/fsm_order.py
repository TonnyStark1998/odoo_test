from odoo import fields, models, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, AccessError

class FSMOrder(models.Model):
    _inherit = "fsm.order"

    order_number = fields.Char()
    description_product = fields.Char()
    amount_km = fields.Char()
    delay_alert = fields.Char(compute='_compute_delay_alert', readonly=True, store=True)
    active_alert = fields.Boolean(default=False,compute='_compute_delay_alert', store=True)
    today = fields.Date(default=fields.Date.today)
    btu = fields.Char()
    acquisition_date = fields.Date()
    stars_date = fields.Date()
    brand_id = fields.Many2one("fsm.brand")
    type_equipment_id = fields.Many2one("fsm.equipment.leconte")
    execution_time = fields.Float(compute='_compute_execution_time',store=True)
    number_days_open = fields.Integer(compute='_compute_number_days_open',store=True)

    @api.depends("request_early", "date_end")
    def _compute_execution_time(self):
        duration = 0.0
        for rec in self:
            if rec.request_early and rec.date_end:
                start = fields.Datetime.from_string(rec.request_early)
                end = fields.Datetime.from_string(rec.date_end)
                delta = end - start
                duration = delta.total_seconds() / 3600
            rec.execution_time = duration

    @api.depends("acquisition_date", "date_end")
    def _compute_number_days_open(self):
        duration = 0.0
        for rec in self:
            if rec.acquisition_date and rec.date_end:
                start = rec.acquisition_date
                end = rec.date_end.date()
                delta = end - start
                duration = delta.days
            rec.execution_time = duration
            
    @api.depends('today')
    def _compute_delay_alert(self):
        for rec in self:
            active = False
            alert = _('Warning: there is a delay in the work order!')
            if rec.request_early and rec.stage_id.name != 'Completed':
                days = (rec.today - rec.request_early.date()).days
                if days >= 4:
                    active = True
            rec.active_alert = active
            rec.delay_alert = alert
                
    def write(self, values):
        res = super(FSMOrder, self).write(values)
        current_stage_sequence = self.stage_id.sequence
        move_back_stage = self.user_has_groups(
            'fieldservice_leconte.group_fsm_move_back_stage'
        )
        move_stage = self.user_has_groups(
            'fieldservice_leconte.group_fsm_move_stage'
        )
        if values.get('stage_id', False):

            if not move_stage:
                raise UserError(_('You do not have permission to move stages.'))
            
            new_stage_sequence = self.stage_id.browse(values['stage_id']).sequence

            if new_stage_sequence < current_stage_sequence and not move_back_stage:
                raise UserError(_('You do not have permission to go back in stage.'))
        return res
        
class Brand(models.Model):
    _name = "fsm.brand"

    name = fields.Char()


class EquipmentLeconte(models.Model):
    _name = "fsm.equipment.leconte"

    name = fields.Char()
