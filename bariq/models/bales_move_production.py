# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    bales_number = fields.Integer(string="Bales", compute='_compute_bales_number', store=True)

    @api.depends('move_id.production_id.bales_number')
    def _compute_bales_number(self):
        for line in self:
            if line.move_id.production_id:
                line.bales_number = line.move_id.production_id.bales_number
            else:
                line.bales_number = 0
