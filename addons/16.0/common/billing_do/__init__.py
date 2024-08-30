# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID

import logging

def _update_account_tax_tax_type(cr):
    cr.execute('UPDATE account_tax SET tax_type = \'ITBIS\' WHERE id = 3;')
    cr.execute('UPDATE account_tax SET tax_type = \'ITBIS\' WHERE id = 16;')
    cr.execute('UPDATE account_tax SET tax_type = \'ITBIS\' WHERE id = 15;')
    cr.execute('UPDATE account_tax SET tax_type = \'ITBIS\' WHERE id = 22;')
    cr.execute('UPDATE account_tax SET tax_type = \'ITBIS\' WHERE id = 23;')
    cr.execute('UPDATE account_tax SET tax_type = \'ITBIS\' WHERE id = 24;')
    cr.execute('UPDATE account_tax SET tax_type = \'ITBIS\' WHERE id = 25;')
    cr.execute('UPDATE account_tax SET tax_type = \'ITBIS\' WHERE id = 27;')
    cr.execute('UPDATE account_tax SET tax_type = \'Otro\' WHERE id = 5;')
    cr.execute('UPDATE account_tax SET tax_type = \'Otro\' WHERE id = 14;')
    logging.info('[KCS] [Billing DO] Post init hook: Updated the Tax Type to some Account Tax.')

def _update_account_account_withholding_type(cr):
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ISR-606\' WHERE id = 115;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ISR-606\' WHERE id = 117;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ISR-606\' WHERE id = 118;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ISR-606\' WHERE id = 116;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ISR-606\' WHERE id = 112;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ISR-606\' WHERE id = 113;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ISR-606\' WHERE id = 114;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ISR-607\' WHERE id = 39;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ITBIS-606\' WHERE id = 111;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ITBIS-606\' WHERE id = 108;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ITBIS-606\' WHERE id = 109;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ITBIS-606\' WHERE id = 107;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ITBIS-606\' WHERE id = 110;')
    cr.execute('UPDATE account_account SET withholding_tax_type = \'RET-ITBIS-607\' WHERE id = 38;')
    logging.info('[KCS] [Billing DO] Post init hook: Updated the Withholding type to some Accounts.')

def _activate_dop_currency(env):
    env['res.currency'].search([('name', 'in', ['USD'])])\
        .write({'active': True})
    logging.info('[KCS] [Billing DO] Post init hook: Activated the USD currency.')

def _update_parameters(cr):
    cr.execute('UPDATE ir_config_parameter SET value=\'https://acp-webapi-staging.azurewebsites.net/webapi\' WHERE key=\'billing_do.api_services_base_url\';')
    cr.execute('UPDATE ir_config_parameter SET value=\'taxcontributors\' WHERE key=\'billing_do.api_services_tax_contributors_endpoint\';')
    cr.execute('UPDATE ir_config_parameter SET value=\'taxreceiptsnumbers\' WHERE key=\'billing_do.api_services_tax_receipts_endpoint\';')
    cr.execute('UPDATE ir_config_parameter SET value=\'True\' WHERE key=\'billing_do.api_services_tax_contributors_switch\';')
    cr.execute('UPDATE ir_config_parameter SET value=\'currencyrates\' WHERE key=\'billing_do.api_services_currency_rates_endpoint\';')
    cr.execute('UPDATE ir_config_parameter SET value=\'citizens\' WHERE key=\'billing_do.api_services_citizens_endpoint\';')
    cr.execute('UPDATE ir_config_parameter SET value=\'True\' WHERE key=\'billing_do.api_services_currency_rates_switch\';')
    cr.execute('UPDATE ir_config_parameter SET value=\'True\' WHERE key=\'billing_do.api_services_tax_receipts_switch\';')

def _fire_load_currency_cron_job(env):
    env['billing.do.res.currency'].sudo().load_today_currency_rates()
    logging.info('[KCS] [Billing DO] Post init hook: Updated all the currencies with the current exchange rate.')

def _update_default_user_login_info(env):
    current_user = env['res.users'].search([('login', '=', 'admin')])
    env['res.partner'].search([('id', '=', current_user.partner_id.id)])\
        .write({'name': 'Henry Medina'})
    current_user.write({'login': 'hmedina@accounterprise.com'})
    logging.info('[KCS] [Billing DO] Post init hook: Admin user info updated.')

def _deactivate_ir_cron_digest_scheduler_action(env):
    cron_job = \
        env['ir.cron'].search([('id', 
                                '=', 
                                env.ref('digest.ir_cron_digest_scheduler_action', 
                                    raise_if_not_found=False).id)])
    if not cron_job.try_write({'active': False}):
        logging.info('[KCS] [Billing DO] Post init hook: Cron job {} could not be deactivate.'\
            .format(cron_job.cron_name))
    else:
        logging.info('[KCS] [Billing DO] Post init hook: Cron job {} deactivated.'\
            .format(cron_job.cron_name))

def _billing_do_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_account_account_withholding_type(cr)
    _update_account_tax_tax_type(cr)
    _activate_dop_currency(env)
    _update_parameters(cr)
    _fire_load_currency_cron_job(env)
    _update_default_user_login_info(env)
    _deactivate_ir_cron_digest_scheduler_action(env)
