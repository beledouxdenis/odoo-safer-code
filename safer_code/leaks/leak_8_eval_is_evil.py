# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Examples of fixes: https://github.com/odoo/odoo/commit/8d745f9f50d705007e3c3853f4af504624ad3c00

from odoo import models


class AccountMove(models.Model):
    _inherit = 'safer_code.account.move'

    def _get_invoice_action(self, invoice_ids):
        xml_id = 'account_action_invoice_out_refund'
        result = self.env.ref('safer_code.%s' % (xml_id)).read()[0]
        invoice_domain = eval(result['domain'])
        invoice_domain.append(('id', 'in', invoice_ids))
        result['domain'] = invoice_domain
        return result
