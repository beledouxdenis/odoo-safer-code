# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class WebsiteForum(http.Controller):
    @http.route(['/safer_code/profile/user/<int:user_id>'], type='http', auth='public', website=True, sitemap=False)
    def view_user_profile(self, user_id, **post):
        values = {}
        return request.render("safer_code.user_profile_main", values)
