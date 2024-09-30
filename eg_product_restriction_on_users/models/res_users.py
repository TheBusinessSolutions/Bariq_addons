from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    product_template_ids = fields.Many2many(comodel_name='product.template', string='Restrict Products')
