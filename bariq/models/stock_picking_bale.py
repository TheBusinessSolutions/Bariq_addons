# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class StockPickingBale(models.Model):
    _name = 'stock.picking.bale'


    sequence      = fields.Char(string='Sequence')
    product_id    = fields.Many2one('product.product' , string="Product")
    location_id   = fields.Many2one('stock.location'  , string="Location")
    picking_id    = fields.Many2one('stock.picking'   , string="Picking")
    state         = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')], default='draft')


    def action_print_line_barcode(self):
        return self.env.ref('bariq.action_report_bale_barcode').report_action(self)
    


    def action_print_bales_in_range(self):
        picking = self.picking_id  # Assuming the method is called from stock.move.line
        bales = self.env['stock.picking.bale'].search([('picking_id', '=', picking.id)])
        return self.env.ref('bariq.action_report_bale_barcode').report_action(bales)
    
    def action_print_all_bales_barcode(self):
        bales = self.env['stock.picking.bale'].search([('picking_id', '=', self.id)])
        if not bales:
            raise UserError(_("No bales found for this picking."))
        return self.env.ref('bariq.action_report_bale_barcode').report_action(bales)