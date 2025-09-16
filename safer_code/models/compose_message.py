# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MailComposer(models.Model):
    _name = "safer_code.compose.message"
    _description = 'Email composition wizard'

    subject = fields.Char('Subject', required=True)
    body = fields.Html('Contents', required=True)
    model = fields.Char('Related Document Model', required=True)
    res_id = fields.Integer('Related Document ID', required=True)
