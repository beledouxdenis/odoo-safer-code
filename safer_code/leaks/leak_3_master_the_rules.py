# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
This leak is not about any python code, but a lack of restriction in the
ACL (`ir.model.access`)
and
record rules (`ir.rule`)
See files
- `safer_code/security/ir.model.access.csv`
- `safer_code/security/safer_code_security.xml`
regarding `mail.channel.partner`

test: safer_code/tests/test_leak_3_master_the_rules.py
odoo-bin -d safer_db --test-tags .test_unsafe_access_rights_channel_partner
"""
