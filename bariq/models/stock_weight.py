# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockWeight(models.Model):
    _name = 'stock.weight'


    name      = fields.Char(string="Name", required=True)
    code      = fields.Char(string="Code", required=True)
    ip_addr   = fields.Char(string="IP Address", required=True)
    port      = fields.Char(string="Port Number", required=True)
    user_ids  = fields.Many2many('res.users', string="Access Users", required=True)
    is_manual = fields.Boolean(string="Manual")