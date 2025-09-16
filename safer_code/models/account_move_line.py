# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMoveLine(models.Model):
    _name = "safer_code.account.move.line"
    _description = "Journal Item"
    _order = 'name desc, id desc'

    name = fields.Char(string='Label')

    move_id = fields.Many2one(
        comodel_name='safer_code.account.move',
        string='Journal Entry',
        required=True,
        readonly=True,
        ondelete="cascade",
    )
