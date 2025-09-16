# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class HrPaylsip(models.Model):
    _name = 'safer_code.hr.payslip'
    _description = 'Pay Slip'

    name = fields.Char(string='Payslip Name', required=True)
