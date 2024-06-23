# -*- coding: utf-8 -*-


from odoo import api, fields, models


class SrPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    diff_ship = fields.Boolean(string="Separate shipment per line")

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        if not self.diff_ship:
            return super(SrPurchaseOrder, self)._create_picking()
        else:
            for line in self.order_line:
                if any(ptype in ['product', 'consu'] for ptype in line.order_id.order_line.mapped('product_id.type')):
                    res = line.order_id._prepare_picking()
                    picking = StockPicking.create(res)
                    moves = line._create_stock_moves(picking)
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in moves:  # Removed the sorting by date_expected
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': picking, 'origin': line.order_id},
                                                   subtype_id=self.env.ref('mail.mt_note').id)
        return True
