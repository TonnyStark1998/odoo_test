# -*- coding: utf-8 -*-

from copy import copy
from email.policy import default
import logging as log
import datetime as date
from odoo \
    import models, \
            fields, \
            api, \
            exceptions, \
            _

class PatientFunctionalMedicineNutrition(models.Model):
    _name = 'kcs.medical.app.patient'
    _inherit = 'kcs.medical.app.patient'

    menstrual_period_last_date = fields.Date(string='Menstrual Period Last Date')
    menstrual_period_is_regular = fields.Selection(selection=[
                                        ('no', 'No'),
                                        ('yes', 'Yes')
                                    ],
                                    string='Is regular?', 
                                    copy=False)
    menstrual_period_needs_painkiller = fields.Selection(selection=[
                                                ('no', 'No'),
                                                ('yes', 'Yes')
                                            ],
                                            string='Needs painkiller?', 
                                            copy=False)
    menstrual_period_is_voluminous = fields.Selection(selection=[
                                            ('no', 'No'),
                                            ('yes', 'Yes')
                                        ],
                                        string='Is voluminous?', 
                                        copy=False)
 
    physical_activity = fields.Selection(selection=[
                                ('no', 'No'),
                                ('yes', 'Yes')
                            ],
                            string='Physical activities?', 
                            copy=False)
    physical_activity_which = fields.Selection(selection=[
                                ('cardio', 'Cardio'),
                                ('dumbbells', 'Dumbbells'),
                                ('crossfit', 'Crossfit'),
                                ('yoga_pilates', 'Yoga/Pilates'),
                                ('hit_boxing', 'Hit/Boxing'),
                                ('sports', 'Sports')
                                ], 
                            string='Which physical activities?')
    physical_activity_frequency = fields.Selection(selection=[
                                ('more_than_3_times_per_week', 'More than 3 times per week'),
                                ('less_than_3_time_per_week', 'Less than 3 times per week')
                                ], 
                            string='Physical activities frequency?')
    physical_activity_time = fields.Selection(selection=[
                                ('am', 'AM'),
                                ('pm', 'PM')
                                ], 
                            string='When do you do physical activities?')

    defecation_consistency = fields.Selection(selection=[
                                    ('constipation', 'Constipation'),
                                    ('diarrhea', 'Diarrhea'),
                                    ('normal', 'Normal')
                                ],
                            string='Defecation Consistency')
    defecation_see_food_residuals = fields.Selection(selection=[
                                        ('no', 'No'),
                                        ('yes', 'Yes')
                                    ],
                                    string='See Food Residuals?', 
                                    copy=False)

    sleep_range = fields.Selection(selection=[
                            ('8_to_10', '8 to 10'),
                            ('10_to_12', '10 to 12'),
                            ('after_12', 'After 12'),
                        ],
                    string='Sleep Average Range')
    sleep_hours_amount = fields.Selection(selection=[
                                    ('less_than_6', 'Less than 6 hours'),
                                    ('between_6_and_8', 'Between 6 and 8 hours'),
                                    ('more_than_8', 'More than 8 hours'),
                                ],
                            string='How many hours do you sleep?')
    sleep_wake_up_tired = fields.Selection(selection=[
                                        ('no', 'No'),
                                        ('yes', 'Yes')
                                    ],
                                    string='Do you wake up tired?', 
                                    copy=False)
    sleep_insomnia = fields.Selection(selection=[
                                        ('no', 'No'),
                                        ('yes', 'Yes')
                                    ],
                                    string='Suffer insomnia?', 
                                    copy=False)
    sleep_insomnia_type = fields.Selection(selection=[
                                    ('conciliatory', 'Conciliatory'),
                                    ('of_maintenance', 'Of maintenance'),
                                ],
                            string='Insomnia Type')

    water_consumption = fields.Selection(selection=[
                                    ('less_than_1_liter', 'Less than 1 liter'),
                                    ('between_1_and_2_liter', 'Between 1 and 2 liters'),
                                    ('more_than_2_liter', 'More than 2 liters'),
                                ],
                            string='How many liter of water do you consume per day?')

    foods_not_eat = fields.Text(string='List the food you dont eat')