# -*- coding: utf-8 -*-

from . import models
from . import controllers

import logging

def _update_default_website(cr):
    cr.execute('UPDATE website SET homepage_url = \'/stock/products/availability\';')
    logging.info('[KCS] [Billing DO] Post init hook: Update default website to add homepage URL.')

def _freeze_me_post_init(cr, registry):
    _update_default_website(cr)