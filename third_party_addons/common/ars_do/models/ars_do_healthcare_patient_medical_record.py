# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import logging as log

class ArsDoHealthcareMedicalRecord(models.Model):
    _name = 'ars.do.healthcare.medical.record'
    _description = 'Model representing a Healthcare Medical Record.'
    _order = 'date asc'

    date = fields.Date(string='Date',
                        required=True)
    blood_pressure = fields.Char(string='Blood Pressure',
                                    compute='_compute_blood_pressure')
    blood_pressure_high = fields.Integer(string='Blood Pressure High',
                                            required=True)
    blood_pressure_low = fields.Integer(string='Blood Pressure Low',
                                            required=True)
    time = fields.Float(string='Time',
                                required=True)
    bfr = fields.Integer(string='BFR',
                            required=True,
                            size=3)
    weight_display_value = fields.Char(string='Weight',
                                        compute='_compute_weight_display_value')
    weight = fields.Integer(string='Weight',
                                required=True,
                                size=3)
    fdp = fields.Selection(selection=[('1_weekly', '1 weekly'), 
                                        ('2_weekly', '2 weekly'),
                                        ('3_weekly', '3 weekly')],
                            string='FDP',
                            required=True)
    fldrmvd = fields.Integer(string='Filter Number',
                                required=True,
                                size=3)
    heparin_display_value = fields.Char(string='Heparin',
                                        compute='_compute_heparin_display_value')
    heparin = fields.Integer(string='Heparin')
    saline = fields.Selection(selection=[('0_45', '0.45%'), 
                                            ('0_9', '0.9%')],
                                string='Saline')
    ufr = fields.Integer(string='UFR',
                                required=True,
                                size=3)
    temperature_display_value = fields.Char(string='Temperature',
                                            compute='_compute_temperature_display_value')
    temperature = fields.Integer(string='Temperature',
                                    required=True,
                                    size=2)
    ptm = fields.Float(string='PTM',
                        required=True,
                        digits=(2,1))
    channel = fields.Selection(selection=[('catheter', 'Catheter'), 
                                            ('fistula', 'Fistula')],
                                string='Channel',
                                required=True)
    ktv = fields.Float(string='KTV',
                        required=True,
                        digits=(3, 2))
    notes = fields.Text(string='Notes',
                            required=True)

    # Relational fields
    medicines = fields.Many2many(string='Medicines',
                                    comodel_name='product.product',
                                    relation='ars_do_healthcare_medical_records_medicines',
                                    domain=[('is_medicine', '=', True)],
                                    required=True)
    healthcare_patient = fields.Many2one(string='Patient',
                                            comodel_name='res.partner')

    # Compute methods
    @api.onchange('blood_pressure_high', 'blood_pressure_low')
    def _compute_blood_pressure(self):
        for record in self:
            record.blood_pressure = '{}/{} mmHg'.format(record.blood_pressure_high, 
                                                    record.blood_pressure_low)

    @api.onchange('weight')
    def _compute_weight_display_value(self):
        for record in self:
            if record.weight:
                record.weight_display_value = '{} kg'.format(record.weight)
            else:
                record.weight_display_value = ''

    @api.onchange('heparin')
    def _compute_heparin_display_value(self):
        for record in self:
            if record.heparin:
                record.heparin_display_value = '{} cc'.format(record.heparin)
            else:
                record.heparin_display_value = ''

    @api.onchange('temperature')
    def _compute_temperature_display_value(self):
        for record in self:
            if record.temperature:
                record.temperature_display_value = '{} °'.format(record.temperature)
            else:
                record.temperature_display_value = ''

    # Constrains methods
    @api.constrains('saline')
    def _constrain_saline(self):
        for record in self:
            if not record.saline:
                raise exceptions.ValidationError(_('You must specify a value for Saline field.'))
    
    @api.constrains('channel')
    def _constrain_channel(self):
        for record in self:
            if not record.channel:
                raise exceptions.ValidationError(_('You must specify a value for Channel field.'))

    @api.constrains('fdp')
    def _constrain_fdp(self):
        for record in self:
            if not record.fdp:
                raise exceptions.ValidationError(_('You must specify a value for PDF field.'))

    @api.constrains('blood_pressure_high', 'blood_pressure_low', 'time', 'bfr', 'weight', 'fldrmvd', 'heparin', 'ufr', 'temperature', 'ptm', 'ktv')
    def _constrain_value_greater_than_zero(self):
        field_name = False
        if self.blood_pressure_high <= 0:
            field_name = 'blood_pressure_high'
        if self.blood_pressure_high <= 0:
            field_name = 'blood_pressure_high'
        if self.time < 0:
            field_name = 'time'
        if self.bfr <= 0:
            field_name = 'BFR'
        if self.weight <= 0:
            field_name = 'Weight'
        if self.fldrmvd <= 0:
            field_name = 'FLDRMVD'
        if self.heparin <= 0:
            field_name = 'Heparin'
        if self.ufr <= 0:
            field_name = 'UFR'
        if self.temperature <= 0:
            field_name = 'Temperature'
        if self.ptm <= 0:
            field_name = 'PTM'
        if self.ktv <= 0:
            field_name = 'KTV'
        
        if field_name:
            raise exceptions.UserError(_('Field {} can\'t have a value equal or below to 0.'.format(field_name)))