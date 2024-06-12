# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockMove(models.Model):
    _inherit = 'stock.move'


    bales_number = fields.Integer(string="Bales", size=2, related='purchase_line_id.bales_number')