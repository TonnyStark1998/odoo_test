# -*- coding: utf-8 -*-

import logging as log
import datetime as date
from odoo \
    import models, \
            fields, \
            api, \
            exceptions, \
            _

class Patient(models.Model):
    _name = 'kcs.medical.app.patient'
    _inherits = {
        'res.partner': 'partner_id'
    }
    _description = "Patient model for capturing and retrieving the information for each one."
    
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True, ondelete='restrict')

    # Account Move - SQL Constraints
    # _sql_constraints = [
    #    ('national_identity_number',
    #     'UNIQUE(national_identity_number)',
    #     "El número de identificación digitado ya se encuentra registrado."),
    #]

    # Patient - Status Fields
    state = fields.Selection(selection=[
                                ('draft', 'Draft'),
                                ('registered', 'Registered'),
                                ('evolutioned', 'Evolutioned')
                            ], string='State', required=True, readonly=True, copy=False, tracking=True,
                            default='draft')
    
    # Patient - Personal Information Fields
    national_identity_number = fields.Char(string='Identity Number', 
                                            copy=False, 
                                            index=True, 
                                            required=True)

    genre = fields.Selection(selection=[
                                ('female', 'Female'),
                                ('male', 'Male'),
                                ('other', 'Other')
                            ], string='Genre', store=True)
    birthdate = fields.Date(string='Birthdate', store=True)
    age = fields.Integer(string='Age', readonly=True, compute='_compute_age', store=True, Tracking=True)
    phone_international = fields.Char(string='Phone International', copy=False, store=True)
    image_profile = fields.Image(string='Image Profile', max_width=200, max_height=200, attachment=True, copy=False, store=True)

    stetic_medicine_patient_images = fields.Many2many('ir.attachment', 
                                                        string="Stetic Medicine - Patient Images")
    plastic_surgery_process_1_patient_images = fields.Many2many(comodel_name='ir.attachment', 
                                                                string='Plastic Surgery - Process 1 - Patient Images',
                                                                relation='kma_plastic_surgery_process_1_patient_images')
    plastic_surgery_process_2_patient_images = fields.Many2many(comodel_name='ir.attachment', 
                                                                string='Plastic Surgery - Process 2 - Patient Images',
                                                                relation='kma_plastic_surgery_process_2_patient_images')
    plastic_surgery_process_3_patient_images = fields.Many2many(comodel_name='ir.attachment', 
                                                                string='Plastic Surgery - Process 3 - Patient Images',
                                                                relation='kma_plastic_surgery_process_3_patient_images')
    plastic_surgery_process_4_patient_images = fields.Many2many(comodel_name='ir.attachment', 
                                                                string='Plastic Surgery - Process 4 - Patient Images',
                                                                relation='kma_plastic_surgery_process_4_patient_images')
    dermatology_patient_images = fields.Many2many('ir.attachment', 
                                                    string="Dermatology - Patient Images",
                                                    relation="kma_dermatology_patient_images")

    # Patient - Miscelaneous Information Fields
    blood_type_id = fields.Many2one('kcs.medical.app.patient.bloodtype', string='Blood Type',  ondelete='restrict')
    recommended_by = fields.Char(string='Recommended By', copy=False, store=True)
    relative_name = fields.Char(string='Relative Name', copy=False, store=True)
    relative_phone = fields.Char(string='Relative Phone', copy=True, store=True)
    relative_relation = fields.Selection(selection=[
                                                ('grandparent', 'Grandparent'),
                                                ('friend', 'Friend'),
                                                ('roommate', 'Roommate'),
                                                ('wife', 'Wife'),
                                                ('husband', 'Husband'),
                                                ('sister', 'Sister'),
                                                ('brother', 'Brother'),
                                                ('daughter', 'Daughter'),
                                                ('son', 'Son'),
                                                ('mother', 'Mother'),
                                                ('grandchild', 'Grandchild'),
                                                ('father', 'Father'),
                                                ('other', 'Other'),
                                            ], 
                                            string='Relative Relation', 
                                            copy=False, 
                                            store=True)

    # Patient - Medical History
    disease_ids = fields.Many2many(string='Diseases or Medical Conditions', comodel_name='kcs.medical.app.patient.disease', relation='patients_diseases', copy=False)
    virus_ids = fields.Many2many(string='Viruses', comodel_name='kcs.medical.app.patient.virus', relation='patients_viruses', copy=False)
    medical_history_viruses_notes = fields.Text(string='Notes', copy=False, store=True)
    allergy_ids = fields.Many2many(string='Allergies', comodel_name='kcs.medical.app.patient.allergy', relation='patients_allergies', copy=False)
    medical_history_allergies_notes = fields.Text(string='Allergies Notes', copy=False, store=True)
    medicines_in_use = fields.Text(string='Medicine in use (Include contraceptives, vitamins, proteins, any supplement for weight losing)', copy=False, store=True)
    medical_history_notes = fields.Text(string='Notes', copy=False, store=True)

    # Patient - Birth History
    has_given_birth = fields.Boolean(string='Has given birth?', copy=False, store=True, default=False)
    count_given_birth = fields.Integer(string='Quantity', copy=False, store=True)
    last_date_given_birth = fields.Date(string='Last date has given birth', copy=True, store=True)
    has_given_birth_by_cesarean = fields.Boolean(string='Has given birth by cesarean?', copy=False, store=True, default=False)
    count_given_birth_by_cesarean = fields.Integer(string='Quantity', copy=False, store=True)
    last_date_given_birth_by_cesarean = fields.Date(string='Last date has given birth by cesarean', copy=True, store=True)
    has_aborted = fields.Boolean(string='Has aborted?', copy=False, store=True, default=False)
    count_aborted = fields.Integer(string='Quantity', copy=False, store=True)

    # Patient - Addiction Information
    drink_alcohol = fields.Boolean(string='Drink alcohol?', copy=False, store=True, default=False)
    drink_alcohol_frequency = fields.Boolean(string='More than 3 times per week', copy=False, store=True, default=False)
    smoke = fields.Boolean(string='Smoke?', copy=False, store=True, default=False)
    smoke_frequency = fields.Integer(string='How many cigarettes per day?', copy=False, store=True, default=0)
    smoke_since = fields.Integer(string='How many months have been smoking?', copy=False, store=True, default=0)

    smoked = fields.Boolean(string='Did you smoke?', copy=False, store=True, default=False)
    smoked_frequency = fields.Integer(string='How many cigarettes per day did you smoke?', copy=False, store=True, default=0)
    smoked_length = fields.Integer(string='For how long did you smoke?', copy=False, store=True, default=0)
    smoked_stopped_since = fields.Integer(string='How many months ago did you quit smoking?', copy=False, store=True, default=0)

    # Patient - Surgeries Information
    general_surgeries = fields.Text(string='General Surgeries', copy=False, store=True)
    stetic_surgeries = fields.Text(string='Stetic Surgeries', copy=False, store=True)

    # Patient - Family Medical History
    family_medical_history_father = fields.Text(string='Father Medical History', copy=False, store=True)
    family_medical_history_mother = fields.Text(string='Mother Medical History', copy=False, store=True)
    family_medical_history_siblings = fields.Text(string='Siblings Medical History', copy=False, store=True)
    family_medical_history_children = fields.Text(string='Children Medical History', copy=False, store=True)

    # Patient - Appointment Reason
    appointment_date = fields.Date(string='Appointment Date', copy=False, store=True)
    appointment_reason = fields.Text(string='Appointment Reason', copy=False, store=True)
    appointment_body_parts_ids = fields.Many2many(string='Body Parts', comodel_name='kcs.medical.app.patient.bodypart', relation='patients_bodyparts', copy=False)

    # Patient - Physical Exam
    heart_rate = fields.Integer(string='HR', copy=False, store=True)
    blood_pressure_low = fields.Integer(string='BPL', copy=False, store=True)
    blood_pressure_high = fields.Integer(string='BPH', copy=False, store=True)
    weight_measure = fields.Integer(string='WM', copy=False, store=True)
    height_measure_feet = fields.Integer(string='HM Feet', copy=False, store=True)
    height_measure_inches = fields.Integer(string='HM Inches', copy=False, store=True)
    imc_value = fields.Float(string='IMC', copy=False, store=True, digits=(5,2), compute='_compute_imc', default=0.00)
    so2_value = fields.Float(string='SO2',copy=False, store=False, digits=(3,2), default='')
    physical_exam_notes = fields.Text(string='Notes', copy=False, store=True)

    # Patient - Stetic Medicine
    evolution_ids_stetic_medicine = fields.One2many(string='Evolutions - Stetic Medicine', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=[('evolution_type', 'in', ['stetic_surgery'])])
    stetic_medicine_comment_medical = fields.Text(string='Stetic Medicine - Medical Comments', copy=False)
    stetic_medicine_comment_administrative = fields.Text(string='Stetic Medicine - Administrative Comments', copy=False)

    # Patient - Plastic Surgery
    ## Pre surgery
    evolution_ids_plastic_surgery_pre_surgery_process_1 = fields.One2many(string='Pre-surgery - Plastic Surgery - Process 1', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=['&', 
                                                                ('evolution_type', 'in', ['plastic_surgery']),
                                                            '&',
                                                                ('process_number', 'in', ['process_1']),
                                                                ('procedure_type', 'in', ['pre_surgery'])
                                                            ])
    evolution_ids_plastic_surgery_pre_surgery_process_2 = fields.One2many(string='Pre-surgery - Plastic Surgery - Process 2', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=['&', 
                                                                ('evolution_type', 'in', ['plastic_surgery']),
                                                            '&',
                                                                ('process_number', 'in', ['process_2']),
                                                                ('procedure_type', 'in', ['pre_surgery'])
                                                            ])
    evolution_ids_plastic_surgery_pre_surgery_process_3 = fields.One2many(string='Pre-surgery - Plastic Surgery - Process 3', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=['&', 
                                                                ('evolution_type', 'in', ['plastic_surgery']),
                                                            '&',
                                                                ('process_number', 'in', ['process_3']),
                                                                ('procedure_type', 'in', ['pre_surgery'])
                                                            ])
    evolution_ids_plastic_surgery_pre_surgery_process_4 = fields.One2many(string='Pre-surgery - Plastic Surgery - Process 4', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=['&', 
                                                                ('evolution_type', 'in', ['plastic_surgery']),
                                                            '&',
                                                                ('process_number', 'in', ['process_4']),
                                                                ('procedure_type', 'in', ['pre_surgery'])
                                                            ])

    ## Post surgery
    evolution_ids_plastic_surgery_post_surgery_process_1 = fields.One2many(string='Post-surgery - Plastic Surgery - Process 1', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=['&', 
                                                                ('evolution_type', 'in', ['plastic_surgery']),
                                                            '&',
                                                                ('process_number', 'in', ['process_1']),
                                                                ('procedure_type', 'in', ['post_surgery'])
                                                            ])
    evolution_ids_plastic_surgery_post_surgery_process_2 = fields.One2many(string='Post-surgery - Plastic Surgery - Process 2', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=['&', 
                                                                ('evolution_type', 'in', ['plastic_surgery']),
                                                            '&',
                                                                ('process_number', 'in', ['process_2']),
                                                                ('procedure_type', 'in', ['post_surgery'])
                                                            ])
    evolution_ids_plastic_surgery_post_surgery_process_3 = fields.One2many(string='Post-surgery - Plastic Surgery - Process 3', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=['&', 
                                                                ('evolution_type', 'in', ['plastic_surgery']),
                                                            '&',
                                                                ('process_number', 'in', ['process_3']),
                                                                ('procedure_type', 'in', ['post_surgery'])
                                                            ])
    evolution_ids_plastic_surgery_post_surgery_process_4 = fields.One2many(string='Post-surgery - Plastic Surgery - Process 4', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=['&', 
                                                                ('evolution_type', 'in', ['plastic_surgery']),
                                                            '&',
                                                                ('process_number', 'in', ['process_4']),
                                                                ('procedure_type', 'in', ['post_surgery'])
                                                            ])

    evolution_ids_plastic_surgery_procedure_ids_process_1 = fields.Many2many(string='Plastic Surgery - Process 1 - Evolution Procedures', 
                                                                    comodel_name='product.product', 
                                                                    relation='kma_patient_evolutions_procedures_process_1', 
                                                                    copy=False,
                                                                    domain=[
                                                                        ('sale_ok','=','True')
                                                                    ])
    evolution_ids_plastic_surgery_procedure_ids_process_2 = fields.Many2many(string='Plastic Surgery - Process 2 - Evolution Procedures', 
                                                                    comodel_name='product.product', 
                                                                    relation='kma_patient_evolutions_procedures_process_2', 
                                                                    copy=False,
                                                                    domain=[
                                                                        ('sale_ok','=','True')
                                                                    ])
    evolution_ids_plastic_surgery_procedure_ids_process_3 = fields.Many2many(string='Plastic Surgery - Process 3 - Evolution Procedures', 
                                                                    comodel_name='product.product', 
                                                                    relation='kma_patient_evolutions_procedures_process_3', 
                                                                    copy=False,
                                                                    domain=[
                                                                        ('sale_ok','=','True')
                                                                    ])
    evolution_ids_plastic_surgery_procedure_ids_process_4 = fields.Many2many(string='Plastic Surgery - Process 4 - Evolution Procedures', 
                                                                    comodel_name='product.product', 
                                                                    relation='kma_patient_evolutions_procedures_process_4', 
                                                                    copy=False,
                                                                    domain=[
                                                                        ('sale_ok','=','True')
                                                                    ])

    plastic_surgery_comment_medical = fields.Text(string='Plastic Surgery - Medical Comments', copy=False)
    plastic_surgery_comment_administrative = fields.Text(string='Plastic Surgery - Administrative Comments', copy=False)

    # Patient - Dermatology
    dermatology_evolution_ids = fields.One2many(string='Evolutions - Dermatology', 
                                                    comodel_name='kcs.medical.app.patient.evolution',
                                                    inverse_name='patient_id',
                                                    domain=[('evolution_type', 'in', ['dermatology'])])
    dermatology_comment_medical = fields.Text(string='Dermatology - Medical Comments', 
                                                    copy=False)
    dermatology_comment_administrative = fields.Text(string='Dermatology - Administrative Comments', 
                                                            copy=False)

    # Patient - Evolutions History
    evolution_history_ids = fields.One2many(string='Evolutions History', 
                                                    comodel_name='kcs.medical.app.patient.evolution.history',
                                                    inverse_name='patient_id')
    evolution_history_budget_procedures = fields.Char(string='Evolution History Procedures',
                                                        required=False,
                                                        readonly=True)
    evolution_history_budget_plastic_comments = fields.Char(string='Evolution History Plastic Comments',
                                                        required=False,
                                                        readonly=True)
    evolution_history_budget_stetic_comments = fields.Char(string='Evolution History Stetic Comments',
                                                        required=False,
                                                        readonly=True)

    # Patient - COVID Info
    has_tested_postitive_to_covid = \
        fields.Boolean(string='Has tested positive to COVID-19?', 
                        copy=False, 
                        store=True, 
                        default=False)
    has_been_in_hospital_for_covid = \
        fields.Boolean(string='Has been in the hospital for COVID-19?', 
                        copy=False, 
                        store=True, 
                        default=False)
    date_tested_positive_to_covid = \
        fields.Date(string='Which date did you test positive for COVID-19?', 
                        copy=False, 
                        store=True)

    channel_ids = fields.Many2many('mail.channel', 'mail_channel_patients', 'partner_id', 'channel_id', string='Channels', copy=False)

    # Patient - Compute Field's Functions
    @api.depends('stetic_medicine_budget_product_ids')
    def _compute_stetic_medicine_budget(self):
        for patient in self:
            if patient.stetic_medicine_budget_product_ids:
                budget = 0.0
                for product in patient.stetic_medicine_budget_product_ids:
                    budget += product.list_price
                self.stetic_medicine_budget_total = budget
    
    @api.depends('plastic_surgery_budget_product_ids')
    def _compute_plastic_surgery_budget(self):
        for patient in self:
            budget = 0.0
            if patient.plastic_surgery_budget_product_ids:
                for product in patient.plastic_surgery_budget_product_ids:
                    budget += product.list_price
            self.plastic_surgery_budget_total = budget

    @api.depends('birthdate', 'age')
    def _compute_age(self):
        age = 0
        for patient in self:
            if patient.birthdate:
                today = date.date.today()
                age = today.year - patient.birthdate.year
                if age > 0:
                    if int(patient.birthdate.month) > int(today.month):
                        age = age - 1
                    elif int(patient.birthdate.month) == int(today.month) and int(patient.birthdate.day) > int(today.day):
                        age = age - 1
            patient.age = age
    
    @api.depends('weight_measure', 'height_measure_feet', 'height_measure_inches')
    def _compute_imc(self):
        imc = 0.00
        for patient in self:
            if patient.weight_measure > 0 and patient.height_measure_feet > 0 and patient.height_measure_inches > 0:
                height = (patient.height_measure_feet * 12) + patient.height_measure_inches
                imc = (patient.weight_measure / (height**2)) * 703
            patient.imc_value = imc

    # Patient - OnChange Field's Functions
    @api.onchange('national_identity_number')
    def _onchange_national_identity_number(self):
        _reset_fields = False
        if self.national_identity_number:
            patient = self.env['kcs.medical.app.patient'].search(args=[('national_identity_number', '=', self.national_identity_number)], limit=1)
            if patient:
                self = patient
                return {
                    'warning': {
                        'title': "Paciente registrado",
                        'message': "La cédula digitada ({0}) pertenece a un paciente ya registrado.".format(patient.national_identity_number)
                    }
                }
            self.partner_id = self.env['res.partner'].search(args=[('vat', '=', self.national_identity_number)], limit=1).id
            if not self.partner_id:
                _reset_fields = True
        else:
            _reset_fields = True
        
        if _reset_fields:
            self._reset_fields()

    @api.onchange('so2_value')
    def _onchange_so2_value(self):
        if self.so2_value:
            if not self._validate_value_range(self.so2_value, 0, 100):
                return {
                    'warning': {
                        'title': "Campo con valor erróneo",
                        'message': "El valor del campo SO2 (Saturación en oxígeno) debe estar en 0 y 100."
                    }
                }

    # Patient - Contraints Field's Functions
    @api.constrains('so2_value')
    def _check_so2_value(self):
        for patient in self:
            if patient.so2_value:
                if not self._validate_value_range(self.so2_value, 0, 100):
                    raise exceptions.UserError(_('The value for the SO2 field (Oxygen Saturation) must be between 0 and 100.'))

    @api.constrains('date_tested_positive_to_covid')
    def _check_date_tested_positive_to_covid(self):
        for patient in self:
            if patient.date_tested_positive_to_covid:
                log.info('[{0}] ({1}) = {2}'.format(patient.date_tested_positive_to_covid, date.date.today(), patient.date_tested_positive_to_covid > date.date.today()))
                if patient.date_tested_positive_to_covid > date.date.today():
                    raise exceptions.UserError(_('The date you tested positive ({0}) must be before the current date ({1}).')
                                                    .format(patient.date_tested_positive_to_covid.strftime('%d-%m-%Y'), 
                                                            date.date.today().strftime('%d-%m-%Y')))

    @api.model
    def create(self, values):
        partner = self.env['res.partner'].search(args=[('vat', '=', values['national_identity_number'])], limit=1)
        if not partner:
            values['partner_id'] = self.env['res.partner'].create({
                'type': 'contact',
                'name': values['name'],
                'display_name': values['name'],
                'vat': values['national_identity_number'],
                'phone': values['phone'],
                'mobile': values['mobile'],
                'email': values['email'],
                'street': values['street'],
                'street2': values['street2'],
                'city': values['city'],
                'country_id': values['country_id'],
                'function': values['function']
            }).id
        else:
            values['partner_id'] = partner.id
        values['tax_contributor_type'] = '3'
        values['state'] = 'registered'
        values['company_id'] = self.env.company.id
        return super(Patient, self).create(values)

    def add_new_evolution_stetic_medicine(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "kcs.medical.app.patient.evolution",
            "views": [[False, "form"]],
            "domain": [],
            "target": "new",
            "context": {
                "default_patient_id": self.id,
                "default_evolution_type": "stetic_surgery",
                "default_date_recorded": fields.Datetime.now()
            },
            "name": "Nuevo proceso"
        }
    
    def add_new_evolution_dermatology(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "kcs.medical.app.patient.evolution",
            "views": [[False, "form"]],
            "domain": [],
            "target": "new",
            "context": {
                "default_patient_id": self.id,
                "default_evolution_type": "dermatology",
                "default_date_recorded": fields.Datetime.now()
            },
            "name": "Nuevo proceso"
        }

    def add_new_evolution_plastic_surgery_pre_surgery_process_1(self):
        return self._add_new_evolution_plastic_surgery_pre_surgery('process_1')
    
    def add_new_evolution_plastic_surgery_pre_surgery_process_2(self):
        return self._add_new_evolution_plastic_surgery_pre_surgery('process_2')
    
    def add_new_evolution_plastic_surgery_pre_surgery_process_3(self):
        return self._add_new_evolution_plastic_surgery_pre_surgery('process_3')
    
    def add_new_evolution_plastic_surgery_pre_surgery_process_4(self):
        return self._add_new_evolution_plastic_surgery_pre_surgery('process_4')

    def add_new_evolution_plastic_surgery_post_surgery_process_1(self):
        return self._add_new_evolution_plastic_surgery_post_surgery('process_1')

    def add_new_evolution_plastic_surgery_post_surgery_process_2(self):
        return self._add_new_evolution_plastic_surgery_post_surgery('process_2')

    def add_new_evolution_plastic_surgery_post_surgery_process_3(self):
        return self._add_new_evolution_plastic_surgery_post_surgery('process_3')
        
    def add_new_evolution_plastic_surgery_post_surgery_process_4(self):
        return self._add_new_evolution_plastic_surgery_post_surgery('process_4')

    def _reset_fields(self):
        self.name = ''
        self.phone = ''
        self.mobile = ''
        self.email = ''
        self.street = ''
        self.street2 = ''
        self.zip = ''
        self.city = ''
        self.state_id = None
        self.country_id = None

    def _validate_value_range(self, value, lowerBound, upperBound):
        return value >= lowerBound and value <= upperBound

    def _add_new_evolution_plastic_surgery_pre_surgery(self, process_number):
        return self._add_new_evolution_plastic_surgery('pre_surgery', process_number)

    def _add_new_evolution_plastic_surgery_post_surgery(self, process_number):
        return self._add_new_evolution_plastic_surgery('post_surgery', process_number)

    def _add_new_evolution_plastic_surgery(self, procedure_type, process_number):
        return {
            "type": "ir.actions.act_window",
            "res_model": "kcs.medical.app.patient.evolution",
            "views": [[False, "form"]],
            "domain": [],
            "target": "new",
            "context": {
                "default_patient_id": self.id,
                "default_evolution_type": "plastic_surgery",
                "default_procedure_type": procedure_type,
                "default_process_number": process_number,
                "default_date_recorded": fields.Datetime.now()
            },
            "name": "Nueva pre operatorio" if procedure_type in ['pre_surgery'] else "Nueva post operatoria"
        }

class PatientEvolution(models.Model):
    _name = 'kcs.medical.app.patient.evolution'
    _description = 'Evolution model for capturing and retrieving the information about every evolution for a specific Patient'

    currency_id = fields.Many2one(string='Currency',
                                    comodel_name='res.currency')

    # Patient Evolution - Fields
    description = fields.Text(string='Description', copy=False, index=True)
    date_recorded = fields.Datetime(string='Recorded Date', readonly=True, required=True, store=True, copy=False)
    user_who_recorded_id = fields.Many2one('res.users', 
                                            string='User', 
                                            readonly=True, 
                                            required=True, 
                                            ondelete='restrict', 
                                            default=lambda self: self.env.user and self.env.user.id or False)
    patient_id = fields.Many2one('kcs.medical.app.patient', string='Patient', required=True, ondelete='restrict')
    evolution_type = fields.Selection(selection=[
                                            ('plastic_surgery', 'Plastic Surgery'),
                                            ('stetic_surgery', 'Stetic Surgery'),
                                            ('dermatology', 'Dermatology')
                                        ], 
                                        string='Evolution Type', 
                                        copy=False, 
                                        store=True, 
                                        required=True)
    procedure_type = fields.Selection(selection=[
                                            ('pre_surgery', 'Pre-Surgery'),
                                            ('post_surgery', 'Post-Surgery'),
                                        ], 
                                        string='Procedure Type', 
                                        copy=False, 
                                        store=True, 
                                        required=False,
                                        default='pre_surgery')
    process_number = fields.Selection(selection=[
                                        ('process_1', 'Process 1'),
                                        ('process_2', 'Process 2'),
                                        ('process_3', 'Process 3'),
                                        ('process_4', 'Process 4'),
                                    ],
                                    string='Process Number',
                                    copy=False)

    procedure_ids = fields.Many2many(string='Evolution Procedures', 
                                        comodel_name='product.product', 
                                        relation='kcs_medical_app_patient_evolutions_procedures', 
                                        copy=False,
                                        domain=[
                                            ('sale_ok','=','True')
                                        ])

    budget_product_ids = fields.Many2many(string='Products', 
                                            comodel_name='product.product', 
                                            relation='kcs_medical_app_patient_evolution_products',
                                            domain=[
                                                ('sale_ok', '=', 'True')
                                            ])

    doctor_notes = fields.Text(string='Doctor Notes', required=True, copy=False, store=True)

    next_date = fields.Integer(string='Next Date (Days)',
                                copy=False)

    @api.model
    def create(self, values):
        patient_evolution = super(PatientEvolution, self).create(values)
        patient = self.env['kcs.medical.app.patient'].browse(patient_evolution.patient_id.id)
        # sale_order = self.env['sale.order'].create({
        #     "name" : "Cotizacion para: " + patient.name,
        #     "state" : "draft",
        #     "validity_date" : date.date.today() + date.timedelta(days=30),
        #     "partner_id" : patient.partner_id.id,
        #     "pricelist_id": self.env.company.partner_id.property_product_pricelist and self.env.company.partner_id.property_product_pricelist.id or False,
        # })

        # products_ids = []

        # if patient_evolution.budget_product_ids:
        #     products_ids += patient_evolution.budget_product_ids

        # if patient_evolution.procedure_ids:
        #     products_ids += patient_evolution.procedure_ids

        # if products_ids:
        #     for product in products_ids:
        #         self.env['sale.order.line'].create({
        #             "order_id" : sale_order.id,
        #             "name" : product.name,
        #             "product_id" : product.id,
        #         })

        if patient.state in ['registered']:
            patient.write({
                'state': 'evolutioned'
            })
        return patient_evolution

    @api.onchange('evolution_type')
    def _onchange_evolution_type(self):
        if self.evolution_type:
            products_domain = [
                ('sale_ok', '=', 'True'),
                ('patient_evolution_type','=',self.evolution_type)
            ]
            return {
                'domain': {
                    'procedure_ids': products_domain,
                    'budget_product_ids': products_domain,
                }
            }

class PatientEvolutionHistory(models.Model):
    _name = 'kcs.medical.app.patient.evolution.history'
    _description = 'Evolution histories model for displaying the evolutions migrated.'

    description = fields.Text(string='Description', required=True, copy=False)
    date_recorded = fields.Date(string='Recorded Date', readonly=True, copy=False)
    user_who_recorded = fields.Char(string='User Who Recorded')
    patient_id = fields.Many2one('kcs.medical.app.patient', string='Patient', required=True, ondelete='restrict')

class PatientBloodType(models.Model):
    _name = 'kcs.medical.app.patient.bloodtype'
    _description = 'This class represents a blood type for a patient.'

    # Account Move - SQL Constraints
    _sql_constraints = [
        ('name',
         'UNIQUE(name)',
         "El tipo de sangre debe ser único. Verifique el listado y valide que no existe el que digitó."),
    ]

    name = fields.Char(string='Blood Type', required=True, store=True, copy=False)
    active = fields.Boolean(string='Active', store=True, copy=True, default=True)
    patients = fields.One2many(string='Patients', comodel_name='kcs.medical.app.patient', inverse_name='blood_type_id')

class PatientDisease(models.Model):
    _name = 'kcs.medical.app.patient.disease'
    _description = 'This class represents a disease for a patient.'

    # Account Move - SQL Constraints
    _sql_constraints = [
        ('name',
         'UNIQUE(name)',
         "Las enfermedades deben ser únicas. Verifique el listado y valide que no existe la que digitó."),
    ]

    name = fields.Char(string='Disease', required=True, store=True, copy=False)
    active = fields.Boolean(string='Active', store=True, copy=True, default=True)
    patient_ids = fields.Many2many(string='Patients', comodel_name='kcs.medical.app.patient', relation='patients_diseases', copy=False)

class PatientVirus(models.Model):
    _name = 'kcs.medical.app.patient.virus'
    _description = 'This class represents a virus for a patient.'

    # Account Move - SQL Constraints
    _sql_constraints = [
        ('name',
         'UNIQUE(name)',
         "Los virus deben ser únicos. Verifique el listado y valide que no existe el que digitó."),
    ]

    name = fields.Char(string='Virus', required=True, store=True, copy=False)
    active = fields.Boolean(string='Active', store=True, copy=True, default=True)
    patient_ids = fields.Many2many(string='Patients', comodel_name='kcs.medical.app.patient', relation='patients_viruses', copy=False)

class PatientAllergy(models.Model):
    _name = 'kcs.medical.app.patient.allergy'
    _description = 'This class represents an allergy for a patient.'

    # Account Move - SQL Constraints
    _sql_constraints = [
        ('name',
         'UNIQUE(name)',
         "Las alergias deben ser únicas. Verifique el listado y valide que no existe la que digitó."),
    ]

    name = fields.Char(string='Allergy', required=True, store=True, copy=False)
    active = fields.Boolean(string='Active', store=True, copy=True, default=True)
    patient_ids = fields.Many2many(string='Patients', comodel_name='kcs.medical.app.patient', relation='patients_allergies', copy=False)

class PatientSteticContraindication(models.Model):
    _name = 'kcs.medical.app.patient.stetic.contraindication'
    _description = 'This class represents a contraindication for a patient about stetic medicine.'

    # Account Move - SQL Constraints
    _sql_constraints = [
        ('name',
         'UNIQUE(name)',
         "Las contraindicaciones deben ser únicas. Verifique el listado y valide no existe la que digitó."),
    ]

    name = fields.Char(string='Contraindication', required=True, store=True, copy=False)
    active = fields.Boolean(string='Active', store=True, copy=True, default=True)
    patient_ids = fields.Many2many(string='Patients', comodel_name='kcs.medical.app.patient', relation='patients_contraindications', copy=False)

class PatientSteticSkinType(models.Model):
    _name = 'kcs.medical.app.patient.stetic.skin.type'
    _description = 'This class represents a skin type for a patient about stetic medicine.'

    # Account Move - SQL Constraints
    _sql_constraints = [
        ('name',
         'UNIQUE(name)',
         "Los tipos de piel deben ser únicos. Verifique el listado y valide que no existe la que digitó."),
    ]

    name = fields.Char(string='Skin Type', required=True, store=True, copy=False)
    active = fields.Boolean(string='Active', store=True, copy=True, default=True)
    patient_ids = fields.Many2many(string='Patients', comodel_name='kcs.medical.app.patient', relation='patients_skin_type', copy=False)

class PatientBodyPart(models.Model):
    _name = 'kcs.medical.app.patient.bodypart'
    _description = 'This class represents a part of the body for a patient.'

    # Patient Body Part - SQL Constraints
    _sql_constraints = [
        ('name',
         'UNIQUE(name)',
         "Las partes del cuerpo deben ser únicas. Verifique el listado y valide que no existe la que digitó."),
    ]

    name = fields.Char(string='Body Part', required=True, store=True, copy=False)
    active = fields.Boolean(string='Active', store=True, copy=True, default=True)
    patient_ids = fields.Many2many(string='Patients', comodel_name='kcs.medical.app.patient', relation='patients_bodyparts', copy=False)