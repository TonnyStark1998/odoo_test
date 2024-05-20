# -*- coding: utf-8 -*-

import logging as log

from odoo\
    import models, fields, api, exceptions
import datetime

class FreezeMeCustomizationStockLocation(models.Model):
    _inherit = "stock.location"
    _description = """
        Agrega los campos requeridos para el despliege de la información requerida por la empresa Freeze Me.
    """

    picking_location_ids = fields.One2many(string='Pickings Locations',
        comodel_name='stock.picking',
        inverse_name='location_id')

    picking_location_dest_ids = fields.One2many(string='Pickings Locations Dest',
        comodel_name='stock.picking',
        inverse_name='location_dest_id')

    availability = fields.Selection(selection=[('ocupado', 'Ocupado'), 
            ('desocupado', 'Desocupado')],
        string='Availability',
        compute='_compute_availability',
        store=True)
    
    availability_date = fields.Date(string='Availability Date',
        compute='_compute_availability_date',
        store=True)
    
    reserved_date = fields.Date(string='Reserved Date',
        compute='_compute_reserved_date',
        store=True)

    @api.depends('quant_ids', 'quant_ids.quantity')
    def _compute_availability(self):
        for location in self:
            log.info('[KCS] Quants: {}'.format(location.quant_ids))
            log.info('[KCS] Mapped Quantities: {}'.format(location.quant_ids.mapped("quantity")))
            log.info('[KCS] Sum Mapped Quantities: {}'.format(sum(location.quant_ids.mapped("quantity"))))
            if sum(location.quant_ids.mapped("quantity")) > 0:
                location.availability = 'ocupado'
            else:
                location.availability = 'desocupado'

    @api.depends('picking_location_ids', 'picking_location_ids.state', 
        'picking_location_ids.scheduled_date', 'availability')
    def _compute_availability_date(self):
        for location in self:
            schedule_date = None
            if location.availability in ['ocupado']:
                log.info('[KCS] Pickings: {}'.format(location.picking_location_ids))
                picking_outgoing_in_draft = location.picking_location_ids\
                    .filtered(lambda l: l.state in ['draft']
                        and l.picking_type_id.code in ['outgoing'])
                log.info('[KCS] Pickings(outgoing)(draft): {}'.format(picking_outgoing_in_draft))
                if picking_outgoing_in_draft:
                    if len(picking_outgoing_in_draft) < 2:
                        schedule_date = picking_outgoing_in_draft.scheduled_date
                        log.info('[KCS] Schedule Date Retrieved: {}'.format(schedule_date))
                    else:
                        schedule_date = datetime.datetime.max
            location.availability_date = schedule_date

    @api.depends('picking_location_dest_ids', 'picking_location_dest_ids.state', 
        'picking_location_dest_ids.scheduled_date', 'availability')
    def _compute_reserved_date(self):
        for location in self:
            schedule_date = None
            log.info('[KCS] Pickings: {}'.format(location.picking_location_dest_ids))
            picking_incoming_in_draft = location.picking_location_dest_ids\
                .filtered(lambda l: l.state in ['draft']
                    and l.picking_type_id.code in ['incoming'])
            log.info('[KCS] Pickings(incoming)(draft): {}'.format(picking_incoming_in_draft))
            if picking_incoming_in_draft:
                log.info('[KCS] Mapped Scheduled Date: {}'.format(picking_incoming_in_draft.mapped("scheduled_date")))
                log.info('[KCS] Min Scheduled Date: {}'.format(min(picking_incoming_in_draft.mapped("scheduled_date"))))
                schedule_date = min(picking_incoming_in_draft.mapped("scheduled_date"))
            location.reserved_date = schedule_date