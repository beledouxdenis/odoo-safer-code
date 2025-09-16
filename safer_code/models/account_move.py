# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMove(models.Model):
    _name = 'safer_code.account.move'
    _description = "Journal Entry"
    _order = 'name desc, id desc'

    name = fields.Char(string='Number', required=True, copy=False)
    line_ids = fields.One2many(
        'safer_code.account.move.line',
        'move_id',
        string='Journal Items',
        copy=True,
        readonly=True,
    )
