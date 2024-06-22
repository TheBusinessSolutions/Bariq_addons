# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    bales_number = fields.Integer(string="Bales", size=2, related='move_id.purchase_line_id.bales_number')
    is_dawar_picking = fields.Boolean(related='picking_id.is_dawar_picking')