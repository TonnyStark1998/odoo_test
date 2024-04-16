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

    picking_ids = fields.One2many(string='Pickings',
        comodel_name='stock.picking',
        inverse_name='location_id')

    availability = fields.Selection(selection=[('ocupado', 'Ocupado'), 
            ('desocupado', 'Desocupado')],
        string='Availability',
        compute='_compute_availability',
        store=True)
    
    availability_date = fields.Date(string='Availability Date',
        compute='_compute_availability_date')
    
    reserved_date = fields.Date(string='Reserved Date',
        compute='_compute_availability_date')

    @api.depends('quant_ids')
    def _compute_availability(self):
        for location in self:
            if sum(location.quant_ids.mapped("quantity")) > 0:
                location.availability = 'ocupado'
            else:
                location.availability = 'desocupado'

    @api.depends('picking_ids')
    def _compute_availability_date(self):
        for location in self:
            picking_in_draft = location.picking_ids\
                .filtered(lambda l: l.state in ['draft'])
            log.info('[KCS] Pickings: {}'.format(picking_in_draft))
            if picking_in_draft:
                log.info('[KCS] Mapped Scheduled Date: {}'.format(picking_in_draft.mapped("scheduled_date")))
                log.info('[KCS] Min Scheduled Date: {}'.format(min(picking_in_draft.mapped("scheduled_date"))))
                location.reserved_date = location.availability_date = \
                    min(picking_in_draft.mapped("scheduled_date"))
            else:
                location.reserved_date = location.availability_date = datetime.datetime.now()