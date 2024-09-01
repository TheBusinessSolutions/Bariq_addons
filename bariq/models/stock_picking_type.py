from odoo import models, fields, api, exceptions

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    material_transfers = fields.Boolean(string='Material Transfer', default=False)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    weight_id = fields.Many2one('stock.weight', string='Weight Type')
    weight_1 = fields.Float(string="Weight")
    weight_2 = fields.Float(string="Weight")
    material_transfer_r = fields.Boolean(string='Material Transfer', compute='_compute_material_transfer', store=True)

    @api.depends('picking_type_id.material_transfers')
    def _compute_material_transfer(self):
        for record in self:
            record.material_transfer_r = record.picking_type_id.material_transfers

    @api.onchange('weight_1')
    def _onchange_weight_1(self):
        if self.weight_1:
            for move in self.move_ids_without_package:
                move.quantity_done = self.weight_1

     @api.onchange('weight_2')
    def _onchange_weight_1(self):
        if self.weight_2:
            for move in self.move_ids_without_package:
                move.quantity_done = self.weight_2


    def get_weight_1(self):
        if not self.weight_id:
            raise exceptions.UserError("Weight configuration is missing. Please ensure that a valid Weight ID is set.")
        try:
            import socket
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.weight_id.ip_addr, int(self.weight_id.port)))

            response = client.recv(1024)
            response = response.decode("utf-8")

            if not response.isdigit():
                raise exceptions.UserError("Invalid Return Response %s" % response)

            try:
                self.weight_1 = float(response)
            except ValueError:
                self.weight_1 = 0.0

            client.close()

        except Exception as e:
            raise exceptions.UserError("We Can't Process Request: (%s)" % e)
