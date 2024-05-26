# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    driver_name    = fields.Char(string="Driver Name")
    driver_license = fields.Char(string="Driver License")
    truck_number   = fields.Char(string="Truck Number")
    trailer_number = fields.Char(string="Trailer Number")