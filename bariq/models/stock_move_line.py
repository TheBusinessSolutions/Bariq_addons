# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    
    bales_number = fields.Integer(string="Bales", size=2, related='move_id.bales_number')
    bariq_lot_id = fields.Char(string="Bariq Lot ID")
    is_dawar_picking = fields.Boolean(related='picking_id.is_dawar_picking')
    scanned_bale_ids = fields.Many2many('stock.picking.bale', string='Scanned Bales')