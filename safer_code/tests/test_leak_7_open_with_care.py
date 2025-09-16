# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError

from .common import UnsafeCase


class TestOpenWithCare(UnsafeCase):

    def test_open_with_care(self):
        server_action = self.env['ir.actions.server'].create({
            'name': 'foo',
            'model_id': self.env.ref('base.model_ir_actions_server').id,
            'state': 'code',
            'code': """
bundle = env['safer_code.ir.qweb'].get_asset_bundle(None, [
    {'atype': 'text/css', 'url': 'foo', 'filename': '/etc/passwd', 'content': 'foo', 'media': 'foo'},
])
asset = bundle.stylesheets[0]
raise UserError(asset._fetch_content())
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
            "A user of the SAAS must not be able to read arbitraty files on the server",
        )
