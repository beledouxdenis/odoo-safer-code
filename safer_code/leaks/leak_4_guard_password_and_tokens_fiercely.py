# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


# https://github.com/odoo/odoo/commit/b2265108406e0dc1d1e1250fdbad5bc2cee2006d
class PaymentAcquirer(models.Model):
    """
        test: safer_code/tests/test_leak_4_guard_password_and_tokens_fiercely.py
        odoo-bin -d safer_db --test-tags .test_unsafe_token
    """
    _inherit = 'safer_code.payment.acquirer'

    ogone_userid = fields.Char(string="API User ID")
    ogone_password = fields.Char(string="API User Password")

    def ogone_get_api_url(self):
        self.ensure_one()
        return 'https://secure.ogone.com/ncol/prod/orderdirect_utf8.asp?user_id=%s' % self.ogone_userid
