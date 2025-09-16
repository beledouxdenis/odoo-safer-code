# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = 'base'

    # https://github.com/odoo/odoo/blob/9ee022362a098359c78fd1cdb53287dab4d5b298/odoo/models.py#L548-L557
    @api.model
    def _field_add(self, name, field):
        """ Add the given ``field`` under the given ``name`` in the class """
        cls = type(self)
        # add field as an attribute and in cls._fields (for reflection)
        setattr(cls, name, field)
        field._toplevel = True
        field.__set_name__(cls, name)
        cls._fields[name] = field

    # Not a real example, just to make a point how far you can go with just getattr
    # Examples of security fixes: https://github.com/odoo/odoo/commit/a08b2bac0b2e8e3e560668302e58caea65ea7d28
    @api.model
    def _get_field(self, name):
        return getattr(self, name, None)


# https://github.com/odoo/enterprise/commit/cc61146e76946c53ec8c0283ade9904688e02490
class BrowsableObject:
    def __init__(self, dict):
        self.dict = dict

    def __getattr__(self, attr):
        value = None
        if attr in self.dict:
            value = self.dict.__getitem__(attr)
        return value


class HrPayslip(models.Model):
    _inherit = 'safer_code.hr.payslip'

    def _get_localdict(self):
        return {
            'categories': BrowsableObject({}),
        }
