# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    diff_ship = fields.Boolean(string="Separate shipment per line")


    def _create_picking(self):
        if not self.diff_ship:
            return super(PurchaseOrder, self)._create_picking()
        else:
            for line in self.order_line:
                cntrs_number = int(self.cntrs_number)  # Retrieve cntrs_number from the order

                if cntrs_number <= 0:
                    raise ValueError("The CNTRs number must be greater than 0.")

                qty_per_picking = line.product_qty / cntrs_number  # Calculate quantity per picking

                for count in range(cntrs_number):
                    if line.product_id.type in ['product', 'consu']:
                        res = self._prepare_picking()
                        picking = self.env['stock.picking'].create(res)
                        move_vals = line._prepare_stock_moves(picking)
                        # Update the quantity of the move to the calculated quantity per picking
                        for move_val in move_vals:
                            move_val['product_uom_qty'] = qty_per_picking

                        moves = self.env['stock.move'].create(move_vals)
                        moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                        moves._action_assign()

                        picking.message_post_with_view('mail.message_origin_link', values={'self': picking, 'origin': self}, subtype_id=self.env.ref('mail.mt_note').id)