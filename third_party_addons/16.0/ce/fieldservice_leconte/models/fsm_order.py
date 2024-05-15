from odoo import fields, models, api, _
import datetime
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class FSMOrder(models.Model):
    _inherit = "fsm.order"

    order_number = fields.Char()
    description_product = fields.Char()
    amount_km = fields.Char()
    delay_alert = fields.Char(compute='_compute_delay_alert', readonly=True, store=True)
    active_alert = fields.Boolean(default=False,compute='_compute_delay_alert', store=True)
    today = fields.Datetime(default=datetime.datetime.now())
    acquisition_date = fields.Date()
    equipment_series = fields.Char('Equipment Series')
    brand_id = fields.Many2one("fsm.brand")
    type_equipment_id = fields.Many2one("fsm.equipment.leconte")
    execution_time = fields.Integer(compute='_compute_execution_time',store=True)
    number_days_open = fields.Integer(compute='_compute_number_days_open',store=True)
    active_recurrence = fields.Boolean()
    execution_date = fields.Date(compute='_compute_order_recurrence')
    order_id = fields.Many2one('sale.order')
    order_recurrence = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('quadrennial', 'Quadrennial'),
        ('semiannual', 'Semiannual'),
        ('annual', 'Annual'),
    ])

    date_stage_not_contacted = fields.Datetime(
        compute='_compute_stages_dates',
        store=True,
        tracking=True
    )
    date_stage_contacted = fields.Datetime(
        compute='_compute_stages_dates',
        store=True,
        tracking=True
    )
    date_stage_coordination = fields.Datetime(
        compute='_compute_stages_dates',
        store=True,
        tracking=True
    )
    date_stage_instalation = fields.Datetime(
        compute='_compute_stages_dates', 
        store=True,
        tracking=True
    )

    @api.depends('stage_id')
    def _compute_stages_dates(self):
        date = fields.datetime.now()
        for stage in self.stage_id:

            stage = stage.name
            if stage == 'Contactado':
                self.date_stage_not_contacted = date
            elif stage == 'En Coordinación':
                self.date_stage_contacted = date
            elif stage == 'Instalación':
                self.date_stage_coordination = date
            elif stage in ['Completado', 'Completed']:
                self.date_stage_instalation = date

    @api.depends("request_early", "date_end")
    def _compute_execution_time(self):
        duration = 0.0
        for rec in self:
            date_end = rec.date_end if rec.date_end else fields.Datetime.now()
            if rec.request_early and date_end:
                start = rec.request_early
                end = date_end
                delta = end - start
                duration = delta.days
            rec.execution_time = duration

    @api.depends("acquisition_date", "date_end")
    def _compute_number_days_open(self):
        duration = 0.0
        for rec in self:
            date_end = rec.date_end.date() if rec.date_end else fields.Date.today()
            if rec.acquisition_date and date_end:
                start = rec.acquisition_date
                end = date_end
                delta = end - start
                duration = delta.days
            rec.number_days_open = duration
            
    @api.depends('today', 'request_early')
    def _compute_delay_alert(self):
        today = datetime.datetime.now()
        orders = self.search([])
        for rec in orders:
            active = False
            alert = _('Warning: there is a delay in the work order!')
            if rec.request_early and rec.stage_id.name not in [
                'Cancelled',
                'Cancelado',
                'Completed', 
                'Completado',
            ]:
                days = (today - rec.request_early).days
                if days >= 4:
                    active = True
            rec.active_alert = active
            rec.delay_alert = alert
                
    def write(self, values):
        res = super(FSMOrder, self).write(values)
        current_stage_sequence = self.stage_id.sequence
        order_stage_id = self.env['project.task.type'].search([
            ('fsm_stage_id','=', self.stage_id.id)
        ],limit=1)
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
            
            self.project_task_id.write({'stage_id': order_stage_id.id})
        return res

    @api.model
    def create(self, vals):
        res = super(FSMOrder, self).create(vals)
        project_id = vals.get('project_id', False)
        location = res.location_id.name
        order_number = vals.get('order_number', False)

        if project_id:
           project_task_id = self.env['project.task'].create({
                'name': '%s - %s' % (location, order_number),
                'project_id': project_id,
            })
           res.project_task_id = project_task_id.id
        return res
    
    @api.depends('order_recurrence', 'date_end', 'active_recurrence')
    def _compute_order_recurrence(self):
        excution_date = None
        for rec in self:
            if rec.date_end and rec.active_recurrence and rec.order_recurrence:
                if rec.order_recurrence == 'monthly':
                    excution_date = rec.date_end + relativedelta(months=1)
                elif rec.order_recurrence == 'quarterly':
                    excution_date = rec.date_end + relativedelta(months=3)
                elif rec.order_recurrence == 'quadrennial':
                    excution_date = rec.date_end + relativedelta(months=4)
                elif rec.order_recurrence == 'semiannual':
                    excution_date = rec.date_end + relativedelta(months=6)
                elif rec.order_recurrence == 'annual':
                    excution_date = rec.date_end + relativedelta(years=1)
                
            if excution_date:
                rec.execution_date = excution_date.date()
            else:
                rec.execution_date = excution_date

    def _duplicate_order(self):
        today = fields.Date.today()
        orders = self.search([
            ('active_recurrence','=', True),
        ])
        for rec in orders:
            if rec.execution_date:
               if rec.execution_date == today:
                    rec.copy({
                        'date_end': None,
                        'active_recurrence': False,
                        'order_recurrence': None
                    })

    def action_create_quotation(self):
        sale_order = self.env['sale.order']
        product = self.env['product.template']
        customer_id = self.project_id.partner_id.id
        type = self.type.name
        number = self.order_number
        product_id = product.search([
            ('type_equipment_id', '=', self.type_equipment_id.id)
        ], limit=1)

        if not self.project_id:
            raise ValidationError(_("There is no assigned project"))
        if not customer_id:
            raise ValidationError(_("The project does not have an assigned client"))
        
        order = sale_order.create({
            'partner_id': customer_id,
            'order_line':[(0, 0, {
                'product_id': product_id.id,
                'name': f"{type} - {number}"
            })]
        })
        self.order_id = order.id
        
    def action_view_quotations(self):
        action = self.env.ref('sale.action_quotations').read()[0]
        action["views"] = [(self.env.ref("sale.view_order_form").id, "form")]
        action["res_id"] = self.order_id.id
        return action

class Brand(models.Model):
    _name = "fsm.brand"

    name = fields.Char()


class EquipmentLeconte(models.Model):
    _name = "fsm.equipment.leconte"

    name = fields.Char()
