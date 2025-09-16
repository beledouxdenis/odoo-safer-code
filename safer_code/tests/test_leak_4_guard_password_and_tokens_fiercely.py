# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import users

from .common import UnsafeCase


class TestUnsafePasswordTokens(UnsafeCase):
    @users('safer_code_portal')
    def test_unsafe_token(self):
        # Create an Ogone acquirer for the sake of the test
        ogone_id = self.env['safer_code.payment.acquirer'].sudo().create({
            'name': 'Ogone',
            'ogone_userid': 'foo',
            'ogone_password': 'bar',
        }).id

        self.authenticate(self.env.user.login, self.env.user.login)
        api_url = self.rpc('safer_code.payment.acquirer', 'ogone_get_api_url', [ogone_id])
        self.assertTrue(api_url)
        result = self.rpc('safer_code.payment.acquirer', 'search_read', [], ['ogone_userid', 'ogone_password'])
        self.assertFalse(
            any(r.get('ogone_password') for r in result),
            "A portal user must not be able to read the payment provider API password",
        )
