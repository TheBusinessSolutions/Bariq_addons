# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockMove(models.Model):
    _inherit = 'stock.move'


    bales_number = fields.Integer(string="Bales", compute='compute_bales_number')
    bariq_lot_id = fields.Char(string="Bariq Lot ID")
    production_bales_number = fields.Integer(string="Production Bales Number")
    scanned_bale_ids = fields.Many2many('stock.picking.bale', string='Scanned Bales')

    @api.depends('picking_id.stock_picking_bale_ids')
    @api.depends('picking_id.stock_picking_bale_ids')
    def compute_bales_number(self):
        for record in self:
            if record.picking_id.picking_type_code in ['incoming']:

                if record.purchase_line_id and record.purchase_line_id.order_id.diff_ship and record.purchase_line_id.order_id.imported_order and int(record.purchase_line_id.order_id.cntrs_number) > 0:
                    record.bales_number = record.purchase_line_id.bales_number / int(record.purchase_line_id.order_id.cntrs_number)
                else:
                    record.bales_number = record.purchase_line_id.bales_number

            elif record.picking_id.picking_type_code in ['outgoing', 'internal']:
                record.bales_number = len(record.picking_id.stock_picking_bale_ids.filtered(lambda bale: bale.product_id.id == record.product_id.id).ids)

            else:
                record.bales_number = 0
            