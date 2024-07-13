# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockMove(models.Model):
    _inherit = 'stock.move'


    bales_number = fields.Integer(string="Bales", compute='compute_bales_number')
    bariq_lot_id = fields.Char(string="Bariq Lot ID")


    def compute_bales_number(self):
        for record in self:
            if record.purchase_line_id and record.purchase_line_id.order_id.diff_ship and record.purchase_line_id.order_id.imported_order and int(record.purchase_line_id.order_id.cntrs_number) > 0:
                record.bales_number = record.purchase_line_id.bales_number / int(record.purchase_line_id.order_id.cntrs_number)
            else:
                record.bales_number = record.purchase_line_id.bales_number