# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Safer Code',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Actual examples how hackers broke Odoo\'s security.',
    'description': """
This module contains examples of code hackers exploited
to obtain data or access they were not supposed to.
    """,
    'depends': [
        'contacts',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/safer_code_security.xml',
        'views/account_move.xml',
        'views/res_partner_views.xml',
        'views/templates.xml',
        'views/website_forum_profile.xml',
    ],
    'demo': [
        'data/leak_1_sql_injection_demo.xml',
        'data/leak_2_unsafe_sudo_demo.xml',
        'data/leak_3_master_the_rules_demo.xml',
        'data/leak_4_guard_password_and_tokens_fiercely_demo.xml',
        'data/leak_6_xss_demo.xml',
        'data/leak_7_open_with_care_demo.xml',
        'data/leak_8_eval_is_evil_demo.xml',
        'data/leak_9_dangerous_objects.xml',
        'data/leak_10_unsafe_getattr_setattr_demo.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'safer_code/static/src/js/*',
            'safer_code/static/src/xml/*',
        ],
        'web.assets_tests': [
            'safer_code/static/tests/tours/*',
        ],
    },
    'post_init_hook': '_post_init_hook',
    'author': 'Odoo S.A.',
}
