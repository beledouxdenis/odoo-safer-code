# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SignTemplate(models.Model):
    _name = "safer_code.sign.template"
    _description = "Signature Template"

    name = fields.Char('Name')
