# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models

"""
This leak is not about any python code, but
- a reflected XSS in a Qweb template: `safer_code/views/website_forum_profile.xml` in particular `user_profile_sub_nav`
  - test: safer_code/tests/test_leak_6_xss.py
    odoo-bin -d safer_db --test-tags .test_unsafe_reflected_xss_forum
- a stored XSS in a Javascript widget: `safer_code/static/src/js/dialog_contact.js` in particular `formatSelection`
  - test: safer_code/tests/test_leak_6_xss.py
    odoo-bin -d safer_db --test-tags .test_unsafe_stored_xss
"""


# Revert https://github.com/odoo/odoo/commit/d0ff93afed55fdab4dedfd0d5e09e727e38cd089
class IrQWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    def _post_processing_att(self, tagName, atts):
        origin_href = atts.get('href')
        atts = super()._post_processing_att(tagName, atts)
        if origin_href:
            atts['href'] = origin_href
        return atts
