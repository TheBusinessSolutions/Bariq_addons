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
        # """ New method to print barcodes for all bales within the start and end sequence range found in stock.move.line. """

        # Get the current picking from the context (assuming this is called from a stock.picking)
        picking_id = self.env.context.get('picking_id')
        if not picking_id:
            raise UserError(_("No picking found in context."))

        # Get stock.move.line records for this picking
        picking = self.env['stock.picking'].browse(picking_id)
        move_lines = picking.move_line_ids

        # Get the start and end sequence numbers from stock.move.line
        start_sequence = min(move_lines.mapped('bale_sequence'))
        end_sequence = max(move_lines.mapped('bale_sequence'))

        if not start_sequence or not end_sequence:
            raise UserError(_("No bale sequence found in stock.move.line for this picking."))

        # Ensure the start sequence is less than or equal to the end sequence
        if start_sequence > end_sequence:
            raise UserError(_("Start sequence must be less than or equal to end sequence."))

        # Find all bales within the sequence range
        bales_in_range = self.search([('sequence', '>=', start_sequence), ('sequence', '<=', end_sequence)])

        if not bales_in_range:
            raise UserError(_("No bales found in the specified range."))

        # Return the report action for printing all the bales in the range
        return self.env.ref('bariq.action_report_bale_barcode').report_action(bales_in_range)