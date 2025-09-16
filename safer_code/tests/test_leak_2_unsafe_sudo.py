# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import uuid

from lxml import html

from odoo.tests.common import users
from odoo.tools import mute_logger

from .common import HEADERS_JSON, UnsafeCase


class TestUnsafeSudo(UnsafeCase):

    @users('safer_code_portal')
    def test_unsafe_sudo_route_me(self):
        self.authenticate(self.env.user.login, self.env.user.login)
        response = self.url_open('/me')
        dom = html.fromstring(response.content)
        csrf_token = dom.xpath('//input[@name="csrf_token"]')[0].get('value')
        ref = str(uuid.uuid4())
        self.url_open('/me', data={'ref': ref, 'csrf_token': csrf_token})
        self.assertNotEqual(
            self.env.user.partner_id.ref,
            ref,
            "A portal user must not be able to set arbitrary fields of his partner",
        )

    @users('safer_code_portal')
    def test_unsafe_sudo_domain_injection(self):
        # For the test purpose, post a message containing a password on another user/partner
        user_admin = self.env.ref('base.user_admin')
        user_admin.with_user(user_admin).partner_id.message_post(body='Here is your password: passwd123')

        self.authenticate(self.env.user.login, self.env.user.login)
        with mute_logger('odoo.http'):
            response = self.url_open('/my-last-messages', headers=HEADERS_JSON, data=json.dumps({
                'params': {
                    'domain': ['|', ('body', 'ilike', 'password'), '&'],
                }
            })).json()
        self.assertTrue(
            not response.get('result') or not any('passwd123' in message.get('body') for message in response['result']),
            "A portal user must not be able to inject an arbitrary domain to obtain sensitive information",
        )

    @users('safer_code_portal')
    def test_unsafe_sudo_writable_whitelist(self):
        # For the test purpose, create a project with the portal user as collaborator,
        # and a task belonging to that project
        user_admin = self.env.ref('base.user_admin').sudo()
        project = self.env['safer_code.project'].with_user(user_admin).create({
            'name': 'foo',
            'collaborator_ids': [self.user_portal.id],
        })
        task = self.env['safer_code.task'].with_user(user_admin).create({
            'project_id': project.id,
            'name': 'foo',
            'description': 'bar',
        })

        hacker_email = 'foo@bar.com'
        # Sanity assert, that the email of the admin is not already the email of the hacker
        self.assertNotEqual(user_admin.email, hacker_email)

        self.authenticate(self.env.user.login, self.env.user.login)
        self.rpc('safer_code.task', 'write', [task.id], {
            'partner_id': user_admin.partner_id.id,
            'partner_email': hacker_email,
        }, raise_error=False)
        self.assertNotEqual(
            user_admin.email,
            hacker_email,
            "A portal user must not be able to change the email address of the admin user",
        )

    @users('safer_code_employee')
    def test_unsafe_related_sudo(self):
        # Create an attachment any employee is not supposed to read
        forbidden_data = b"This data is restricted to admins"
        update_notification_cron = self.env.ref('mail.ir_cron_module_update_notification')
        attachment = self.env['ir.attachment'].sudo().create({
            'name': 'foo',
            'res_model': update_notification_cron._name,
            'res_id': update_notification_cron.id,
            'datas': base64.b64encode(forbidden_data),
        })

        self.authenticate(self.env.user.login, self.env.user.login)

        # Check accessing the attachment data directly is forbidden
        with mute_logger('odoo.http'):
            response = self.rpc('ir.attachment', 'read', [attachment.id], ['datas'], raise_error=False)
        self.assertEqual(response.get('error', {}).get('data', {}).get('name'), 'odoo.exceptions.AccessError')

        try:
            with mute_logger('odoo.http'):
                # Check accessing the attachment data through the related `sign.template.datas` is forbidden
                template_id = self.rpc('safer_code.sign.template', 'create', {
                    'attachment_id': attachment.id,
                }, raise_error=False)
                [result] = self.rpc('safer_code.sign.template', 'read', [template_id], ['datas'], raise_error=False)
        except Exception:  # noqa: BLE001
            result = {'datas': b''}
        self.assertNotEqual(
            base64.b64decode(result['datas']), forbidden_data,
            "Any employee must not be able to access any attachment datas through a related to `attachment_id.datas`",
        )
