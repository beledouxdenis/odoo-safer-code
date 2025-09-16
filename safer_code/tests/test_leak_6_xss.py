# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import re
import uuid

from werkzeug.urls import url_encode

from odoo.tests.common import tagged, users

from .common import UnsafeCase


@tagged('post_install', '-at_install')
class TestUnsafeXSS(UnsafeCase):
    def get_js_code_add_admin(self):
        login = f"{str(uuid.uuid4())[:4]}@bar.com"
        body = json.dumps({
            'params': {
                'model': 'res.users',
                'method': 'create',
                'args': [{
                    'name': login,
                    'login': login,
                    'password': login,
                    'group_ids': [(6, 0, [self.env.ref('base.group_system').id])],
                }],
                'kwargs': {},
            }
        })
        js_code = """
            fetch(
                document.location.protocol + "//" + document.location.host + "/web/dataset/call_kw",
                {
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"},
                    "mode": "cors",
                    "credentials": "include",
                    "body": "%s",
                }
            );
        """ % body.replace('"', '\\"')
        return re.sub(r'\s+', '', js_code).strip()

    # https://github.com/odoo/odoo/commit/df1b22f23511ec82687d28a284ab8696fcd2aef4
    @users('safer_code_employee')
    def test_unsafe_stored_xss(self):
        # Ensure the current employee user doesn't have the settings group
        self.assertFalse(self.env.user._has_group('base.group_system'))

        # As an employee, create a partner with injected code.
        # The method to create the tag doesn't matter, as employee have the required access right to create/write a tag.

        injected_code = """
            <img
                src=x
                onerror='
                %s
                "--- oct0pus7 says hello! 🐙";
                '
            >
        """ % self.get_js_code_add_admin()
        partner = self.env['res.partner'].create({'name': re.sub(r'\s+', ' ', injected_code).strip()})

        admin_count = self.env['res.users'].sudo().search_count([
            ('group_ids', 'in', self.env.ref('base.group_system').id),
        ])

        # Do a tour, as an admin,
        # selecting that tag and executing the code with the administrator account
        # without him knowing
        self.start_tour(f'/odoo/contacts/{partner.id}', 'test_unsafe_stored_xss', login='admin')

        # Check that after the tour, after the administrator selected the tag including XSS,
        # a new admin user has not been created
        self.assertEqual(
            self.env['res.users'].search_count([('group_ids', 'in', self.env.ref('base.group_system').id)]),
            admin_count,
            "An employee user must not be able to escalate access rights through an XSS",
        )

    # https://github.com/odoo/odoo/commit/270f3a23f602a8094f06522e8a48623b552f2917
    @users('safer_code_portal')
    def test_unsafe_reflected_xss_forum(self):
        # Forge a link with injected code in the URL params granting the settings access to a user
        query_string = url_encode({'forum_origin': 'javascript: %s' % self.get_js_code_add_admin()})
        url = f"/safer_code/profile/user/{self.env.user.id}?{query_string}"

        admin_count = self.env['res.users'].sudo().search_count([
            ('group_ids', 'in', self.env.ref('base.group_system').id),
        ])

        # Do a tour, as admin,
        # click the back button on a user profile, containing the injected code,
        # being executed with the administrator account without the administrator knowing
        self.start_tour(url, 'test_unsafe_reflected_xss_forum', login='admin')

        # Check that after the tour, after the administrator clicked on the "Back" link containing the XSS,
        # a new admin user has not been created
        self.assertEqual(
            self.env['res.users'].sudo().search_count([('group_ids', 'in', self.env.ref('base.group_system').id)]),
            admin_count,
            "A portal user must not be able to escalate access rights through an XSS",
        )
