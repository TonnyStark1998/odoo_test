# -*- coding: utf-8 -*-
"""
Odoo Proprietary License v1.0.

see License:
https://www.odoo.com/documentation/user/14.0/legal/licenses/licenses.html#odoo-apps
# Copyright ©2022 Bernard K. Too<bernard.too@optima.co.ke>
"""
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

ROTATE = [(str(x), str(x) + "°") for x in range(0, 361)]
FONTSIZE = [(str(x), str(x)) for x in range(1, 160)]
OPACITY = [(str(round(x * 0.01, 2)), str(round(x * 0.01, 2))) for x in range(5, 105, 5)]


class TemplateSettings(models.Model):
    """A model to store report template settings and styles to be applied on
    reports."""

    _name = "report.template.settings"
    _description = "Report Style Settings"

    @api.model
    def _default_so_template(self):
        def_tpl = self.env["ir.ui.view"].search(
            [
                ("key", "like", "professional_templates.SO\_%\_document"),
                ("type", "=", "qweb"),
            ],
            order="key asc",
            limit=1,
        )
        return def_tpl or self.env.ref("sale.report_saleorder_document")

    @api.model
    def _default_po_template(self):
        def_tpl = self.env["ir.ui.view"].search(
            [
                ("key", "like", "professional_templates.PO\_%\_document"),
                ("type", "=", "qweb"),
            ],
            order="key asc",
            limit=1,
        )
        return def_tpl or self.env.ref("purchase.report_purchaseorder_document")

    @api.model
    def _default_rfq_template(self):
        def_tpl = self.env["ir.ui.view"].search(
            [
                ("key", "like", "professional_templates.RFQ\_%\_document"),
                ("type", "=", "qweb"),
            ],
            order="key asc",
            limit=1,
        )
        return def_tpl or self.env.ref("purchase.report_purchasequotation_document")

    @api.model
    def _default_dn_template(self):
        def_tpl = self.env["ir.ui.view"].search(
            [
                ("key", "like", "professional_templates.DN\_%\_document"),
                ("type", "=", "qweb"),
            ],
            order="key asc",
            limit=1,
        )
        return def_tpl or self.env.ref("stock.report_delivery_document")

    @api.model
    def _default_pk_template(self):
        def_tpl = self.env["ir.ui.view"].search(
            [
                ("key", "like", "professional_templates.PICK\_%\_document"),
                ("type", "=", "qweb"),
            ],
            order="key asc",
            limit=1,
        )
        return def_tpl or self.env.ref("stock.report_picking")

    @api.model
    def _default_payment_template(self):
        def_tpl = self.env["ir.ui.view"].search(
            [
                ("key", "like", "professional_templates.PAYMENT\_%\_document"),
                ("type", "=", "qweb"),
            ],
            order="key asc",
            limit=1,
        )
        return def_tpl or self.env.ref("stock.report_picking")

    @api.model
    def _default_inv_template(self):
        def_tpl = self.env["ir.ui.view"].search(
            [
                ("key", "like", "professional_templates.INVOICE\_%\_document"),
                ("type", "=", "qweb"),
            ],
            order="key asc",
            limit=1,
        )
        return def_tpl or self.env.ref("account.report_invoice_document_with_payments")

    name = fields.Char(
        "Name of Style", required=True, help="Give a unique name for this report style"
    )
    template_inv = fields.Many2one(
        "ir.ui.view",
        "Invoice Template",
        default=_default_inv_template,
        domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.INVOICE\_%\_document' )]",
        required=False,
    )
    template_so = fields.Many2one(
        "ir.ui.view",
        "Order/Quote Template",
        default=_default_so_template,
        domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.SO\_%\_document' )]",
        required=False,
    )

    template_po = fields.Many2one(
        "ir.ui.view",
        "Purchase Order Template",
        default=_default_po_template,
        domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.PO\_%\_document' )]",
        required=False,
    )

    template_rfq = fields.Many2one(
        "ir.ui.view",
        "RFQ Template",
        default=_default_rfq_template,
        domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.RFQ\_%\_document' )]",
        required=False,
    )

    template_dn = fields.Many2one(
        "ir.ui.view",
        "Delivery Note Template",
        default=_default_dn_template,
        domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.DN\_%\_document' )]",
        required=False,
    )

    template_pk = fields.Many2one(
        "ir.ui.view",
        "Picking Slip Template",
        default=_default_pk_template,
        domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.PICK\_%\_document' )]",
        required=False,
    )

    template_payment = fields.Many2one(
        "ir.ui.view",
        "Payment Receipt Template",
        default=_default_payment_template,
        domain="[('type', '=', 'qweb'), ('key', 'like','professional_templates.PAYMENT\_%\_document' )]",
        required=False,
    )

    logo = fields.Binary(
        "Header Logo",
        attachment=True,
        help="This field holds the image used as logo for the reports,\
                        if non is uploaded, the company logo will be used",
    )
    footer_logo = fields.Binary(
        "Footer Logo",
        attachment=True,
        help="This field holds the image used as footer logo for the reports,\
                        if non is uploaded and footer logo is enabled then the company logo will be used",
    )
    company_stamp = fields.Binary(
        "Company Stamp",
        attachment=True,
        help="This field holds the image used as the company stamp for the reports.\
            It is controlled by the 'Show Company Stamp' settings.",
    )
    odd = fields.Char(
        "Odd parity Color",
        size=7,
        required=True,
        default="#F2F2F2",
        help="The background color for Odd invoice lines in the invoice",
    )
    even = fields.Char(
        "Even parity Color",
        size=7,
        required=True,
        default="#FFFFFF",
        help="The background color for Even invoice lines in the invoice",
    )
    theme_color = fields.Char(
        "Theme Color",
        size=7,
        required=True,
        default="#F07C4D",
        help="The Main Theme color of the invoice. Normally this\
                        should be one of your official company colors",
    )
    text_color = fields.Char(
        "Text Color",
        size=7,
        required=True,
        default="#6B6C6C",
        help="The Text color of the invoice. Normally this should be one of your official \
                        company colors or default HTML text color",
    )
    name_color = fields.Char(
        "Company Name Color",
        size=7,
        required=True,
        default="#F07C4D",
        help="The Text color of the Company Name. Normally this should be one of your official\
                        company colors or default HTML text color",
    )
    cust_color = fields.Char(
        "Customer Name Color",
        size=7,
        required=True,
        default="#F07C4D",
        help="The Text color of the Customer Name. Normally this should be one of your official\
                        company colors or default HTML text color",
    )
    theme_txt_color = fields.Char(
        "Theme Text Color",
        size=7,
        required=True,
        default="#FFFFFF",
        help="The Text color of the areas bearing the theme color. Normally this should NOT\
                        be the same color as the theme color. Otherwise the text will not be visible",
    )

    header_font = fields.Selection(
        [(str(x), str(x)) for x in range(1, 51)],
        string="Header Font(px):",
        default="10",
        required=True,
    )
    body_font = fields.Selection(
        [(str(x), str(x)) for x in range(1, 51)],
        string="Body Font(px):",
        default="10",
        required=True,
    )
    footer_font = fields.Selection(
        [(str(x), str(x)) for x in range(1, 51)],
        string="Footer Font(px):",
        default="8",
        required=True,
    )
    font_family = fields.Char("Font Family:", default="sans-serif", required=True)
    aiw_report = fields.Boolean(
        "Enable amount in words",
        default=True,
        help="Check this box to enable the display of amount in words in the \
                        invoice/quote/sale order reports",
    )
    show_img = fields.Boolean(
        "Display product image",
        default=True,
        help="Check this box to display product image in Sales Order, Quotation, \
                        Invoice and Delivery Note",
    )
    show_footer_logo = fields.Boolean(
        "Enable footer logo",
        default=True,
        help="Check this box to display footer logo in the reports",
    )
    show_company_stamp = fields.Boolean(
        "Show Company Stamp",
        default=False,
        help="Check this box to display the Compny Stamp on Reports.",
    )
    transparent = fields.Boolean(
        "Background transparent",
        default=False,
        help="Check this box to have a transparent background for your reports. \n\
                        This is useful when the watermark feature is enabled so that your \
                        watermark is not hidden behind the report content/text",
    )
    footer = fields.Boolean(
        "Enable footer",
        default=True,
        help="Check this box to enable footer in your reports. \nYou may want to disable footer \
                        if you are using a watermark PDF with a footer content already",
    )
    header = fields.Boolean(
        "Enable header",
        default=True,
        help="Check this box to enable header in your reports. \nYou may want to disable header if\
                        you are using a watermark PDF with a header content already",
    )
    ############ Watermark Settings ################

    watermark = fields.Text(
        "Watermark Python Expression",
        default="""
# Please always ensure each line of the instructions below are always commented out with '#'
# If you want to have a watermark text printed on your PDF report, please create a simple python expression/code  that will be evaluated in
# order to generate a watermark text to be printed in the PDF report. Use the variables given below to write a simple line of code and store the value in 'watermark' variable
# EXAMPLE 1: `watermark = doc.name + ' ' + time.strftime('%Y-%m-%d %H:%M:%S')` => this example will print something like 'SO2017001 2017-07-26 01:07:42'
# EXAMPLE 2: `watermark = 'My Watermark Text'` => this example does not use the available variables. It simply prints the text your enter on the PDF Report asis
# Available variables:
#-------------------------------------------------
# env: the Odoo environment object.
# doc: object containing the current report being printed i.e Invoice, Order/Quote,PO/RFQ, Delivery Note or Picking Slip...e.g "doc.name" will print sales Order as watermark
# user: object containing the current login user.e.g "user.name" will print user's name as watermark
# time: reference to time from the Python standard library ..e.g "time.strftime('%Y-%m-%d %H:%M:%S')" will print current time as watermark like this: '2017-07-26 01:07:42'
# company: object containing the company of the login user..e.g "company.name" will print company name as watermark
# watermark: a string/text variable that will hold the watermark expression evaluated. Your watermark expression has to be set in the variable 'watermark'
#--------------------------------------------------
# IMPORTANT NOTE: Returned value have to be set in the variable 'watermark' as shown below.
watermark = doc.name
""",
        help="Put a python expression/code which when evaluated, will result in some \
        text to be printed on PDF as watermark.",
    )
    leftpadding = fields.Integer(
        "Distance from left (mm)",
        default=50,
        required=True,
        help="Text to start at 'x' distance from left margin of the PDF body",
    )
    toppadding = fields.Integer(
        "Distance from top (mm)",
        default=100,
        required=True,
        help="Text to start at 'y' distance from top margin of the PDF body",
    )
    wm_color = fields.Char(
        "Watermark color (Hex)",
        size=7,
        default="#5A5B5C",
        required=True,
        help="The watermark text color",
    )
    rotate = fields.Selection(
        ROTATE,
        string="Text Rotation (0°-360°):",
        required=True,
        default="0",
        help="Rotates the watermark text a given number of degrees counter clockwise\
                    around its centre",
    )
    opacity = fields.Selection(
        OPACITY,
        string="Opacity (0.05-1.0):",
        required=True,
        default="0.5",
        help="Sets the opacity of the watermark text. \nGive a number between 0.05 and 1.0 with \
                    1.0 being opaque and 0.05 being almost transparent",
    )
    fontsize = fields.Selection(
        FONTSIZE,
        string="Watermark font-size (px):",
        default="96",
        required=True,
        help="The font-size of the watermark text to be printed on PDF body",
    )

    def wm_eval(self, doc, time, user, company):
        """Method to be called from the template in order to evaluate the
        watermark expression and return a text to be printed on PDF."""
        localdict = dict(
            watermark=None, env=self.env, doc=doc, time=time, user=user, company=company
        )
        try:
            safe_eval(self.watermark, localdict, mode="exec", nocopy=True)
            return localdict["watermark"]
        except BaseException:
            msg = _("Invalid python expression defined for watermark: ")
            raise UserError(msg + "%s (%s)" % (self.name, self.watermark))
