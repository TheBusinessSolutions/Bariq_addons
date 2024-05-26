# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    driver_name    = fields.Char(string="Driver Name")
    driver_license = fields.Char(string="Driver License")
    truck_number   = fields.Char(string="Truck Number")
    trailer_number = fields.Char(string="Trailer Number")

    dawar_ticket = fields.Char(string="DAWAR Ticket")
    weight_1 = fields.Float(string="Weight 1")
    weight_2 = fields.Float(string="Weight 2")
    rejected = fields.Float(string="Rejected (%)")
    weight_ticket_number = fields.Char(string="Weight Ticket Number")
