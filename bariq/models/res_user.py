from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    set_rejection_rate = fields.Boolean(string="Set Rejection Rate", default=False)
