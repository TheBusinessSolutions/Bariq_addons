# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Alexander Ezquevo <alexander@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class Lot(models.Model):
    _inherit = 'stock.production.lot'

    unit_cost = fields.Float(string='Lot unit cost', default=0)


class MRP_production(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def action_produce(
            self, production_qty, production_mode,
            wiz=False):
        if wiz and wiz.lot_id and len(wiz.consume_lines) > 0:
            '''
            control = True
            for line in wiz.consume_lines:
                if not line.lot_id:
                    control = False
            if(control):
                self.calculateCost(wiz)
            '''
            self.calculateCost(wiz)
        super(MRP_production, self).action_produce(
            self.id, production_qty, production_mode, wiz)

    def get_price_unit(self, move):
        return move.price_unit

    @api.model
    def calculateCost(self, wiz):
        stock_quant_obj = self.env['stock.quant']
        stock_move_obj = self.env['stock.move']
        totalCost = 0.0
        for line in wiz.consume_lines:
            if line.lot_id:
                quants = stock_quant_obj.search([
                    ('product_id', '=', line.product_id.id,),
                    ('lot_id', '=', line.lot_id.id)])
                ids = []
                for q in quants:
                    ids.append(q.id)
                moves = stock_move_obj.search([
                    ('quant_ids', 'in', ids),
                    ('picking_id','!=', False)])
                amount = 0.0
                raw_qty = 0
                if len(moves) != 0:
                    for move in moves:
                        amount += self.get_price_unit(move) * move.product_qty
                        raw_qty += move.product_qty
                    unit_price = amount/raw_qty
                    totalCost += line.product_qty * unit_price
        if wiz.lot_id.unit_cost and wiz.lot_id.unit_cost != 0.0:
            initial_lots = stock_quant_obj.search([
                ('lot_id', '=', wiz.lot_id.id)])
            initial_totalCost = 0.0
            totalQty = 0.0
            for q in initial_lots:
                initial_totalCost += wiz.lot_id.unit_cost * q.qty
                totalQty += q.qty
            totalQty += wiz.product_qty
            totalCost = initial_totalCost + totalCost
            wiz.lot_id.unit_cost = totalCost/totalQty
        else:
            wiz.lot_id.unit_cost = totalCost/wiz.product_qty
