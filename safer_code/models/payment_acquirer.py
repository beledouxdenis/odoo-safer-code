# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PaymentAcquirer(models.Model):
    _name = 'safer_code.payment.acquirer'
    _description = 'Payment Acquirer'

    name = fields.Char(string="Name", required=True, translate=True)
