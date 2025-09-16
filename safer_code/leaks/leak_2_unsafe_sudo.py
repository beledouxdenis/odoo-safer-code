# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import AccessError
from odoo.http import Controller, request, route


# https://github.com/odoo/odoo/commit/c3c0408471763ea90e9379a2d05fd2add820d57e#diff-37a05e08bc0d2d227fe7f446bc432c85ae5e89a4e9ebdc7a1a5915dd9a6bf71eR83
# --test-tags .test_unsafe_sudo_route_me
class Me(Controller):

    @route(['/me'], type='http', auth='user', website=True)
    def me(self, **post):
        """
        test: safer_code/tests/test_leak_2_unsafe_sudo.py
        odoo-bin -d safer_db --test-tags .test_unsafe_sudo_route_me
        """
        partner = request.env.user.partner_id
        if post:
            partner.sudo().write(post)
            return request.redirect('/me')
        values = {
            'partner': partner,
        }
        return request.render("safer_code.me", values)


# https://www.slideshare.net/OlivierDony/how-to-break-odoos-security-odoo-experience-2018
# Slide 23
# --test-tags .test_unsafe_sudo_domain_injection
class MyMessage(Controller):

    @route(['/my-last-messages'], type='jsonrpc', auth='user', website=True)
    def my_last_messages(self, domain=None):
        """
        test: safer_code/tests/test_leak_2_unsafe_sudo.py
        odoo-bin -d safer_db --test-tags .test_unsafe_sudo_domain_injection
        """
        force_domain = [('model', '=', 'res.partner'), ('res_id', '=', request.env.user.partner_id.id)]
        domain = (domain or []) + force_domain
        return request.env['mail.message'].sudo().search_read(domain, ['subject', 'body'], limit=10)


# https://github.com/odoo/odoo/commit/e50bc120020d606962c1d9b687e53b1bdb34c048#diff-dcdc6e8a2e65aff0582c53d72c3890c1b56725a8b9fcf7abbb0378097b5999afR43-R44
# --test-tags .test_unsafe_sudo_writable_whitelist
class Task(models.Model):
    """
        test: safer_code/tests/test_leak_2_unsafe_sudo.py
        odoo-bin -d safer_db --test-tags .test_unsafe_sudo_writable_whitelist
    """
    _inherit = 'safer_code.task'

    PROJECT_TASK_WRITABLE_FIELDS = {
        'name',
        'description',
        'partner_id',
        'partner_email',
    }

    def write(self, vals):

        portal_can_write = False
        if self.env.user.has_group('base.group_portal') and not self.env.su:
            unauthorized_fields = set(vals.keys()) - (self.PROJECT_TASK_WRITABLE_FIELDS)
            if unauthorized_fields:
                raise AccessError(_('You cannot write on %s fields in task.', ', '.join(unauthorized_fields)))
            self.check_access('write')
            portal_can_write = True

        tasks = self

        if portal_can_write:
            tasks = tasks.sudo()

        result = super(Task, tasks).write(vals)
        return result


# https://github.com/odoo/enterprise/commit/8e258c72067c9c0d93f9c7c267dc1402d163030e
class SignTemplate(models.Model):
    """
        test: safer_code/tests/test_leak_2_unsafe_sudo.py
        odoo-bin -d safer_db --test-tags .test_unsafe_related_sudo
    """
    _inherit = 'safer_code.sign.template'

    attachment_id = fields.Many2one('ir.attachment', string="Attachment", required=True, ondelete='cascade')
    name = fields.Char(related='attachment_id.name', readonly=False)
    datas = fields.Binary(related='attachment_id.datas', readonly=False)
