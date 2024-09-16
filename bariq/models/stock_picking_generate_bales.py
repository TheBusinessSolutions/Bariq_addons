from odoo import models, fields, api

# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
    
#     # One2many relation to store bales
#     bales_ids = fields.One2many('stock.picking.bale', 'picking_id', string="Bales Ref")
    
#     # Button to generate the bales based on the bales_number field
#     def action_generate_bales(self):
#         self.ensure_one()
#         if not self.bales_ids:  # Ensure we don't duplicate the bales
#             bales_list = []
#             for i in range(1, self.bales_number + 1):
#                 bales_list.append((0, 0, {
#                     'name': 'BL' + str(i),
#                 }))
#             self.bales_ids = bales_list
#         return True

# class Bale(models.Model):
#     _name = 'stock.picking.bale'
#     _description = 'Bale'

#     name = fields.Char(string="Bale Number", required=True)
#     picking_id = fields.Many2one('stock.picking', string="Picking")
