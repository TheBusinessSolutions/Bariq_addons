from odoo import models


class StockLinePrintBarcode(models.Model):
    _inherit = "stock.move"
    _inherit = 'stock.move.line'
    bales_number = fields.Integer(string="Bales", size=2, related='move_id.purchase_line_id.bales_number')
    is_dawar_picking = fields.Boolean(related='picking_id.is_dawar_picking')

    def action_open_label_layout(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'product.action_open_label_layout')
        action['context'] = {
            'default_product_ids': [self.product_id.id],
            'default_custom_quantity': self.quantity_done or 1,
        }
        return action
