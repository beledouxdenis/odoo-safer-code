# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError

from .common import UnsafeCase


class TestEvalIsEvil(UnsafeCase):

    def test_eval_is_evil(self):
        server_action = self.env['ir.actions.server'].create({
            'name': 'foo',
            'model_id': self.env.ref('base.model_ir_actions_server').id,
            'state': 'code',
            'code': """
action = env.ref('safer_code.account_action_invoice_out_refund')
action.write({'domain': "[__import__('os').popen('cat /etc/passwd').read()]"})
# Could also be
# action.write({'domain': "[self.create.__globals__['__builtins__']['__import__']('os').popen('cat /etc/passwd').read()]"})
result = env['safer_code.account.move']._get_invoice_action([1, 2, 3])
raise UserError(result['domain'][0])
        """
        })
        try:
            server_action.run()
        except UserError as e:
            [result] = e.args
        else:
            result = ''
        self.assertNotIn(
            'root:x',
            result,
            "A user of the SAAS must not be able to execute arbitraty commands on the server",
        )
