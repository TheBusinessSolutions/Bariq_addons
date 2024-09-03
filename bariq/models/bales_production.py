# Step 1: Add the "received_bales_number" Field to mrp.production

from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_bales_number = fields.Integer(string="Production Bales Number")

# Step 3: Pass "production_bales_number" to stock.picking


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_bales_number = fields.Integer(string="Production Bales Number")

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        
        for production in self:
            if production.production_bales_number:
                # Find the related stock picking
                pickings = production.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
                for picking in pickings:
                    for move_line in picking.move_line_ids_without_package:
                        move_line.update({
                            'production_bales_number': production.production_bales_number,
                        })
        return res

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    production_bales_number = fields.Integer(string="Production Bales Number")