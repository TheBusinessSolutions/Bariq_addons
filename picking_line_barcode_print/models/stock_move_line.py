# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    
    def action_print_line_barcode(self):
        # data = {'product_barcode': self.product_id.barcode if self.product_id else False, 'lot_barcode': self.lot_id.name if self.lot_id else False}
        # return self.env.ref('picking_line_barcode_print.action_report_barcode').report_action(self, data=data)

        return self.env.ref('picking_line_barcode_print.action_report_barcode').report_action(self)