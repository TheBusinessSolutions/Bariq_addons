from odoo import models, fields

class StockLinePrintBarcode(models.Model):
    _inherit = ['stock.move', 'stock.move.line']

    bales_number = fields.Integer(string="Bales", related='move_id.purchase_line_id.bales_number')
    is_dawar_picking = fields.Boolean(related='picking_id.is_dawar_picking')

    def action_open_label_layout(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'product.action_open_label_layout')
        action['context'] = {
            'default_product_ids': [self.product_id.id],
            'default_custom_quantity': self.bales_number or 1,  # Updated line
        }
        return action
