from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID


class FormController(http.Controller):
    @http.route('/crm/customer/form', type='http', auth='public')
    def crm_form(self, **kw):
        countries = request.env['res.country'].search([], order='name')
        country_list = [{'id': country.id, 'name': country.name} for country in countries]
        mediums = request.env['utm.medium'].search([], order='name')
        medium_list = [{'id': medium.id, 'name': medium.name} for medium in mediums]

        return request.render("crm_customer_web_form.crm_customer_form", {
            'countries': country_list,
            'mediums': medium_list,
        })

    @http.route('/send/form', type='http', auth='public', methods=['POST'], csrf=False)
    def save_data_customer(self, **kwargs):
        try:
            ir_mail_server = request.env['ir.mail_server']
            mail_template = request.env['mail.template']

            mail_server = ir_mail_server.search([], limit=1)

            if not mail_server:
                raise ValueError("No configured mail server found.")

            template_ref = request.env.ref('crm.mail_template_demo_crm_lead', raise_if_not_found=False)
            if not template_ref:
                raise ValueError("Email template reference not found.")

            template_id = template_ref.id
            template = mail_template.browse(template_id)
            if not template.exists():
                raise ValueError(f"Email template with ID {template_id} not found.")

            values = template.generate_email(
                SUPERUSER_ID,
                ['subject', 'body_html', 'email_from', 'email_to', 'partner_to',
                 'email_cc', 'reply_to', 'scheduled_date', 'attachment_ids']
            )
            values['author_id'] = request.env.user.id
            values['res_id'] = request.env.user.partner_id.id

            msg_id = request.env['mail.mail'].sudo().create({
                'subject': values['subject'],
                'email_from': mail_server.smtp_user,
                'author_id': values['author_id'],
                'email_to': 'info@salutteclinic.do',
                'body_html': values['body_html'],
            })

            if msg_id:
                msg_id.sudo().send()
                request.env['crm.lead'].create_lead_from_json(kwargs)
            return "Emails sent successfully"

        except Exception as e:
            return str(e)
