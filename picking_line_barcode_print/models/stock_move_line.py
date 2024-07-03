# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    
    def action_print_line_barcode(self):
        return self.env.ref('picking_line_barcode_print.action_report_barcode').report_action(self)