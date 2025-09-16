# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class MailComposer(models.Model):
    _inherit = "safer_code.compose.message"

    # https://github.com/odoo/odoo/commit/2ff9b379ef80ba6a8744fb9702a8088284372ddd#diff-898a3d5c08a567c1a7b82c026a213d796e850e376cbdb1c9e7936409f440d37aL287
    def get_blacklist_records_ids(self, res_ids):
        """
        test: safer_code/tests/test_leak_1_sql_injection.py
        odoo-bin -d safer_db --test-tags .test_unsafe_cr_execute
        """
        blacklisted_rec_ids = []
        blacklist = self.env['safer_code.blacklist'].sudo().search([]).mapped('email')
        if blacklist:
            email_field = self.env[self.model]._primary_email
            sql = """ SELECT id from %s WHERE LOWER(%s) = any (array[%s]) AND id in (%s)""" % \
                (self.env[self.model]._table, email_field, ', '.join("'" + rec + "'" for rec in blacklist),
                 ', '.join(str(res_id) for res_id in res_ids))
            self.env.cr.execute(sql)
            blacklisted_rec_ids = [rec[0] for rec in self.env.cr.fetchall()]
        return blacklisted_rec_ids


class AccountMove(models.Model):
    _inherit = "safer_code.account.move.line"

    # https://github.com/odoo/enterprise/commit/364deaa0a2732071f4197ca01f2902cc981d8883
    # Introduced in 16.0 !
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        """
        leak: safer_code/leaks/leak_1_sql_injection.py
        test: safer_code/tests/test_leak_1_sql_injection.py
        odoo-bin -d safer_db --test-tags .test_unsafe_query_order
        """
        # EXTENDS 'base'
        preferred_aml_ids = self.env.context.get('matching_amount_aml_ids')
        if preferred_aml_ids and fields and not order:
            query = super()._search(domain, offset=offset, limit=limit, order=order or self._order)
            placeholder_ids = ', '.join(str(x) for x in preferred_aml_ids)
            query.order = f""" "safer_code_account_move_line".id IN ({placeholder_ids}) DESC,{query.order.code}"""
            records = self.browse(query)

            # Note: copy pasted from models.search_read
            result = []
            if records:
                result = records.read(fields, **read_kwargs)

            if len(result) <= 1:
                return result

            # reorder read
            index = {vals['id']: vals for vals in result}
            return [index[record.id] for record in records if record.id in index]

        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
