# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT section below).
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
#########COPYRIGHT#####
# © 2017 Bernard K Too<bernard.too@optima.co.ke>
from num2words import num2words

from odoo import _, api, fields, models


class PO(models.Model):
    _inherit = ["purchase.order"]

    @api.onchange('partner_id')
    def onchange_partner_style(self):
        self.po_style = self.partner_id.style or self.env.user.company_id.df_style or self.env.ref(
            'professional_templates.df_style_for_all_reports').id
        self.rfq_style = self.partner_id.style or self.env.user.company_id.df_style or self.env.ref(
            'professional_templates.df_style_for_all_reports').id

    po_style = fields.Many2one(
                                string='PO Style',
                                related='company_id.df_style',
                                help="Select Style to use when printing the PO",
                                # default=lambda self: self.env.company.df_style
                                #                        or self.partner_id.style 
                                #                        or self.env.user.company_id.df_style,
                                readonly=True
    )

    amount_words = fields.Char(
        'Amount in Words:',
        help=
        "The total amount in words is automatically generated by the system..few languages are supported currently",
        compute='_compute_num2words')

    def _compute_num2words(self):
        for rec in self:
            style = rec.po_style or rec.partner_id.style or rec.env.user.company_id.df_style or rec.env.ref(
                'professional_templates.df_style_for_all_reports')
            if style and style.aiw_report:
                try:
                    rec.amount_words = (
                        num2words(rec.amount_total, lang=rec.partner_id.lang or
                            'en') +
                        ' ' + (rec.currency_id.currency_name or '')).upper()
                except NotImplementedError:
                    rec.amount_words = (
                        num2words(rec.amount_total, lang='en') + ' ' +
                        (rec.currency_id.currency_name or '')).upper()
            else:
                rec.amount_words = _('Disabled')
