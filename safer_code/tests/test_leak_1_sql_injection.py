# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import users
from odoo.tools import mute_logger

from .common import UnsafeCase


class TestSQLInjection(UnsafeCase):
    @users('safer_code_portal')
    def test_unsafe_cr_execute(self):
        emails = ['foo@foo.com', 'bar@bar.com', 'baz@baz.com', 'xyz@xyz.com']
        partners = self.env['res.partner'].sudo().create([{'name': email, 'email': email} for email in emails])
        # Blacklist the two first emails
        self.env['safer_code.blacklist'].sudo().create([{'email': email} for email in emails[:2]])

        self.authenticate(self.env.user.login, self.env.user.login)
        composer_id = self.rpc('safer_code.compose.message', 'create', {
            'subject': 'foo',
            'body': 'foo',
            'model': 'res.partner',
            'res_id': 1,
        })
        # 1. Ensure the feature works
        result = self.rpc('safer_code.compose.message', 'get_blacklist_records_ids', [composer_id], partners.ids)
        self.assertEqual(result, partners.ids[:2])

        # 2. Ensure it's not possible to do SQL injection
        try:
            with mute_logger('odoo.http'), mute_logger('odoo.sql_db'):
                result = self.rpc(
                    'safer_code.compose.message', 'get_blacklist_records_ids', [composer_id],
                    ["1);SELECT password FROM res_users--"],
                    raise_error=False,
                )
        except Exception:  # noqa: BLE001
            result = []
        self.assertFalse(
            any('sha512' in record for record in result if record),
            "A user must not be able to retrieve sensitive information thanks to an SQL injection"
        )

    @users('safer_code_portal')
    def test_unsafe_query_order(self):
        self.authenticate(self.env.user.login, self.env.user.login)

        move = self.env.ref('safer_code.move_foo')
        line_3_id, line_2_id, line_1_id = move.line_ids.ids

        # 1. Ensure the feature works
        result = self.rpc(
            'safer_code.account.move.line', 'search_read', [], ['name'],
            context={'matching_amount_aml_ids': [line_1_id, line_2_id]}
        )
        self.assertEqual([r['id'] for r in result], [line_2_id, line_1_id, line_3_id])

        # 2. Ensure it's not possible to do SQL injection
        try:
            with mute_logger('odoo.sql_db'), mute_logger('odoo.http'):
                self.rpc('safer_code.account.move.line', 'search_read', [], ['name'], context={
                    'matching_amount_aml_ids': [
                        "1);"
                        "UPDATE res_users SET login = 'foo', password = 'foo', active = 't' WHERE id = 2;"
                        "SELECT 1;--"
                    ]
                }, raise_error=False)
        except Exception:  # noqa: BLE001
            pass
        self.assertNotEqual(
            self.env.ref('base.user_admin').sudo().login,
            'foo',
            "A user must not be able to update the admin login and password thanks to an SQL injection")
