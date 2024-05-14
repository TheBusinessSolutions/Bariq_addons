from odoo import fields, models


class ProductProduct(models.Model):
    """ Make some of the product fields as storable to database"""
    _inherit = 'product.product'

    outgoing_qty = fields.Float(string="Outgoing quantity",
                                help="Quantity selling", readonly=True,
                                store=True)
    incoming_qty = fields.Float(string="Incoming quantity",
                                help="Quantity buying", readonly=True,
                                store=True)
    free_qty = fields.Float(string="Free quantity",
                            help="Balance quantity", readonly=True,
                            store=True)
    qty_available = fields.Float(string='Quantity available',
                                 help='Available quantity',
                                 readonly=True, store=True)
