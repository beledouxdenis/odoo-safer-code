# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Project(models.Model):
    _name = "safer_code.project"
    _description = "Project"

    name = fields.Char(string='Name', required=True)
    collaborator_ids = fields.Many2many('res.users', string='Collaborators', copy=False)
