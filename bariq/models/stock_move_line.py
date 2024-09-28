# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    
    bales_number = fields.Integer(string="Bales", size=2, related='move_id.bales_number')
    bariq_lot_id = fields.Char(string="Bariq Lot ID")
    is_dawar_picking = fields.Boolean(related='picking_id.is_dawar_picking')


    # def compute_bales_number(self):
    #     for record in self:
    #         if record.picking_id.picking_type_code in ['incoming']:
    #             record.bales_number = record.move_id.bales_number
    #         elif record.picking_id.picking_type_code in ['outgoing', 'internal']:
    #             record.bales_number = len(record.picking_id.stock_picking_bale_ids.filtered(lambda bale: bale.product_id.id == record.product_id.id).ids)
    #         else:
    #             record.bales_number = 0