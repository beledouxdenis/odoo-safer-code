# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Channel(models.Model):
    _name = 'safer_code.mail.channel'
    _description = 'Discussion Channel'

    name = fields.Char('Name', required=True)
    public = fields.Selection(
        [
            ('public', 'Everyone'),
            ('private', 'Invited people only'),
            ('groups', 'Selected group of users')
        ],
        string='Privacy',
        required=True, default='groups',
        help='This group is visible by non members. Invisible groups can add members through the invite button.'
    )
    group_public_id = fields.Many2one(
        'res.groups', string='Authorized Group', default=lambda self: self.env.ref('base.group_user')
    )
    channel_partner_ids = fields.One2many(
        'safer_code.mail.channel.partner', 'channel_id', string='Channel Partners',
        groups='base.group_user')
