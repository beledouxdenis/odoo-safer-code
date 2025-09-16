# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import Controller, request, route


class SeaSurf(Controller):

    @route(['/safer_code/set-company-name'], type='http', auth='user', website=True)
    def set_company_name(self, name=None):
        """
            test: safer_code/tests/test_leak_5_sea_surf.py
            odoo-bin -d safer_db --test-tags .test_unsafe_route_get_method
        """
        values = {}
        if name:
            request.env['res.company'].browse(request.env.company.id).name = name
            values['renamed'] = True
        values['name'] = request.env.company.name
        return request.render("safer_code.set_company_name", values)
