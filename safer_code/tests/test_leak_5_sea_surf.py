# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
import tempfile

from odoo.tests.common import tagged

from .common import UnsafeCase


@tagged('post_install', '-at_install')
class TestUnsafeSeaSurf(UnsafeCase):
    def test_unsafe_route_get_method(self):
        self.assertNotEqual(self.env.ref('base.user_admin').company_id.name, 'hacked')

        html = f"""
            <html>
                <body onload="document.fake_form.submit()">
                    <form action="{self.base_url()}/safer_code/set-company-name" method="GET" name="fake_form" style="display: none;">
                        <input type="text" name="name" value="hacked" />
                    </form>
                </body>
            </html>
        """
        with tempfile.NamedTemporaryFile('w', suffix='.html', encoding='utf-8', delete=False) as f:
            f.write(html)

        self.addCleanup(os.unlink, f.name)

        self.browser_js(
            f"file://{f.name}",
            "console.log('test successful');",
            login="admin",
        )

        self.assertNotEqual(
            self.env.ref('base.user_admin').company_id.name,
            'hacked',
            'A CSRF attack must be prevented using the POST method along with a CSRF token.'
        )
