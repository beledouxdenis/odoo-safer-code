# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError

from .common import UnsafeCase


class TestUnsafeGettAttrSetAttr(UnsafeCase):

    def test_unsafe_setattr(self):
        # Cleanup: as the server action will patch `ir.attachment`.`_full_path`, we need to reset it after test.
        # Otherwise `_full_path` will remain the hack patched method.
        self.addCleanup(
            setattr, self.env.registry['ir.attachment'], '_full_path', self.env.registry['ir.attachment']._full_path
        )

        server_action = self.env['ir.actions.server'].create({
            'name': 'foo',
            'model_id': self.env.ref('base.model_ir_actions_server').id,
            'state': 'code',
            'code': """
try:
    env['ir.attachment']._field_add('_full_path', lambda self, path: path)
except Exception:
    pass
result = env['ir.attachment']._file_read('/etc/passwd')
raise UserError(result)
        """
        })
        try:
            server_action.run()
        except UserError as e:
            [result] = e.args
        else:
            result = False
        self.assertEqual(
            result,
            "",
            "A user of the SAAS must not be able to read arbitraty files of the SAAS server",
        )

    def test_unsafe_getattr(self):
        server_action = self.env['ir.actions.server'].create({
            'name': 'foo',
            'model_id': self.env.ref('base.model_ir_actions_server').id,
            'state': 'code',
            'code': """
self = env['res.partner']
kls = self._get_field('__class__')
_import = kls._get_field(self.create, '__globals__')['__builtins__']['__import__']
os = _import('os')
result = os.popen('cat /etc/passwd').read()
raise UserError(result)
        """
        })
        try:
            server_action.run()
        except UserError as e:
            [result] = e.args
        else:
            result = False
        self.assertEqual(
            result,
            "",
            "A user of the SAAS must not be able to execute arbitraty commands on the server",
        )
