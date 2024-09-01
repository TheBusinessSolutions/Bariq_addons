# -*- coding: utf-8 -*-
from odoo import models, fields, api

# Step 1: Add the "received_bales_number" Field to mrp.production
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    received_bales_number = fields.Integer(string="Received Bales Number")

    # Step 3: Pass "received_bales_number" to stock.picking
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        
        for production in self:
            if production.received_bales_number:
                # Find the related stock picking
                pickings = production.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
                for picking in pickings:
                    for move_line in picking.move_ids_without_package:
                        move_line.update({
                            'received_bales_number': production.received_bales_number,
                        })
        return res


# Update the StockMove model to use the received_bales_number field
class StockMove(models.Model):
    _inherit = 'stock.move'

    bales_number = fields.Integer(string="Bales", compute='compute_bales_number')
    bariq_lot_id = fields.Char(string="Bariq Lot ID")

    def compute_bales_number(self):
        for record in self:
            # If received_bales_number is set, use it
            if record.move_ids_without_package and record.move_ids_without_package[0].received_bales_number:
                record.bales_number = record.move_ids_without_package[0].received_bales_number
            # Otherwise, use the existing logic
            elif record.purchase_line_id and record.purchase_line_id.order_id.diff_ship and record.purchase_line_id.order_id.imported_order and int(record.purchase_line_id.order_id.cntrs_number) > 0:
                record.bales_number = record.purchase_line_id.bales_number / int(record.purchase_line_id.order_id.cntrs_number)
            else:
                record.bales_number = record.purchase_line_id.bales_number


# Ensure that the StockMoveLine model has the received_bales_number field
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    received_bales_number = fields.Integer(string="Received Bales Number")
