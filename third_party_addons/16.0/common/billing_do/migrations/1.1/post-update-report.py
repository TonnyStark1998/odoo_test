from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    line_to_update = env.ref("billing_do.kpi_bs_CURR_YEAR_EARNINGS")
    line_to_update.write({"expression": "-bale[('account_type', 'in', ('income', 'income_other'))][] - bale[('account_type', 'in', ('expense_direct_cost', 'expense', 'expense_depreciation'))][]"})
    subreport_to_unlink = env.ref("billing_do.report_balance_sheet_subreport_pl", False)
    if subreport_to_unlink:
        subreport_to_unlink.unlink()