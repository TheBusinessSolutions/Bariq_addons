from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    # One2many relation to store bales
    #this is the bales list which will be generated in the picking
    bales_ids = fields.One2many('stock.picking.bale', 'picking_id', string="Bales Ref")
    
    #get the bales number from the PO
    bales_number = fields.Integer(string="Bales Number", compute='_compute_bales_number', store=True)

    def _compute_bales_number(self):
        for picking in self:
            # bales_total = sum(move.bales_number for move in picking.move_ids_without_package)
            bales_total = sum(move.bales_number for move in picking.move_line_nosuggest_ids)
            picking.bales_number = bales_total
        # Button to generate the bales based on the bales_number field
    def action_generate_bales(self):
        self.ensure_one()
        if self.bales_number > 0:
            # Clear existing bales if necessary
            self.bales_ids.unlink()
            
            # Create new bales
            bales_list = []
            for i in range(1, self.bales_number + 1):
                bale_name = str(i)
                bales_list.append((0, 0, {
                    'name': bale_name,
                    'picking_id': self.id,
                }))
            self.bales_ids = bales_list
            
            # Return a UserError to show a popup message
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Bales Generated',
                    'message': f'{len(bales_list)} bales have been successfully created.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Bales Created',
                    'message': 'The number of bales is zero or less, no bales created.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
