# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MailBlackList(models.Model):
    """ Model of blacklisted email addresses to stop sending emails."""
    _name = 'safer_code.blacklist'
    _description = 'Mail Blacklist'
    _rec_name = 'email'

    email = fields.Char(string='Email Address', required=True)
