# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo.tests.common import HttpCase

_logger = logging.getLogger(__name__)

HEADERS_JSON = {'Content-Type': 'application/json'}


class UnsafeCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_employee = cls.env['res.users'].create({
            'name': 'safer_code_employee',
            'login': 'safer_code_employee',
            'password': 'safer_code_employee',
            'group_ids': [
                # Employee
                cls.env.ref('base.group_user').id,
                # Contact creation
                cls.env.ref('base.group_partner_manager').id,
            ],
        })
        cls.user_portal = cls.env['res.users'].create({
            'name': 'safer_code_portal',
            'login': 'safer_code_portal',
            'password': 'safer_code_portal',
            'group_ids': [cls.env.ref('base.group_portal').id],
        })

    def rpc(self, model, method, *args, raise_error=True, **kwargs):
        response = self.url_open('/web/dataset/call_kw', headers=HEADERS_JSON, data=json.dumps({
            'params': {
                'model': model,
                'method': method,
                'args': args,
                'kwargs': kwargs
            }
        }))
        response = json.loads(response.content)
        if 'error' in response:
            if raise_error:
                _logger.error(response['error']['data']['debug'])
                str_args = ', '.join(map(str, args))
                str_kwargs = ', '.join(f'{key}={value}' for key, value in kwargs.items())
                raise Exception(f'Error while calling call_kw with {model}.{method}({str_args}, {str_kwargs})')
            else:
                return response
        return response.get("result")
