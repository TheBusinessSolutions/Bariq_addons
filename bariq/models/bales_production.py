from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_bales_number = fields.Integer(string="Production Bales Number")

    def button_mark_done(self):
        # Call the original button_mark_done() method
        res = super(MrpProduction, self).button_mark_done()
        
        # Iterate over production orders
        for production in self:
            if production.production_bales_number:
                # Find the related stock picking (transfers)
                pickings = production.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
                
                for picking in pickings:
                    # Update the stock move with the bales number
                    for move in picking.move_ids_without_package:
                        move.update({
                            'production_bales_number': production.production_bales_number,
                        })
        return res