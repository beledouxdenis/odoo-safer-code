# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import users
from odoo.tools import mute_logger

from .common import UnsafeCase


class TestUnsafeAccessRights(UnsafeCase):
    @users('safer_code_portal')
    def test_unsafe_access_rights_channel_partner(self):
        # Create a random partner with an email to demonstrate we can extract any email from the database as portal
        foo_partner = self.env['res.partner'].sudo().create({'name': 'Foo', 'email': 'foo@foo.com'})

        # Create a public channel, as admin
        channel = self.env['safer_code.mail.channel'].sudo().create({'name': 'foo', 'public': 'public'})
        self.authenticate(self.env.user.login, self.env.user.login)

        # Create a first mail.channel.partner subscribing to a public channel,
        # with my own partner id for instance but could be any
        channel_partner_id = self.rpc('safer_code.mail.channel.partner', 'create', {
            'channel_id': channel.id, 'partner_id': self.env.user.partner_id.id
        })
        # Then, bruteforce each partner id to get their email address
        emails = []
        for i in range(foo_partner.id + 1):
            try:
                with mute_logger('odoo.sql_db'), mute_logger('odoo.http'):
                    self.rpc('safer_code.mail.channel.partner', 'write', [channel_partner_id], {
                        'partner_id': i,
                    }, raise_error=False)
            except Exception:  # noqa: BLE001
                # if this ID doesn't exist, just skip it
                continue
            email = self.rpc(
                'safer_code.mail.channel.partner', 'read', [channel_partner_id], ['partner_email']
            )[0]['partner_email']
            if email:
                emails.append(email)

        self.assertNotIn(
            'foo@foo.com',
            emails,
            "A portal user must not be able to obtain all the email addresses of a database",
        )

        admin_partner = self.env.ref('base.user_admin').sudo().partner_id
        self.rpc('safer_code.mail.channel.partner', 'write', [channel_partner_id], {
            'partner_id': admin_partner.id,
        })

        self.assertNotIn(
            admin_partner,
            channel.channel_partner_ids.partner_id,
            "A portal user must not be able to subscribe any partner to a channel",
        )
