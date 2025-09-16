# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ChannelPartner(models.Model):
    _name = 'safer_code.mail.channel.partner'
    _description = 'Listeners of a Channel'

    partner_id = fields.Many2one('res.partner', string='Recipient', ondelete='cascade', index=True)
    partner_email = fields.Char('Email', related='partner_id.email', readonly=False)
    channel_id = fields.Many2one('safer_code.mail.channel', string='Channel', ondelete='cascade', readonly=True, required=True)
