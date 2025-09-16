# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Task(models.Model):
    _name = "safer_code.task"
    _description = "Task"

    active = fields.Boolean(default=True)
    project_id = fields.Many2one('safer_code.project', string='Project')
    name = fields.Char(string='Title', required=True)
    description = fields.Html(string='Description')
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_email = fields.Char(
        compute='_compute_partner_email', inverse='_inverse_partner_email',
        string='Email', readonly=False, store=True, copy=False
    )
    user_ids = fields.Many2many(
        'res.users', relation='safer_code_task_user_rel', column1='task_id', column2='user_id', string='Assignees',
        context={'active_test': False}
    )

    @api.depends('partner_id.email')
    def _compute_partner_email(self):
        for task in self:
            if task.partner_id.email != task.partner_email:
                task.partner_email = task.partner_id.email

    def _inverse_partner_email(self):
        for task in self:
            if task.partner_id and task.partner_email != task.partner_id.email:
                task.partner_id.email = task.partner_email
