# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    bales_number = fields.Integer(string='Bales Number')