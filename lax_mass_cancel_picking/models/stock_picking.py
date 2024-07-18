from odoo import models
import random


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_cancel(self):
        if self.picking_type_id.code == 'internal':
            if self.state in ['done', 'confirmed']:
                for move in self.move_lines:
                    pack_op = self.env['stock.move'].sudo().search(
                            [('picking_id', '=', move.picking_id.id), ('product_id', '=', move.product_id.id)])
                    move.set_quant_quantity(move, pack_op, move.picking_id.state)
        res = super(StockPicking, self).action_cancel()
        account_obj = self.env['account.move']
        for move in self.move_ids_without_package:
            entry_name = move.name + ' - ' + move.product_id.name
            entry_s_name = move.name
            entry_names = [entry_name, entry_s_name]
            move_ids = account_obj.search([('ref', 'in', entry_names), ('state', '=', 'posted')])
            if move_ids:
                move_ids.sudo().button_draft()
                move_ids.sudo().button_cancel()
        return res

    def action_set_draft(self):
        move_obj = self.env['stock.move']
        for pick in self:
            ids2 = [move.id for move in pick.move_lines]
            moves = move_obj.browse(ids2)
            moves.sudo().action_draft()
            for move in moves:
                for m_line in move.move_line_ids:
                    m_line.unlink()
        return True


class stock_move(models.Model):
    _inherit = 'stock.move'

    def unlink_serial_number(self):
        if self.picking_type_id and self.picking_type_id.code == 'incoming':
            for line in self.move_line_ids:
                if line.lot_id:
                    line.lot_id.name = line.lot_id.name + '- Cancel - ' + str(random.randint(0, 99999))

    def action_draft(self):
        res = self.write({'state': 'draft'})
        return res

    def dev_set_quantity(self, move_qty, stock_move):
        quant_pool = self.env['stock.quant']
        product = stock_move.product_id
        if stock_move.product_id.tracking == 'none':
            out_qaunt = quant_pool.sudo().search(
                [('product_id', '=', product.id), ('location_id', '=', stock_move.location_id.id)])
            if not out_qaunt:
                out_qaunt = quant_pool.sudo().create({
                    'product_id': product and product.id or False,
                    'location_id': stock_move.location_id and stock_move.location_id.id or False,
                    'quantity': 0,
                    'product_uom_id': stock_move.product_uom and stock_move.product_uom.id or False,
                })
            if out_qaunt:
                out_qaunt[0].quantity = out_qaunt[0].quantity + move_qty
                if out_qaunt[0].quantity == 0:
                        out_qaunt[0].unlink()
            out_qaunt = quant_pool.sudo().search(
                [('product_id', '=', product.id), ('location_id', '=', stock_move.location_dest_id.id)])
            if not out_qaunt:
                out_qaunt = quant_pool.sudo().create({
                    'product_id': product and product.id or False,
                    'location_id': stock_move.location_id and stock_move.location_id.id or False,
                    'quantity': 0,
                    'product_uom_id': stock_move.product_uom and stock_move.product_uom.id or False,
                })
            if out_qaunt:
                out_qaunt[0].quantity = out_qaunt[0].quantity - move_qty
                if out_qaunt[0].quantity == 0:
                        out_qaunt[0].unlink()
        else:
            for line in stock_move.move_line_ids:
                out_qaunt = quant_pool.sudo().search(
                    [('product_id', '=', product.id), ('location_id', '=', stock_move.location_id.id), ('lot_id', '=', line.lot_id.id)])
                if not out_qaunt:
                    out_qaunt = quant_pool.sudo().create({
                        'product_id': product and product.id or False,
                        'location_id': stock_move.location_id and stock_move.location_id.id or False,
                        'quantity': 0,
                        'product_uom_id': stock_move.product_uom and stock_move.product_uom.id or False,
                        'lot_id': line.lot_id and line.lot_id.id or False,
                    })
                if out_qaunt:
                    out_qaunt[0].quantity = out_qaunt[0].quantity + line.qty_done
                    if out_qaunt[0].quantity == 0:
                        out_qaunt[0].unlink()
                out_qaunt = quant_pool.sudo().search(
                    [('product_id', '=', product.id), ('location_id', '=', stock_move.location_dest_id.id), ('lot_id', '=', line.lot_id.id)])
                if not out_qaunt:
                    out_qaunt = quant_pool.sudo().create({
                        'product_id': product and product.id or False,
                        'location_id': stock_move.location_id and stock_move.location_id.id or False,
                        'quantity': 0,
                        'product_uom_id': stock_move.product_uom and stock_move.product_uom.id or False,
                        'lot_id': line.lot_id and line.lot_id.id or False,
                    })
                if out_qaunt:
                    out_qaunt[0].quantity = out_qaunt[0].quantity - line.qty_done
                    if out_qaunt[0].quantity == 0:
                        out_qaunt[0].unlink()

    def set_quant_quantity(self, stock_move, pack_operation_ids, pic_state):
        for pack_operation_id in pack_operation_ids:
            move_qty = stock_move.product_uom_qty
            if stock_move.quantity_done:
                move_qty = stock_move.quantity_done
            if stock_move.quantity_done:
                if stock_move.sale_line_id:
                    if stock_move.sale_line_id.qty_delivered >= move_qty:
                        stock_move.sale_line_id.qty_delivered = stock_move.sale_line_id.qty_delivered - move_qty
                # if stock_move.purchase_line_id:
                #     if stock_move.purchase_line_id.qty_received >= move_qty:
                #         stock_move.purchase_line_id.qty_received = stock_move.purchase_line_id.qty_received - move_qty
                if stock_move.product_id.type == 'product':
                    self.dev_set_quantity(move_qty, stock_move)
        return True

    def unlink_stock_valuation_layer(self, move_id):
        val_line_ids = self.env['stock.valuation.layer'].sudo().search([('stock_move_id', '=', move_id.id)])
        for line in val_line_ids:
            line.unlink()

    def _action_cancel(self):
        for move in self:
            pic_state = move.picking_id.state
            if move.picking_id.state != 'done':
                move._do_unreserve()
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if all(state in ('done', 'cancel') for state in siblings_states):
                move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
            if move.picking_id.state == 'done' or 'confirmed' and move.picking_id.picking_type_id.code in ['incoming', 'outgoing']:
                pack_op = self.env['stock.move'].sudo().search(
                    [('picking_id', '=', move.picking_id.id), ('product_id', '=', move.product_id.id)])
                self.set_quant_quantity(move, pack_op, pic_state)
            self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
            self.unlink_stock_valuation_layer(move)
            move.unlink_serial_number()
        return True


class stock_move_line(models.Model):
    _inherit = "stock.move.line"

    def unlink(self):
        return super(stock_move_line, self).unlink()
