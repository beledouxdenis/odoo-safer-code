# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
This leak is not about any python code, but
- a reflected XSS in a Qweb template: `safer_code/views/website_forum_profile.xml` in particular `user_profile_sub_nav`
  - test: safer_code/tests/test_leak_6_xss.py
    odoo-bin -d safer_db --test-tags .test_unsafe_reflected_xss_forum
- a stored XSS in a Javascript widget: `safer_code/static/src/js/dialog_contact.js` in particular `formatSelection`
  - test: safer_code/tests/test_leak_6_xss.py
    odoo-bin -d safer_db --test-tags .test_unsafe_stored_xss
"""
