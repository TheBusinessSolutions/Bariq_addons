# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    material_transfers = fields.Boolean(string='Material Transfer', default=False)
