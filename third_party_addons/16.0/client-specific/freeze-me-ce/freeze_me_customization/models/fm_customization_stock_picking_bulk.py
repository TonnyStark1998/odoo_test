# -*- coding: utf-8 -*-

import logging

from odoo\
    import models, fields, api

class FreezeMeCustomizationStockPickingBulk(models.Model):
    _name = 'freeze.me.customization.stock.picking.bulk'
    _description = """
        Permite la creación de transferencias internas por lote según lo requerido por la empresa Freeze Me.
    """

    #############################################
    #            Default Methods                #
    #############################################

    def _default_name(self):
        stock_picking_bulk_sequence = self.env['ir.sequence']\
            .browse(self.env.ref('freeze_me_customization.sequence_stock_picking_bulk').id)
        return stock_picking_bulk_sequence.next_by_id()
    
    def _default_picking_type_id(self):
        return self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)

    #############################################
    #               Basic Fields                #
    #############################################

    name = fields.Char(string='Bulk Number',
        compute='_compute_name',
        readonly=False,
        index=True,
        store=True,
        tracking=True,
        default=_default_name)
    
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('generated', 'Generated')
        ], 
        string='State', 
        required=True, 
        readonly=True, 
        copy=False, 
        tracking=True,
        default='draft')
    
    stock_picking_ids = fields.One2many(string='Stock Pickings',
        comodel_name='stock.picking',
        inverse_name='stock_picking_bulk_id')
    
    stock_pickings_count = fields.Integer(string='Stock Pickings Count',
        compute='_compute_stock_pickings_count')

    partner_id = fields.Many2one(comodel_name='res.partner',
        string='Contact',
        states={'generated': [('readonly', True)]},
        required=True)

    scheduled_date = fields.Datetime(string='Scheduled Date',
        index=True,
        default=fields.Datetime.now,
        tracking=True,
        states={'generated': [('readonly', True)]},
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")
    
    picking_type_id = fields.Many2one(comodel_name='stock.picking.type',
        string='Operation Type', 
        readonly=True, 
        index=True,
        default=_default_picking_type_id)

    #############################################
    #            Compute Methods                #
    #############################################

    api.depends('state')
    def _compute_name(self):
        stock_picking_bulk_sequence = self.env['ir.sequence']\
            .browse(self.env.ref('freeze_me_customization.sequence_stock_picking_bulk').id)
        for stock_picking_bulk in self:
            logging.info('[KCS] Stock Picking Bulk Name: {}'.format(stock_picking_bulk.name))
            if stock_picking_bulk.state in ['generated']:
                continue
            if not stock_picking_bulk.id:
                stock_picking_bulk.name = \
                    stock_picking_bulk_sequence.get_next_char(stock_picking_bulk_sequence.number_next_actual)
                logging.info('[KCS] Sequence Next By ID: {}'.format(stock_picking_bulk.name))
            else:
                stock_picking_bulk.name = stock_picking_bulk_sequence.next_by_id()
                logging.info('[KCS] Sequence Next By ID: {}'.format(stock_picking_bulk.name))

    @api.depends('stock_picking_ids')
    def _compute_stock_pickings_count(self):
        for stock_picking_bulk in self:
            stock_picking_bulk.stock_pickings_count =\
                len(stock_picking_bulk.stock_picking_ids)
            
    #############################################
    #            onchange Methods               #
    #############################################

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.stock_picking_ids:
            for stock_picking_id in self.stock_picking_ids:
                stock_picking_id.partner_id = self.partner_id

    @api.onchange('scheduled_date')
    def _onchange_scheduled_date(self):
        if self.stock_picking_ids:
            for stock_picking_id in self.stock_picking_ids:
                stock_picking_id.scheduled_date = self.scheduled_date

    #############################################
    #             Actions Methods               #
    #############################################

    def action_freeze_me_customization_stock_picking_bulk_generate(self):
        self.ensure_one()
        self.write({'state': 'generated'})