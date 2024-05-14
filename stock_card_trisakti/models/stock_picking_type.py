from odoo import fields, models


class StockPicking(models.Model):
    """ Adding field and make it storable in the database"""
    _inherit = "stock.picking.type"

    display_name = fields.Char(string="Display name",
                               help='Name which is to display',
                               readonly=False, store=True)
